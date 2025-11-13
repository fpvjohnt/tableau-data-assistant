"""
Data quality assessment and scoring
Calculates comprehensive quality metrics for datasets
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

from config.settings import QUALITY_WEIGHTS
from utils.logger import get_logger

logger = get_logger(__name__)


class DataQualityScorer:
    """Calculate data quality scores and metrics"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize quality scorer

        Args:
            df: DataFrame to assess
        """
        self.df = df
        self.total_cells = df.shape[0] * df.shape[1]
        self.scores = {}
        self.details = {}

    def calculate_completeness_score(self) -> float:
        """
        Calculate completeness score based on missing values

        Returns:
            Completeness score (0-100)
        """
        if self.total_cells == 0:
            self.details['completeness'] = {
                'total_cells': 0,
                'missing_cells': 0,
                'missing_percentage': 0.0,
                'columns_with_missing': []
            }
            return 0.0

        missing_cells = self.df.isnull().sum().sum()
        completeness = ((self.total_cells - missing_cells) / self.total_cells) * 100

        self.details['completeness'] = {
            'total_cells': self.total_cells,
            'missing_cells': int(missing_cells),
            'missing_percentage': round((missing_cells / self.total_cells) * 100, 2),
            'columns_with_missing': self.df.columns[self.df.isnull().any()].tolist()
        }

        logger.debug(f"Completeness score: {completeness:.2f}")
        return completeness

    def calculate_uniqueness_score(self) -> float:
        """
        Calculate uniqueness score based on duplicate records

        Returns:
            Uniqueness score (0-100)
        """
        if len(self.df) == 0:
            return 100.0

        primary_duplicates = self.df.duplicated().sum()
        all_duplicates = self.df.duplicated(keep=False).sum()
        duplicates = int((primary_duplicates + all_duplicates) // 2)
        uniqueness = ((len(self.df) - duplicates) / len(self.df)) * 100

        self.details['uniqueness'] = {
            'total_rows': len(self.df),
            'duplicate_rows': int(duplicates),
            'duplicate_percentage': round((duplicates / len(self.df)) * 100, 2)
        }

        logger.debug(f"Uniqueness score: {uniqueness:.2f}")
        return uniqueness

    def calculate_validity_score(self) -> float:
        """
        Calculate validity score based on data type consistency

        Returns:
            Validity score (0-100)
        """
        validity_issues = 0
        total_checks = 0

        validity_details = {
            'issues': [],
            'total_checks': 0,
            'failed_checks': 0
        }

        for col in self.df.columns:
            col_type = self.df[col].dtype

            # Numeric columns - check for inf, -inf
            if pd.api.types.is_numeric_dtype(col_type):
                inf_count = np.isinf(self.df[col]).sum()
                total_checks += 1
                if inf_count > 0:
                    validity_issues += 1
                    validity_details['issues'].append({
                        'column': col,
                        'issue': f'{inf_count} infinite values'
                    })

            # String columns - check for excessive whitespace, empty strings
            if pd.api.types.is_string_dtype(col_type) or col_type == 'object':
                non_null = self.df[col].dropna()
                if len(non_null) > 0:
                    # Check for leading/trailing whitespace
                    whitespace_count = non_null.astype(str).str.strip().ne(non_null.astype(str)).sum()
                    total_checks += 1
                    if whitespace_count > len(non_null) * 0.1:  # More than 10%
                        validity_issues += 1
                        validity_details['issues'].append({
                            'column': col,
                            'issue': f'{whitespace_count} values with whitespace issues'
                        })

                    # Check for empty strings
                    empty_count = (non_null.astype(str).str.strip() == '').sum()
                    total_checks += 1
                    if empty_count > 0:
                        validity_issues += 1
                        validity_details['issues'].append({
                            'column': col,
                            'issue': f'{empty_count} empty strings'
                        })

            # DateTime columns - check for invalid dates
            if pd.api.types.is_datetime64_any_dtype(col_type):
                total_checks += 1
                # Check for dates in the far future or past
                non_null_dates = self.df[col].dropna()
                if len(non_null_dates) > 0:
                    current_year = datetime.now().year
                    future_dates = (non_null_dates.dt.year > current_year + 50).sum()
                    old_dates = (non_null_dates.dt.year < 1900).sum()

                    if future_dates > 0 or old_dates > 0:
                        validity_issues += 1
                        validity_details['issues'].append({
                            'column': col,
                            'issue': f'{future_dates} future dates, {old_dates} very old dates'
                        })

        validity_details['total_checks'] = total_checks
        validity_details['failed_checks'] = validity_issues

        if total_checks == 0:
            validity_score = 100.0
        else:
            validity_score = ((total_checks - validity_issues) / total_checks) * 100

        self.details['validity'] = validity_details
        logger.debug(f"Validity score: {validity_score:.2f}")
        return validity_score

    def calculate_consistency_score(self) -> float:
        """
        Calculate consistency score based on outliers and anomalies

        Returns:
            Consistency score (0-100)
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            self.details['consistency'] = {'message': 'No numeric columns to assess'}
            return 100.0

        total_outliers = 0
        total_values = 0
        outlier_details = []

        for col in numeric_cols:
            non_null = self.df[col].dropna()
            if len(non_null) == 0:
                continue

            Q1 = non_null.quantile(0.25)
            Q3 = non_null.quantile(0.75)
            IQR = Q3 - Q1

            if IQR == 0:
                continue

            outliers = ((non_null < Q1 - 1.5 * IQR) | (non_null > Q3 + 1.5 * IQR)).sum()
            total_outliers += outliers
            total_values += len(non_null)

            if outliers > 0:
                outlier_details.append({
                    'column': col,
                    'outliers': int(outliers),
                    'percentage': round((outliers / len(non_null)) * 100, 2)
                })

        if total_values == 0:
            consistency_score = 100.0
        else:
            consistency_score = ((total_values - total_outliers) / total_values) * 100

        self.details['consistency'] = {
            'total_numeric_values': total_values,
            'total_outliers': total_outliers,
            'outlier_percentage': round((total_outliers / total_values * 100) if total_values > 0 else 0, 2),
            'columns_with_outliers': outlier_details
        }

        logger.debug(f"Consistency score: {consistency_score:.2f}")
        return consistency_score

    def calculate_timeliness_score(self) -> float:
        """
        Calculate timeliness score based on date relevance

        Returns:
            Timeliness score (0-100)
        """
        date_cols = self.df.select_dtypes(include=['datetime64']).columns

        if len(date_cols) == 0:
            self.details['timeliness'] = {'message': 'No date columns to assess'}
            return 100.0

        timeliness_score = 100.0
        date_details = []

        for col in date_cols:
            non_null_dates = self.df[col].dropna()
            if len(non_null_dates) == 0:
                continue

            max_date = non_null_dates.max()
            current_date = pd.Timestamp.now()

            # Calculate data freshness
            days_old = (current_date - max_date).days

            # Scoring: 100 for current data, decreasing for older data
            if days_old <= 30:
                col_score = 100
            elif days_old <= 180:
                col_score = 80
            elif days_old <= 365:
                col_score = 60
            else:
                col_score = 40

            date_details.append({
                'column': col,
                'max_date': str(max_date.date()),
                'days_old': days_old,
                'score': col_score
            })

            timeliness_score = min(timeliness_score, col_score)

        self.details['timeliness'] = {
            'date_columns': date_details,
            'overall_freshness': 'Current' if timeliness_score >= 80 else 'Moderately old' if timeliness_score >= 60 else 'Old'
        }

        logger.debug(f"Timeliness score: {timeliness_score:.2f}")
        return timeliness_score

    def calculate_overall_score(self) -> Dict:
        """
        Calculate overall data quality score

        Returns:
            Dictionary with scores and details
        """
        logger.info("Calculating data quality scores...")

        # Calculate individual scores
        self.scores['completeness'] = self.calculate_completeness_score()
        self.scores['uniqueness'] = self.calculate_uniqueness_score()
        self.scores['validity'] = self.calculate_validity_score()
        self.scores['consistency'] = self.calculate_consistency_score()
        self.scores['timeliness'] = self.calculate_timeliness_score()

        # Calculate weighted overall score
        overall_score = sum(
            self.scores[dimension] * QUALITY_WEIGHTS[dimension]
            for dimension in QUALITY_WEIGHTS.keys()
        )

        # Determine grade
        if overall_score >= 90:
            grade = 'A'
            rating = 'Excellent'
        elif overall_score >= 80:
            grade = 'B'
            rating = 'Good'
        elif overall_score >= 70:
            grade = 'C'
            rating = 'Fair'
        elif overall_score >= 60:
            grade = 'D'
            rating = 'Poor'
        else:
            grade = 'F'
            rating = 'Very Poor'

        result = {
            'overall_score': round(overall_score, 2),
            'grade': grade,
            'rating': rating,
            'dimension_scores': {k: round(v, 2) for k, v in self.scores.items()},
            'details': self.details,
            'recommendations': self._generate_recommendations()
        }

        logger.info(f"Overall quality score: {overall_score:.2f} (Grade: {grade})")
        return result

    def _generate_recommendations(self) -> List[str]:
        """
        Generate recommendations based on scores

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Completeness recommendations
        if self.scores['completeness'] < 80:
            missing_pct = self.details['completeness']['missing_percentage']
            recommendations.append(
                f"📊 Address {missing_pct}% missing values - consider imputation or removal of incomplete records"
            )

        # Uniqueness recommendations
        if self.scores['uniqueness'] < 95:
            dup_pct = self.details['uniqueness']['duplicate_percentage']
            recommendations.append(
                f"🔄 Remove {dup_pct}% duplicate rows to improve data quality"
            )

        # Validity recommendations
        if self.scores['validity'] < 90:
            issues = len(self.details['validity']['issues'])
            recommendations.append(
                f"✅ Fix {issues} validity issues (whitespace, empty strings, invalid values)"
            )

        # Consistency recommendations
        if self.scores['consistency'] < 85:
            outlier_pct = self.details['consistency'].get('outlier_percentage', 0)
            recommendations.append(
                f"📉 Investigate {outlier_pct}% outliers - may indicate data entry errors or genuine extreme values"
            )

        # Timeliness recommendations
        if self.scores['timeliness'] < 70:
            recommendations.append(
                "⏰ Data appears outdated - consider refreshing from source"
            )

        if not recommendations:
            recommendations.append("✨ Data quality is excellent - ready for analysis!")

        return recommendations


def calculate_quality_score(df: pd.DataFrame) -> Dict:
    """
    Convenience function to calculate data quality score

    Args:
        df: DataFrame to assess

    Returns:
        Quality score dictionary
    """
    scorer = DataQualityScorer(df)
    return scorer.calculate_overall_score()
