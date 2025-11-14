"""
Anomaly detection module for Tableau Data Assistant
Provides deterministic outlier and anomaly detection for data quality analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import stats

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    StandardScaler = None

from config.settings import (
    ANOMALY_CONTAMINATION,
    ANOMALY_N_ESTIMATORS,
    ANOMALY_MAX_FEATURES,
    OUTLIER_IQR_MULTIPLIER
)


@dataclass
class AnomalyReport:
    """Report of anomaly detection results"""
    method: str = "unknown"
    total_anomalies: int = 0
    anomaly_percentage: float = 0.0
    anomalies_by_column: Dict[str, int] = field(default_factory=dict)
    anomaly_indices: List[int] = field(default_factory=list)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'method': self.method,
            'total_anomalies': self.total_anomalies,
            'anomaly_percentage': self.anomaly_percentage,
            'anomalies_by_column': self.anomalies_by_column,
            'anomaly_indices': self.anomaly_indices,
            'feature_importance': self.feature_importance,
            'summary_stats': self.summary_stats,
            'timestamp': self.timestamp.isoformat()
        }


class IQRAnomalyDetector:
    """
    IQR-based anomaly detection (deterministic, no ML required)
    Uses Interquartile Range method for outlier detection
    """

    def __init__(self, multiplier: float = OUTLIER_IQR_MULTIPLIER):
        """
        Initialize IQR detector

        Args:
            multiplier: IQR multiplier for outlier bounds (default 1.5)
        """
        self.multiplier = multiplier

    def detect(self, df: pd.DataFrame) -> AnomalyReport:
        """
        Detect anomalies using IQR method

        Args:
            df: DataFrame to analyze

        Returns:
            AnomalyReport with detection results
        """
        report = AnomalyReport(method="IQR")

        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return report

        # Track anomalies per row
        anomaly_mask = pd.Series([False] * len(df), index=df.index)

        # Detect anomalies for each numeric column
        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            # Calculate IQR
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1

            # Calculate bounds
            lower_bound = Q1 - self.multiplier * IQR
            upper_bound = Q3 + self.multiplier * IQR

            # Find outliers
            col_anomalies = (df[col] < lower_bound) | (df[col] > upper_bound)
            anomaly_count = col_anomalies.sum()

            if anomaly_count > 0:
                report.anomalies_by_column[col] = int(anomaly_count)
                anomaly_mask |= col_anomalies

                # Store summary stats
                report.summary_stats[col] = {
                    'Q1': float(Q1),
                    'Q3': float(Q3),
                    'IQR': float(IQR),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'outlier_count': int(anomaly_count)
                }

        # Aggregate results
        report.total_anomalies = int(anomaly_mask.sum())
        report.anomaly_percentage = (report.total_anomalies / len(df)) * 100
        report.anomaly_indices = df[anomaly_mask].index.tolist()

        return report

    def get_outlier_bounds(self, df: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
        """
        Get outlier bounds for each numeric column

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary mapping column names to (lower_bound, upper_bound) tuples
        """
        bounds = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - self.multiplier * IQR
            upper_bound = Q3 + self.multiplier * IQR

            bounds[col] = (float(lower_bound), float(upper_bound))

        return bounds


class ZScoreAnomalyDetector:
    """
    Z-score based anomaly detection (deterministic)
    Detects values that are N standard deviations from mean
    """

    def __init__(self, threshold: float = 3.0):
        """
        Initialize Z-score detector

        Args:
            threshold: Number of standard deviations for outlier threshold
        """
        self.threshold = threshold

    def detect(self, df: pd.DataFrame) -> AnomalyReport:
        """
        Detect anomalies using Z-score method

        Args:
            df: DataFrame to analyze

        Returns:
            AnomalyReport with detection results
        """
        report = AnomalyReport(method="Z-Score")

        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return report

        # Track anomalies per row
        anomaly_mask = pd.Series([False] * len(df), index=df.index)

        # Detect anomalies for each numeric column
        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            # Calculate z-scores
            mean = col_data.mean()
            std = col_data.std()

            if std == 0:  # Avoid division by zero
                continue

            z_scores = np.abs((df[col] - mean) / std)
            col_anomalies = z_scores > self.threshold

            anomaly_count = col_anomalies.sum()

            if anomaly_count > 0:
                report.anomalies_by_column[col] = int(anomaly_count)
                anomaly_mask |= col_anomalies

                # Store summary stats
                report.summary_stats[col] = {
                    'mean': float(mean),
                    'std': float(std),
                    'threshold': self.threshold,
                    'outlier_count': int(anomaly_count)
                }

        # Aggregate results
        report.total_anomalies = int(anomaly_mask.sum())
        report.anomaly_percentage = (report.total_anomalies / len(df)) * 100
        report.anomaly_indices = df[anomaly_mask].index.tolist()

        return report


class IsolationForestDetector:
    """
    Isolation Forest anomaly detection (ML-based)
    Requires scikit-learn. Falls back to IQR if not available.
    """

    def __init__(
        self,
        contamination: float = ANOMALY_CONTAMINATION,
        n_estimators: int = ANOMALY_N_ESTIMATORS,
        max_features: float = ANOMALY_MAX_FEATURES,
        random_state: int = 42
    ):
        """
        Initialize Isolation Forest detector

        Args:
            contamination: Expected proportion of anomalies
            n_estimators: Number of trees in the forest
            max_features: Features to use per tree
            random_state: Random seed for reproducibility
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is required for Isolation Forest detection. "
                "Install with: pip install scikit-learn"
            )

        self.contamination = contamination
        self.n_estimators = n_estimators
        self.max_features = max_features
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.feature_names = None

    def detect(self, df: pd.DataFrame) -> AnomalyReport:
        """
        Detect anomalies using Isolation Forest

        Args:
            df: DataFrame to analyze

        Returns:
            AnomalyReport with detection results
        """
        report = AnomalyReport(method="Isolation Forest")

        # Get numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return report

        # Prepare data
        X = df[numeric_cols].copy()

        # Handle missing values (impute with median)
        X = X.fillna(X.median())

        # Check if we have data
        if len(X) == 0 or X.shape[1] == 0:
            return report

        self.feature_names = numeric_cols

        # Standardize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Fit Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            max_features=self.max_features,
            random_state=self.random_state,
            n_jobs=-1  # Use all CPU cores
        )

        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.model.fit_predict(X_scaled)
        anomaly_mask = predictions == -1

        # Get anomaly scores (lower is more anomalous)
        anomaly_scores = self.model.score_samples(X_scaled)

        # Count anomalies per column (approximate using contribution)
        for i, col in enumerate(numeric_cols):
            col_contribution = self._calculate_feature_contribution(X_scaled, anomaly_mask, i)
            if col_contribution > 0:
                report.feature_importance[col] = float(col_contribution)

                # Estimate anomalies for this column
                col_anomalies = int(anomaly_mask.sum() * col_contribution)
                if col_anomalies > 0:
                    report.anomalies_by_column[col] = col_anomalies

        # Aggregate results
        report.total_anomalies = int(anomaly_mask.sum())
        report.anomaly_percentage = (report.total_anomalies / len(df)) * 100
        report.anomaly_indices = df[anomaly_mask].index.tolist()

        # Summary statistics
        report.summary_stats = {
            'mean_anomaly_score': float(anomaly_scores[anomaly_mask].mean()) if anomaly_mask.sum() > 0 else 0.0,
            'mean_normal_score': float(anomaly_scores[~anomaly_mask].mean()) if (~anomaly_mask).sum() > 0 else 0.0,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators
        }

        return report

    def _calculate_feature_contribution(
        self,
        X: np.ndarray,
        anomaly_mask: np.ndarray,
        feature_idx: int
    ) -> float:
        """
        Calculate approximate contribution of a feature to anomalies

        Args:
            X: Scaled feature matrix
            anomaly_mask: Boolean mask of anomalies
            feature_idx: Index of feature to analyze

        Returns:
            Contribution score (0-1)
        """
        if anomaly_mask.sum() == 0:
            return 0.0

        # Get feature values for anomalies
        anomaly_values = X[anomaly_mask, feature_idx]
        normal_values = X[~anomaly_mask, feature_idx]

        if len(anomaly_values) == 0 or len(normal_values) == 0:
            return 0.0

        # Calculate separation (using absolute mean difference)
        separation = abs(np.mean(anomaly_values) - np.mean(normal_values))

        # Normalize by standard deviation
        std = np.std(X[:, feature_idx])
        if std > 0:
            return min(separation / std, 1.0)

        return 0.0


class AnomalyDetectorEnsemble:
    """
    Ensemble of multiple anomaly detection methods
    Combines IQR, Z-score, and optionally Isolation Forest
    """

    def __init__(
        self,
        use_iqr: bool = True,
        use_zscore: bool = True,
        use_isolation_forest: bool = False,
        voting: str = 'majority'
    ):
        """
        Initialize ensemble detector

        Args:
            use_iqr: Use IQR method
            use_zscore: Use Z-score method
            use_isolation_forest: Use Isolation Forest (requires scikit-learn)
            voting: Voting strategy ('majority', 'unanimous', 'any')
        """
        self.use_iqr = use_iqr
        self.use_zscore = use_zscore
        self.use_isolation_forest = use_isolation_forest and SKLEARN_AVAILABLE
        self.voting = voting

        self.detectors = []

        if self.use_iqr:
            self.detectors.append(('IQR', IQRAnomalyDetector()))
        if self.use_zscore:
            self.detectors.append(('Z-Score', ZScoreAnomalyDetector()))
        if self.use_isolation_forest:
            self.detectors.append(('Isolation Forest', IsolationForestDetector()))

    def detect(self, df: pd.DataFrame) -> AnomalyReport:
        """
        Detect anomalies using ensemble approach

        Args:
            df: DataFrame to analyze

        Returns:
            AnomalyReport with combined results
        """
        if not self.detectors:
            return AnomalyReport(method="Ensemble (empty)")

        # Run all detectors
        detector_reports = []
        for name, detector in self.detectors:
            report = detector.detect(df)
            detector_reports.append((name, report))

        # Combine results based on voting strategy
        combined_report = self._combine_reports(df, detector_reports)

        return combined_report

    def _combine_reports(
        self,
        df: pd.DataFrame,
        reports: List[Tuple[str, AnomalyReport]]
    ) -> AnomalyReport:
        """Combine multiple anomaly reports using voting strategy"""
        combined = AnomalyReport(method=f"Ensemble ({self.voting} voting)")

        # Create anomaly masks for each detector
        masks = []
        for name, report in reports:
            mask = pd.Series([False] * len(df), index=df.index)
            mask.iloc[report.anomaly_indices] = True
            masks.append(mask)

        # Apply voting strategy
        if self.voting == 'majority':
            # Anomaly if majority of detectors agree
            vote_counts = sum(masks)
            threshold = len(masks) / 2
            final_mask = vote_counts > threshold
        elif self.voting == 'unanimous':
            # Anomaly only if all detectors agree
            final_mask = masks[0]
            for mask in masks[1:]:
                final_mask &= mask
        elif self.voting == 'any':
            # Anomaly if any detector flags it
            final_mask = masks[0]
            for mask in masks[1:]:
                final_mask |= mask
        else:
            # Default to majority
            vote_counts = sum(masks)
            threshold = len(masks) / 2
            final_mask = vote_counts > threshold

        # Populate combined report
        combined.total_anomalies = int(final_mask.sum())
        combined.anomaly_percentage = (combined.total_anomalies / len(df)) * 100
        combined.anomaly_indices = df[final_mask].index.tolist()

        # Aggregate column-level anomalies
        all_cols = set()
        for name, report in reports:
            all_cols.update(report.anomalies_by_column.keys())

        for col in all_cols:
            counts = [report.anomalies_by_column.get(col, 0) for name, report in reports]
            combined.anomalies_by_column[col] = int(np.mean(counts))

        # Store individual detector results in summary
        combined.summary_stats['detector_results'] = {
            name: {
                'total_anomalies': report.total_anomalies,
                'percentage': report.anomaly_percentage
            }
            for name, report in reports
        }

        return combined


def generate_anomaly_summary(report: AnomalyReport) -> str:
    """
    Generate human-readable anomaly detection summary

    Args:
        report: AnomalyReport to summarize

    Returns:
        Formatted string summary
    """
    summary_lines = [
        f"### Anomaly Detection Report ({report.method})",
        "",
        f"**Total Anomalies:** {report.total_anomalies:,} ({report.anomaly_percentage:.2f}%)",
        ""
    ]

    if report.anomalies_by_column:
        summary_lines.append("**Anomalies by Column:**")
        sorted_cols = sorted(
            report.anomalies_by_column.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for col, count in sorted_cols[:10]:  # Top 10
            summary_lines.append(f"  - {col}: {count:,} anomalies")

        if len(report.anomalies_by_column) > 10:
            summary_lines.append(f"  - ... and {len(report.anomalies_by_column) - 10} more columns")

    if report.feature_importance:
        summary_lines.append("\n**Feature Importance:**")
        sorted_features = sorted(
            report.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for feature, importance in sorted_features[:5]:  # Top 5
            summary_lines.append(f"  - {feature}: {importance:.3f}")

    if not report.anomalies_by_column:
        summary_lines.append("No significant anomalies detected.")

    return "\n".join(summary_lines)


# Convenience function
def detect_anomalies(
    df: pd.DataFrame,
    method: str = 'iqr',
    **kwargs
) -> AnomalyReport:
    """
    One-line function to detect anomalies

    Args:
        df: DataFrame to analyze
        method: Detection method ('iqr', 'zscore', 'isolation_forest', 'ensemble')
        **kwargs: Additional arguments for detector

    Returns:
        AnomalyReport with results
    """
    if method == 'iqr':
        detector = IQRAnomalyDetector(**kwargs)
    elif method == 'zscore':
        detector = ZScoreAnomalyDetector(**kwargs)
    elif method == 'isolation_forest':
        detector = IsolationForestDetector(**kwargs)
    elif method == 'ensemble':
        detector = AnomalyDetectorEnsemble(**kwargs)
    else:
        raise ValueError(f"Unknown detection method: {method}")

    return detector.detect(df)
