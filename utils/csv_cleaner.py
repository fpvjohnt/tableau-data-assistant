"""
CSV Data Cleaning Utility
Automatically fixes common data quality issues in CSV files
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

from utils.logger import get_logger

logger = get_logger(__name__)

# Import store number extractor if available
try:
    from utils.store_number_extractor import process_store_data
    STORE_EXTRACTOR_AVAILABLE = True
except ImportError:
    STORE_EXTRACTOR_AVAILABLE = False
    logger.warning("Store number extractor not available")


class CSVCleaner:
    """Clean and fix common data quality issues in CSV files"""

    def __init__(self, df: pd.DataFrame, auto_fix: bool = True):
        """
        Initialize CSV cleaner

        Args:
            df: DataFrame to clean
            auto_fix: Automatically apply recommended fixes
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.auto_fix = auto_fix
        self.cleaning_log = []
        self.stats = {
            'original_rows': len(df),
            'original_columns': len(df.columns),
            'rows_removed': 0,
            'duplicates_removed': 0,
            'missing_values_handled': 0,
            'whitespace_fixed': 0,
            'outliers_capped': 0,
            'data_types_converted': 0
        }

    def clean_all(self) -> Tuple[pd.DataFrame, Dict]:
        """
        Apply all cleaning operations

        Returns:
            Tuple of (cleaned_df, cleaning_report)
        """
        logger.info("Starting comprehensive CSV cleaning...")

        # 1. Remove completely empty rows and columns
        self._remove_empty_rows_columns()

        # 2. Remove duplicate rows
        self._remove_duplicates()

        # 3. Fix whitespace issues
        self._fix_whitespace()

        # 4. Handle missing values
        self._handle_missing_values()

        # 5. Fix data types
        self._fix_data_types()

        # 6. Handle outliers
        self._handle_outliers()

        # 7. Standardize text
        self._standardize_text()

        # 8. Fix date formats
        self._fix_date_formats()

        # 9. Fix store numbers (if applicable)
        self._fix_store_numbers()

        # Update final stats
        self.stats['final_rows'] = len(self.df)
        self.stats['final_columns'] = len(self.df.columns)
        self.stats['rows_removed'] = self.stats['original_rows'] - self.stats['final_rows']

        report = self._generate_report()
        logger.info(f"Cleaning complete: {self.stats['rows_removed']} rows removed, {len(self.cleaning_log)} operations applied")

        return self.df, report

    def _remove_empty_rows_columns(self):
        """Remove completely empty rows and columns"""
        initial_shape = self.df.shape

        # Remove empty rows
        self.df = self.df.dropna(how='all')

        # Remove empty columns
        self.df = self.df.dropna(axis=1, how='all')

        rows_removed = initial_shape[0] - self.df.shape[0]
        cols_removed = initial_shape[1] - self.df.shape[1]

        if rows_removed > 0 or cols_removed > 0:
            self.cleaning_log.append(
                f"Removed {rows_removed} empty rows and {cols_removed} empty columns"
            )
            logger.debug(f"Removed {rows_removed} empty rows, {cols_removed} empty columns")

    def _remove_duplicates(self):
        """Remove duplicate rows"""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        duplicates_removed = initial_count - len(self.df)

        self.stats['duplicates_removed'] = duplicates_removed

        if duplicates_removed > 0:
            self.cleaning_log.append(
                f"Removed {duplicates_removed} duplicate rows ({(duplicates_removed/initial_count*100):.1f}%)"
            )
            logger.debug(f"Removed {duplicates_removed} duplicate rows")

    def _fix_whitespace(self):
        """Fix leading/trailing whitespace in string columns"""
        whitespace_fixed = 0

        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                # Count how many have whitespace
                before = self.df[col].astype(str).str.strip().ne(self.df[col].astype(str)).sum()

                if before > 0:
                    self.df[col] = self.df[col].astype(str).str.strip()
                    whitespace_fixed += before

        self.stats['whitespace_fixed'] = whitespace_fixed

        if whitespace_fixed > 0:
            self.cleaning_log.append(
                f"Fixed whitespace in {whitespace_fixed} values"
            )
            logger.debug(f"Fixed whitespace in {whitespace_fixed} values")

    def _handle_missing_values(self):
        """Handle missing values intelligently"""
        missing_handled = 0

        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()

            if missing_count == 0:
                continue

            missing_pct = (missing_count / len(self.df)) * 100

            # If more than 50% missing, consider dropping column
            if missing_pct > 50:
                self.cleaning_log.append(
                    f"Column '{col}' has {missing_pct:.1f}% missing - consider removing"
                )
                continue

            # For numeric columns, fill with median
            if pd.api.types.is_numeric_dtype(self.df[col]):
                median_val = self.df[col].median()
                self.df[col] = self.df[col].fillna(median_val)
                missing_handled += missing_count
                self.cleaning_log.append(
                    f"Filled {missing_count} missing values in '{col}' with median ({median_val:.2f})"
                )

            # For categorical columns, fill with mode or 'Unknown'
            elif self.df[col].dtype == 'object':
                if self.df[col].mode().empty:
                    self.df[col] = self.df[col].fillna('Unknown')
                else:
                    mode_val = self.df[col].mode()[0]
                    self.df[col] = self.df[col].fillna(mode_val)
                missing_handled += missing_count
                self.cleaning_log.append(
                    f"Filled {missing_count} missing values in '{col}' with mode or 'Unknown'"
                )

        self.stats['missing_values_handled'] = missing_handled
        logger.debug(f"Handled {missing_handled} missing values")

    def _fix_data_types(self):
        """Attempt to convert columns to appropriate data types"""
        conversions = 0

        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    # Remove common non-numeric characters
                    cleaned = self.df[col].astype(str).str.replace(',', '').str.replace('$', '').str.replace('%', '')
                    numeric_series = pd.to_numeric(cleaned, errors='coerce')

                    # If more than 80% can be converted, do it
                    if numeric_series.notna().sum() / len(self.df) > 0.8:
                        self.df[col] = numeric_series
                        conversions += 1
                        self.cleaning_log.append(
                            f"Converted '{col}' to numeric type"
                        )
                        continue
                except:
                    pass

                # Try to convert to datetime
                try:
                    date_series = pd.to_datetime(self.df[col], errors='coerce')

                    # If more than 80% can be converted, do it
                    if date_series.notna().sum() / len(self.df) > 0.8:
                        self.df[col] = date_series
                        conversions += 1
                        self.cleaning_log.append(
                            f"Converted '{col}' to datetime type"
                        )
                        continue
                except:
                    pass

        self.stats['data_types_converted'] = conversions
        logger.debug(f"Converted {conversions} columns to appropriate types")

    def _handle_outliers(self):
        """Handle outliers in numeric columns using IQR method"""
        outliers_capped = 0

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            non_null = self.df[col].dropna()

            if len(non_null) == 0:
                continue

            Q1 = non_null.quantile(0.25)
            Q3 = non_null.quantile(0.75)
            IQR = Q3 - Q1

            if IQR == 0:
                continue

            lower_bound = Q1 - 3 * IQR  # Using 3*IQR for extreme outliers
            upper_bound = Q3 + 3 * IQR

            # Count outliers
            outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()

            if outliers > 0:
                # Cap outliers
                self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
                outliers_capped += outliers
                self.cleaning_log.append(
                    f"Capped {outliers} extreme outliers in '{col}' (range: {lower_bound:.2f} to {upper_bound:.2f})"
                )

        self.stats['outliers_capped'] = outliers_capped
        logger.debug(f"Capped {outliers_capped} extreme outliers")

    def _standardize_text(self):
        """Standardize text columns (case, special characters)"""
        standardized = 0

        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                # Remove extra spaces
                before_count = len(self.df)
                self.df[col] = self.df[col].astype(str).str.replace(r'\s+', ' ', regex=True)

                # Check if column seems to be categorical with limited unique values
                unique_ratio = self.df[col].nunique() / len(self.df)

                if unique_ratio < 0.1:  # Less than 10% unique values (likely categorical)
                    # Standardize case for categorical columns
                    self.df[col] = self.df[col].str.title()
                    standardized += 1

        if standardized > 0:
            self.cleaning_log.append(
                f"Standardized text formatting in {standardized} categorical columns"
            )
            logger.debug(f"Standardized {standardized} text columns")

    def _fix_date_formats(self):
        """Ensure consistent date formats"""
        date_cols = self.df.select_dtypes(include=['datetime64']).columns

        for col in date_cols:
            # Remove timezone info if present (can cause issues in Tableau)
            if hasattr(self.df[col].dtype, 'tz') and self.df[col].dtype.tz is not None:
                self.df[col] = self.df[col].dt.tz_localize(None)
                self.cleaning_log.append(
                    f"Removed timezone info from '{col}' for Tableau compatibility"
                )

    def _fix_store_numbers(self):
        """Fix store numbers - remove decimals and extract from summary if needed"""
        if not STORE_EXTRACTOR_AVAILABLE:
            logger.debug("Store number extractor not available, skipping")
            return

        # Check if we have both Summary and Store Number columns
        has_summary = 'Summary' in self.df.columns
        has_store_num = 'Store Number' in self.df.columns

        if not has_summary and not has_store_num:
            logger.debug("No 'Summary' or 'Store Number' columns found, skipping store number processing")
            return

        logger.info("Processing store numbers...")

        # Process store numbers
        before_count = self.df['Store Number'].notna().sum() if has_store_num else 0

        self.df = process_store_data(
            self.df,
            summary_column='Summary',
            store_column='Store Number'
        )

        after_count = self.df['Store Number'].notna().sum()

        if after_count > before_count:
            recovered = after_count - before_count
            self.cleaning_log.append(
                f"Fixed store numbers: removed decimals and extracted {recovered} missing store numbers from summary"
            )
        elif before_count > 0:
            self.cleaning_log.append(
                f"Fixed store numbers: removed decimal points from {before_count} store numbers"
            )

    def _generate_report(self) -> Dict:
        """
        Generate cleaning report

        Returns:
            Report dictionary
        """
        report = {
            'stats': self.stats,
            'operations': self.cleaning_log,
            'summary': {
                'original_size': f"{self.stats['original_rows']} rows × {self.stats['original_columns']} columns",
                'final_size': f"{self.stats['final_rows']} rows × {self.stats['final_columns']} columns",
                'data_reduction': f"{self.stats['rows_removed']} rows removed",
                'quality_improvements': len(self.cleaning_log)
            },
            'recommendations': self._generate_recommendations()
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for further improvement"""
        recommendations = []

        # Check for high missing value columns
        missing_pct_by_col = (self.df.isnull().sum() / len(self.df)) * 100
        high_missing = missing_pct_by_col[missing_pct_by_col > 30]

        if len(high_missing) > 0:
            recommendations.append(
                f"Consider removing {len(high_missing)} columns with >30% missing values: {', '.join(high_missing.index[:3])}"
            )

        # Check for low variance columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if self.df[col].std() == 0:
                recommendations.append(
                    f"Column '{col}' has zero variance - consider removing"
                )

        # Check for high cardinality categorical columns
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                unique_ratio = self.df[col].nunique() / len(self.df)
                if unique_ratio > 0.9:
                    recommendations.append(
                        f"Column '{col}' has very high cardinality ({self.df[col].nunique()} unique values) - may not be useful for analysis"
                    )

        if not recommendations:
            recommendations.append("Data is well-structured and ready for Tableau!")

        return recommendations


def clean_csv(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to clean CSV data

    Args:
        df: DataFrame to clean

    Returns:
        Tuple of (cleaned_df, report)
    """
    cleaner = CSVCleaner(df)
    return cleaner.clean_all()


def get_data_discrepancies(df: pd.DataFrame) -> Dict:
    """
    Get comprehensive discrepancy report for CSV data

    Args:
        df: DataFrame to analyze

    Returns:
        Discrepancy report dictionary
    """
    logger.info("Analyzing data for discrepancies...")

    discrepancies = {
        'missing_values': {},
        'duplicates': {},
        'data_type_issues': {},
        'outliers': {},
        'text_issues': {},
        'date_issues': {},
        'summary': {}
    }

    # 1. Missing values
    missing_by_col = df.isnull().sum()
    missing_pct_by_col = (missing_by_col / len(df)) * 100
    discrepancies['missing_values'] = {
        'total_missing_cells': int(missing_by_col.sum()),
        'columns_with_missing': {
            col: {
                'count': int(missing_by_col[col]),
                'percentage': round(missing_pct_by_col[col], 2)
            }
            for col in missing_by_col[missing_by_col > 0].index
        }
    }

    # 2. Duplicates
    duplicate_count = df.duplicated().sum()
    discrepancies['duplicates'] = {
        'total_duplicates': int(duplicate_count),
        'percentage': round((duplicate_count / len(df)) * 100, 2) if len(df) > 0 else 0
    }

    # 3. Data type issues
    type_issues = []
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if it should be numeric
            try:
                cleaned = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                numeric = pd.to_numeric(cleaned, errors='coerce')
                convertible_pct = (numeric.notna().sum() / len(df)) * 100

                if 50 < convertible_pct < 95:  # Partially convertible
                    type_issues.append({
                        'column': col,
                        'issue': f'{convertible_pct:.1f}% of values could be numeric',
                        'suggestion': 'Check for mixed data types'
                    })
            except:
                pass

    discrepancies['data_type_issues'] = type_issues

    # 4. Outliers
    outlier_info = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue

        Q1 = non_null.quantile(0.25)
        Q3 = non_null.quantile(0.75)
        IQR = Q3 - Q1

        if IQR > 0:
            outliers = ((non_null < Q1 - 1.5 * IQR) | (non_null > Q3 + 1.5 * IQR)).sum()
            if outliers > 0:
                outlier_info[col] = {
                    'count': int(outliers),
                    'percentage': round((outliers / len(non_null)) * 100, 2),
                    'range': f'{non_null.min():.2f} to {non_null.max():.2f}'
                }

    discrepancies['outliers'] = outlier_info

    # 5. Text issues
    text_issues = []
    for col in df.columns:
        if df[col].dtype == 'object':
            non_null = df[col].dropna()
            if len(non_null) == 0:
                continue

            # Whitespace
            whitespace_count = non_null.astype(str).str.strip().ne(non_null.astype(str)).sum()
            if whitespace_count > 0:
                text_issues.append({
                    'column': col,
                    'issue': f'{whitespace_count} values with leading/trailing whitespace'
                })

            # Empty strings
            empty_count = (non_null.astype(str).str.strip() == '').sum()
            if empty_count > 0:
                text_issues.append({
                    'column': col,
                    'issue': f'{empty_count} empty strings'
                })

    discrepancies['text_issues'] = text_issues

    # 6. Date issues
    date_issues = []
    date_cols = df.select_dtypes(include=['datetime64']).columns

    for col in date_cols:
        non_null_dates = df[col].dropna()
        if len(non_null_dates) == 0:
            continue

        current_year = datetime.now().year
        future_dates = (non_null_dates.dt.year > current_year + 10).sum()
        old_dates = (non_null_dates.dt.year < 1900).sum()

        if future_dates > 0:
            date_issues.append({
                'column': col,
                'issue': f'{future_dates} dates more than 10 years in the future'
            })

        if old_dates > 0:
            date_issues.append({
                'column': col,
                'issue': f'{old_dates} dates before 1900'
            })

    discrepancies['date_issues'] = date_issues

    # Summary
    total_issues = (
        len(discrepancies['missing_values']['columns_with_missing']) +
        (1 if discrepancies['duplicates']['total_duplicates'] > 0 else 0) +
        len(type_issues) +
        len(outlier_info) +
        len(text_issues) +
        len(date_issues)
    )

    discrepancies['summary'] = {
        'total_issues': total_issues,
        'severity': 'High' if total_issues > 10 else 'Medium' if total_issues > 5 else 'Low',
        'recommendation': 'Run CSV cleaner to fix issues automatically' if total_issues > 0 else 'Data looks clean!'
    }

    logger.info(f"Discrepancy analysis complete: {total_issues} issues found")
    return discrepancies
