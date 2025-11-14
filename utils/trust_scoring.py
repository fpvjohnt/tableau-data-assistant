"""
Trust Scoring for Tableau Dashboards
Generates field-level trust scores based on data quality, freshness, and validation history
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import json
import sqlite3

from config.settings import EXPORTS_DIR


@dataclass
class TrustScore:
    """Trust score for a single field/column"""
    field_name: str
    trust_score: float  # 0-100
    completeness_score: float  # 0-100
    validity_score: float  # 0-100
    anomaly_score: float  # 0-100
    freshness_score: float  # 0-100
    sample_size: int
    last_validated: datetime
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def get_grade(self) -> str:
        """Get letter grade for trust score"""
        if self.trust_score >= 95:
            return 'A+'
        elif self.trust_score >= 90:
            return 'A'
        elif self.trust_score >= 85:
            return 'B+'
        elif self.trust_score >= 80:
            return 'B'
        elif self.trust_score >= 75:
            return 'C+'
        elif self.trust_score >= 70:
            return 'C'
        elif self.trust_score >= 60:
            return 'D'
        else:
            return 'F'

    def get_color(self) -> str:
        """Get color code for Tableau visualization"""
        if self.trust_score >= 90:
            return '#10a37f'  # Green
        elif self.trust_score >= 75:
            return '#f39c12'  # Yellow
        elif self.trust_score >= 60:
            return '#e67e22'  # Orange
        else:
            return '#e74c3c'  # Red

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'field_name': self.field_name,
            'trust_score': round(self.trust_score, 2),
            'completeness_score': round(self.completeness_score, 2),
            'validity_score': round(self.validity_score, 2),
            'anomaly_score': round(self.anomaly_score, 2),
            'freshness_score': round(self.freshness_score, 2),
            'grade': self.get_grade(),
            'color': self.get_color(),
            'sample_size': self.sample_size,
            'last_validated': self.last_validated.isoformat(),
            'reasons': self.reasons,
            'warnings': self.warnings
        }


@dataclass
class DatasetTrustReport:
    """Trust report for entire dataset"""
    dataset_name: str
    overall_trust_score: float
    field_scores: List[TrustScore]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to Tableau-ready DataFrame"""
        records = []
        for score in self.field_scores:
            record = {
                'Dataset': self.dataset_name,
                'Field_Name': score.field_name,
                'Trust_Score': round(score.trust_score, 2),
                'Grade': score.get_grade(),
                'Color': score.get_color(),
                'Completeness': round(score.completeness_score, 2),
                'Validity': round(score.validity_score, 2),
                'Anomaly_Free': round(score.anomaly_score, 2),
                'Freshness': round(score.freshness_score, 2),
                'Sample_Size': score.sample_size,
                'Last_Validated': score.last_validated,
                'Warnings': '; '.join(score.warnings) if score.warnings else 'None',
                'Reasons': '; '.join(score.reasons) if score.reasons else 'Good quality'
            }
            records.append(record)

        return pd.DataFrame(records)


class TrustScoreCalculator:
    """Calculate trust scores for dataset fields"""

    # Weights for score components
    WEIGHTS = {
        'completeness': 0.30,
        'validity': 0.30,
        'anomaly': 0.25,
        'freshness': 0.15
    }

    def __init__(self, freshness_threshold_days: int = 7):
        """
        Initialize trust score calculator

        Args:
            freshness_threshold_days: Days before data is considered stale
        """
        self.freshness_threshold_days = freshness_threshold_days

    def calculate_dataset_trust(
        self,
        df: pd.DataFrame,
        validation_result: Optional[Any] = None,
        anomaly_report: Optional[Any] = None,
        date_column: Optional[str] = None,
        dataset_name: str = "dataset"
    ) -> DatasetTrustReport:
        """
        Calculate trust scores for all fields in dataset

        Args:
            df: DataFrame to analyze
            validation_result: Optional ValidationResult from validation module
            anomaly_report: Optional AnomalyReport from anomaly detection
            date_column: Optional date column for freshness calculation
            dataset_name: Name of dataset

        Returns:
            DatasetTrustReport with field-level trust scores
        """
        field_scores = []

        for col in df.columns:
            score = self._calculate_field_trust(
                df[col],
                col,
                validation_result,
                anomaly_report,
                date_column if col == date_column else None
            )
            field_scores.append(score)

        # Calculate overall dataset trust
        overall_trust = np.mean([s.trust_score for s in field_scores])

        return DatasetTrustReport(
            dataset_name=dataset_name,
            overall_trust_score=overall_trust,
            field_scores=field_scores,
            metadata={
                'total_fields': len(field_scores),
                'high_trust_fields': sum(1 for s in field_scores if s.trust_score >= 90),
                'medium_trust_fields': sum(1 for s in field_scores if 75 <= s.trust_score < 90),
                'low_trust_fields': sum(1 for s in field_scores if s.trust_score < 75)
            }
        )

    def _calculate_field_trust(
        self,
        series: pd.Series,
        field_name: str,
        validation_result: Optional[Any],
        anomaly_report: Optional[Any],
        date_column: Optional[str]
    ) -> TrustScore:
        """Calculate trust score for a single field"""
        # 1. Completeness Score (0-100)
        completeness_score = self._calculate_completeness_score(series)

        # 2. Validity Score (0-100)
        validity_score = self._calculate_validity_score(series, field_name, validation_result)

        # 3. Anomaly Score (0-100)
        anomaly_score = self._calculate_anomaly_score(series, field_name, anomaly_report)

        # 4. Freshness Score (0-100)
        freshness_score = self._calculate_freshness_score(series, date_column)

        # Calculate weighted trust score
        trust_score = (
            completeness_score * self.WEIGHTS['completeness'] +
            validity_score * self.WEIGHTS['validity'] +
            anomaly_score * self.WEIGHTS['anomaly'] +
            freshness_score * self.WEIGHTS['freshness']
        )

        # Generate reasons and warnings
        reasons, warnings = self._generate_reasons_and_warnings(
            completeness_score, validity_score, anomaly_score, freshness_score
        )

        return TrustScore(
            field_name=field_name,
            trust_score=trust_score,
            completeness_score=completeness_score,
            validity_score=validity_score,
            anomaly_score=anomaly_score,
            freshness_score=freshness_score,
            sample_size=len(series),
            last_validated=datetime.now(),
            reasons=reasons,
            warnings=warnings
        )

    def _calculate_completeness_score(self, series: pd.Series) -> float:
        """Calculate completeness score (higher = fewer nulls)"""
        if len(series) == 0:
            return 0.0

        completeness = (1 - series.isnull().sum() / len(series)) * 100
        return max(0.0, min(100.0, completeness))

    def _calculate_validity_score(
        self,
        series: pd.Series,
        field_name: str,
        validation_result: Optional[Any]
    ) -> float:
        """Calculate validity score based on validation results"""
        # Start with perfect score
        score = 100.0

        if validation_result is None:
            return score

        # Check for validation errors related to this field
        if hasattr(validation_result, 'errors'):
            field_errors = [
                e for e in validation_result.errors
                if e.get('column') == field_name or field_name in str(e)
            ]
            # Deduct points for errors (max 50 points deduction)
            score -= min(50.0, len(field_errors) * 10)

        # Check for warnings
        if hasattr(validation_result, 'warnings'):
            field_warnings = [
                w for w in validation_result.warnings
                if w.get('column') == field_name or field_name in str(w)
            ]
            # Deduct points for warnings (max 25 points deduction)
            score -= min(25.0, len(field_warnings) * 5)

        return max(0.0, score)

    def _calculate_anomaly_score(
        self,
        series: pd.Series,
        field_name: str,
        anomaly_report: Optional[Any]
    ) -> float:
        """Calculate anomaly score (higher = fewer anomalies)"""
        if anomaly_report is None or not pd.api.types.is_numeric_dtype(series):
            return 100.0  # Default to perfect if no anomaly detection

        if hasattr(anomaly_report, 'anomalies_by_column'):
            anomaly_count = anomaly_report.anomalies_by_column.get(field_name, 0)
            if len(series) > 0:
                anomaly_percentage = (anomaly_count / len(series)) * 100
                # Score decreases with more anomalies
                score = 100.0 - min(50.0, anomaly_percentage * 2)
                return max(0.0, score)

        return 100.0

    def _calculate_freshness_score(
        self,
        series: pd.Series,
        is_date_column: Optional[str]
    ) -> float:
        """Calculate freshness score based on recency of data"""
        if is_date_column is None:
            return 100.0  # Default to perfect if not a date column

        try:
            # Try to parse as datetime
            if not pd.api.types.is_datetime64_any_dtype(series):
                series = pd.to_datetime(series, errors='coerce')

            # Get most recent date
            max_date = series.max()
            if pd.isna(max_date):
                return 50.0  # Medium score if no valid dates

            # Calculate days since last update
            days_old = (datetime.now() - max_date).days

            # Score based on freshness
            if days_old <= 1:
                return 100.0
            elif days_old <= self.freshness_threshold_days:
                # Linear decay from 100 to 70 over threshold period
                return 100.0 - (days_old / self.freshness_threshold_days) * 30
            elif days_old <= 30:
                # Decay from 70 to 40 over next 23 days
                return 70.0 - ((days_old - self.freshness_threshold_days) / 23) * 30
            else:
                # Older than 30 days: 0-40 based on how old
                return max(0.0, 40.0 - min(40.0, (days_old - 30) / 30 * 40))

        except:
            return 100.0  # Default to perfect on error

    def _generate_reasons_and_warnings(
        self,
        completeness: float,
        validity: float,
        anomaly: float,
        freshness: float
    ) -> Tuple[List[str], List[str]]:
        """Generate human-readable reasons and warnings"""
        reasons = []
        warnings = []

        # Completeness
        if completeness >= 95:
            reasons.append("Excellent data completeness (e95%)")
        elif completeness >= 80:
            reasons.append("Good data completeness (e80%)")
        else:
            warnings.append(f"Low completeness ({completeness:.1f}%)")

        # Validity
        if validity >= 95:
            reasons.append("Passes all validation checks")
        elif validity >= 80:
            reasons.append("Minor validation warnings only")
        else:
            warnings.append("Has validation errors")

        # Anomalies
        if anomaly >= 95:
            reasons.append("No significant anomalies detected")
        elif anomaly >= 80:
            reasons.append("Few anomalies detected")
        else:
            warnings.append(f"High anomaly rate ({100 - anomaly:.1f}%)")

        # Freshness
        if freshness >= 95:
            reasons.append("Data is very fresh (d1 day old)")
        elif freshness >= 70:
            reasons.append("Data is reasonably fresh")
        elif freshness >= 40:
            warnings.append("Data is somewhat stale (>7 days)")
        else:
            warnings.append("Data is very stale (>30 days)")

        return reasons, warnings


class TrustScoreStore:
    """Persist trust scores to SQLite for historical tracking"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize trust score store

        Args:
            db_path: Path to SQLite database (default: exports/trust_scores.db)
        """
        if db_path is None:
            db_path = EXPORTS_DIR / "trust_scores.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trust_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                field_name TEXT NOT NULL,
                trust_score REAL NOT NULL,
                completeness_score REAL,
                validity_score REAL,
                anomaly_score REAL,
                freshness_score REAL,
                grade TEXT,
                color TEXT,
                sample_size INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reasons TEXT,
                warnings TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dataset_field
            ON trust_scores(dataset_name, field_name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON trust_scores(timestamp)
        """)

        conn.commit()
        conn.close()

    def save_report(self, report: DatasetTrustReport):
        """Save trust report to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for score in report.field_scores:
            cursor.execute("""
                INSERT INTO trust_scores (
                    dataset_name, field_name, trust_score,
                    completeness_score, validity_score, anomaly_score, freshness_score,
                    grade, color, sample_size, reasons, warnings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.dataset_name,
                score.field_name,
                score.trust_score,
                score.completeness_score,
                score.validity_score,
                score.anomaly_score,
                score.freshness_score,
                score.get_grade(),
                score.get_color(),
                score.sample_size,
                json.dumps(score.reasons),
                json.dumps(score.warnings)
            ))

        conn.commit()
        conn.close()

    def get_historical_scores(
        self,
        dataset_name: str,
        field_name: Optional[str] = None,
        days: int = 30
    ) -> pd.DataFrame:
        """
        Get historical trust scores

        Args:
            dataset_name: Dataset name
            field_name: Optional field name (None for all fields)
            days: Number of days of history

        Returns:
            DataFrame with historical scores
        """
        conn = sqlite3.connect(self.db_path)

        cutoff_date = datetime.now() - timedelta(days=days)

        if field_name:
            query = """
                SELECT * FROM trust_scores
                WHERE dataset_name = ? AND field_name = ?
                AND timestamp >= ?
                ORDER BY timestamp DESC
            """
            params = (dataset_name, field_name, cutoff_date)
        else:
            query = """
                SELECT * FROM trust_scores
                WHERE dataset_name = ?
                AND timestamp >= ?
                ORDER BY timestamp DESC
            """
            params = (dataset_name, cutoff_date)

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def get_latest_scores(self, dataset_name: str) -> pd.DataFrame:
        """Get most recent trust scores for dataset"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT t1.*
            FROM trust_scores t1
            INNER JOIN (
                SELECT field_name, MAX(timestamp) as max_timestamp
                FROM trust_scores
                WHERE dataset_name = ?
                GROUP BY field_name
            ) t2
            ON t1.field_name = t2.field_name
            AND t1.timestamp = t2.max_timestamp
            WHERE t1.dataset_name = ?
        """

        df = pd.read_sql_query(query, conn, params=(dataset_name, dataset_name))
        conn.close()

        return df


class TrustHeatmapGenerator:
    """Generate visual trust heatmaps for Tableau"""

    def __init__(self):
        """Initialize heatmap generator"""
        pass

    def generate_tableau_csv(
        self,
        report: DatasetTrustReport,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate CSV file for Tableau import

        Args:
            report: DatasetTrustReport
            output_path: Optional output path

        Returns:
            Path to generated CSV
        """
        if output_path is None:
            output_path = EXPORTS_DIR / f"trust_scores_{report.dataset_name}.csv"

        df = report.to_dataframe()
        df.to_csv(output_path, index=False)

        return output_path

    def generate_tooltip_text(self, score: TrustScore) -> str:
        """Generate Tableau tooltip text"""
        lines = [
            f"Trust Score: {score.trust_score:.1f}/100 ({score.get_grade()})",
            "",
            "Component Scores:",
            f"  Completeness: {score.completeness_score:.1f}/100",
            f"  Validity: {score.validity_score:.1f}/100",
            f"  Anomaly-Free: {score.anomaly_score:.1f}/100",
            f"  Freshness: {score.freshness_score:.1f}/100",
            ""
        ]

        if score.reasons:
            lines.append("✓ Strengths:")
            for reason in score.reasons:
                lines.append(f"  - {reason}")
            lines.append("")

        if score.warnings:
            lines.append("⚠ Warnings:")
            for warning in score.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)

    def create_trust_matrix(self, report: DatasetTrustReport) -> pd.DataFrame:
        """Create matrix format suitable for heatmap visualization"""
        df = report.to_dataframe()

        # Pivot to create matrix
        matrix = df.pivot_table(
            values=['Trust_Score', 'Completeness', 'Validity', 'Anomaly_Free', 'Freshness'],
            index='Field_Name',
            aggfunc='first'
        )

        return matrix


# Convenience functions
def calculate_trust_scores(
    df: pd.DataFrame,
    validation_result: Optional[Any] = None,
    anomaly_report: Optional[Any] = None,
    date_column: Optional[str] = None,
    dataset_name: str = "dataset"
) -> DatasetTrustReport:
    """
    One-line function to calculate trust scores

    Args:
        df: DataFrame to analyze
        validation_result: Optional validation result
        anomaly_report: Optional anomaly report
        date_column: Optional date column name
        dataset_name: Dataset name

    Returns:
        DatasetTrustReport with trust scores
    """
    calculator = TrustScoreCalculator()
    return calculator.calculate_dataset_trust(
        df, validation_result, anomaly_report, date_column, dataset_name
    )


def export_trust_scores_for_tableau(
    report: DatasetTrustReport,
    save_to_db: bool = True
) -> Path:
    """
    Export trust scores to Tableau-ready format

    Args:
        report: DatasetTrustReport
        save_to_db: Whether to save to SQLite database

    Returns:
        Path to exported CSV file
    """
    # Generate CSV
    generator = TrustHeatmapGenerator()
    csv_path = generator.generate_tableau_csv(report)

    # Save to database
    if save_to_db:
        store = TrustScoreStore()
        store.save_report(report)

    return csv_path
