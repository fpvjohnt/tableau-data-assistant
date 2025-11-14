"""
Data cleaning module for Tableau Data Assistant
Provides comprehensive data cleaning and transformation utilities
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
import re

from config.settings import (
    MAX_TABLEAU_ROWS,
    DATETIME_CONFIDENCE_THRESHOLD,
    NUMERIC_CONFIDENCE_THRESHOLD,
    OUTLIER_IQR_MULTIPLIER
)


@dataclass
class CleaningReport:
    """Report of cleaning operations performed"""
    actions: List[str] = field(default_factory=list)
    original_shape: Tuple[int, int] = (0, 0)
    cleaned_shape: Tuple[int, int] = (0, 0)
    rows_removed: int = 0
    columns_removed: int = 0
    duplicates_removed: int = 0
    type_conversions: Dict[str, str] = field(default_factory=dict)
    missing_values_handled: Dict[str, int] = field(default_factory=dict)
    outliers_detected: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def add_action(self, action: str):
        """Add a cleaning action to the report"""
        self.actions.append(action)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'actions': self.actions,
            'original_shape': self.original_shape,
            'cleaned_shape': self.cleaned_shape,
            'rows_removed': self.rows_removed,
            'columns_removed': self.columns_removed,
            'duplicates_removed': self.duplicates_removed,
            'type_conversions': self.type_conversions,
            'missing_values_handled': self.missing_values_handled,
            'outliers_detected': self.outliers_detected,
            'timestamp': self.timestamp.isoformat()
        }


class DataCleaner:
    """Comprehensive data cleaning for Tableau imports"""

    def __init__(
        self,
        max_rows: int = MAX_TABLEAU_ROWS,
        datetime_threshold: float = DATETIME_CONFIDENCE_THRESHOLD,
        numeric_threshold: float = NUMERIC_CONFIDENCE_THRESHOLD
    ):
        """
        Initialize data cleaner

        Args:
            max_rows: Maximum rows to keep (for Tableau performance)
            datetime_threshold: Confidence threshold for datetime conversion
            numeric_threshold: Confidence threshold for numeric conversion
        """
        self.max_rows = max_rows
        self.datetime_threshold = datetime_threshold
        self.numeric_threshold = numeric_threshold

    def auto_clean_df(
        self,
        df: pd.DataFrame,
        aggressive: bool = False
    ) -> Tuple[pd.DataFrame, CleaningReport]:
        """
        Automatically clean DataFrame for Tableau

        Args:
            df: DataFrame to clean
            aggressive: If True, apply more aggressive cleaning

        Returns:
            Tuple of (cleaned DataFrame, CleaningReport)
        """
        report = CleaningReport()
        report.original_shape = df.shape

        # Create a copy to avoid modifying original
        df_cleaned = df.copy()

        # Step 1: Standardize column names
        df_cleaned = self._standardize_column_names(df_cleaned, report)

        # Step 2: Remove completely empty rows and columns
        df_cleaned = self._remove_empty_rows_cols(df_cleaned, report)

        # Step 3: Remove duplicate rows
        df_cleaned = self._remove_duplicates(df_cleaned, report)

        # Step 4: Convert data types
        df_cleaned = self._convert_data_types(df_cleaned, report)

        # Step 5: Handle missing values
        df_cleaned = self._handle_missing_values(df_cleaned, report, aggressive)

        # Step 6: Trim whitespace from string columns
        df_cleaned = self._trim_whitespace(df_cleaned, report)

        # Step 7: Cap rows for Tableau performance
        df_cleaned = self._cap_rows(df_cleaned, report)

        # Step 8: Optimize data types for memory
        df_cleaned = self._optimize_dtypes(df_cleaned, report)

        # Calculate final statistics
        report.cleaned_shape = df_cleaned.shape
        report.rows_removed = report.original_shape[0] - report.cleaned_shape[0]
        report.columns_removed = report.original_shape[1] - report.cleaned_shape[1]

        return df_cleaned, report

    def _standardize_column_names(
        self,
        df: pd.DataFrame,
        report: CleaningReport
    ) -> pd.DataFrame:
        """Standardize column names for Tableau"""
        original_cols = df.columns.tolist()

        # Remove leading/trailing whitespace
        new_cols = [str(col).strip() for col in df.columns]

        # Replace spaces and special chars with underscores
        new_cols = [re.sub(r'[^\w\s]', '_', col) for col in new_cols]
        new_cols = [re.sub(r'\s+', '_', col) for col in new_cols]

        # Remove consecutive underscores
        new_cols = [re.sub(r'_+', '_', col) for col in new_cols]

        # Remove leading/trailing underscores
        new_cols = [col.strip('_') for col in new_cols]

        # Ensure uniqueness
        seen = {}
        unique_cols = []
        for col in new_cols:
            if col in seen:
                seen[col] += 1
                unique_cols.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                unique_cols.append(col)

        df.columns = unique_cols

        if original_cols != unique_cols:
            report.add_action(f"Standardized {len(df.columns)} column names for Tableau compatibility")

        return df

    def _remove_empty_rows_cols(
        self,
        df: pd.DataFrame,
        report: CleaningReport
    ) -> pd.DataFrame:
        """Remove completely empty rows and columns"""
        initial_shape = df.shape

        # Remove rows where all values are null
        df = df.dropna(how='all')
        rows_removed = initial_shape[0] - len(df)

        # Remove columns where all values are null
        df = df.dropna(axis=1, how='all')
        cols_removed = initial_shape[1] - len(df.columns)

        if rows_removed > 0:
            report.add_action(f"Removed {rows_removed} completely empty rows")
        if cols_removed > 0:
            report.add_action(f"Removed {cols_removed} completely empty columns")

        return df

    def _remove_duplicates(
        self,
        df: pd.DataFrame,
        report: CleaningReport
    ) -> pd.DataFrame:
        """Remove duplicate rows"""
        initial_count = len(df)
        df = df.drop_duplicates()
        duplicates = initial_count - len(df)

        if duplicates > 0:
            report.duplicates_removed = duplicates
            report.add_action(f"Removed {duplicates} duplicate rows")

        return df

    def _convert_data_types(
        self,
        df: pd.DataFrame,
        report: CleaningReport
    ) -> pd.DataFrame:
        """Intelligently convert data types"""
        for col in df.columns:
            original_dtype = str(df[col].dtype)

            # Skip if already numeric or datetime
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                continue

            # Try datetime conversion
            if self._should_convert_to_datetime(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    report.type_conversions[col] = f"{original_dtype} -> datetime64"
                    report.add_action(f"Converted column '{col}' to datetime")
                    continue
                except:
                    pass

            # Try numeric conversion
            if self._should_convert_to_numeric(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    new_dtype = str(df[col].dtype)
                    report.type_conversions[col] = f"{original_dtype} -> {new_dtype}"
                    report.add_action(f"Converted column '{col}' to numeric")
                    continue
                except:
                    pass

        return df

    def _should_convert_to_datetime(self, series: pd.Series) -> bool:
        """Check if series should be converted to datetime"""
        # Sample non-null values
        sample = series.dropna().head(100)
        if len(sample) == 0:
            return False

        # Common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        ]

        match_count = 0
        for val in sample:
            val_str = str(val)
            if any(re.search(pattern, val_str) for pattern in date_patterns):
                match_count += 1

        confidence = match_count / len(sample)
        return confidence >= self.datetime_threshold

    def _should_convert_to_numeric(self, series: pd.Series) -> bool:
        """Check if series should be converted to numeric"""
        # Sample non-null values
        sample = series.dropna().head(100)
        if len(sample) == 0:
            return False

        # Try converting sample to numeric
        try:
            converted = pd.to_numeric(sample, errors='coerce')
            success_rate = converted.notna().sum() / len(sample)
            return success_rate >= self.numeric_threshold
        except:
            return False

    def _handle_missing_values(
        self,
        df: pd.DataFrame,
        report: CleaningReport,
        aggressive: bool = False
    ) -> pd.DataFrame:
        """Handle missing values intelligently"""
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count == 0:
                continue

            missing_pct = (missing_count / len(df)) * 100

            # If too many missing values and aggressive mode, drop column
            if aggressive and missing_pct > 50:
                df = df.drop(columns=[col])
                report.add_action(f"Dropped column '{col}' with {missing_pct:.1f}% missing values")
                continue

            # For numeric columns, consider filling with median
            if pd.api.types.is_numeric_dtype(df[col]):
                if missing_pct < 10:  # Only fill if less than 10% missing
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    report.missing_values_handled[col] = missing_count
                    report.add_action(f"Filled {missing_count} missing values in '{col}' with median ({median_val:.2f})")

            # For categorical columns, consider filling with mode
            elif df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
                if missing_pct < 5:  # Only fill if less than 5% missing
                    mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                    df[col] = df[col].fillna(mode_val)
                    report.missing_values_handled[col] = missing_count
                    report.add_action(f"Filled {missing_count} missing values in '{col}' with mode ('{mode_val}')")

        return df

    def _trim_whitespace(
        self,
        df: pd.DataFrame,
        report: CleaningReport
    ) -> pd.DataFrame:
        """Trim whitespace from string columns"""
        trimmed_cols = []

        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains strings
                sample = df[col].dropna().head(10)
                if len(sample) > 0 and all(isinstance(x, str) for x in sample):
                    df[col] = df[col].str.strip()
                    trimmed_cols.append(col)

        if trimmed_cols:
            report.add_action(f"Trimmed whitespace from {len(trimmed_cols)} string columns")

        return df

    def _cap_rows(
        self,
        df: pd.DataFrame,
        report: CleaningReport
    ) -> pd.DataFrame:
        """Cap rows for Tableau performance"""
        if len(df) > self.max_rows:
            original_count = len(df)
            df = df.head(self.max_rows)
            removed = original_count - len(df)
            report.add_action(
                f"Capped dataset at {self.max_rows:,} rows for Tableau performance "
                f"(removed {removed:,} rows)"
            )

        return df

    def _optimize_dtypes(
        self,
        df: pd.DataFrame,
        report: CleaningReport
    ) -> pd.DataFrame:
        """Optimize data types for memory efficiency"""
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB

        for col in df.columns:
            col_type = df[col].dtype

            # Optimize integers
            if pd.api.types.is_integer_dtype(df[col]):
                c_min = df[col].min()
                c_max = df[col].max()

                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)

            # Optimize floats
            elif pd.api.types.is_float_dtype(df[col]):
                df[col] = df[col].astype(np.float32)

            # Convert to category if low cardinality
            elif df[col].dtype == 'object':
                num_unique = df[col].nunique()
                num_total = len(df[col])
                if num_unique / num_total < 0.5:  # Less than 50% unique
                    df[col] = df[col].astype('category')

        new_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        memory_saved = original_memory - new_memory

        if memory_saved > 0.1:  # If saved more than 0.1 MB
            report.add_action(
                f"Optimized data types, reduced memory usage by {memory_saved:.2f} MB "
                f"({original_memory:.2f} MB -> {new_memory:.2f} MB)"
            )

        return df

    def detect_outliers(
        self,
        df: pd.DataFrame,
        multiplier: float = OUTLIER_IQR_MULTIPLIER
    ) -> Dict[str, pd.Series]:
        """
        Detect outliers using IQR method

        Args:
            df: DataFrame to analyze
            multiplier: IQR multiplier for outlier detection

        Returns:
            Dictionary mapping column names to boolean series indicating outliers
        """
        outliers = {}

        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR

            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)

            if outlier_mask.sum() > 0:
                outliers[col] = outlier_mask

        return outliers

    def remove_outliers(
        self,
        df: pd.DataFrame,
        report: CleaningReport,
        multiplier: float = OUTLIER_IQR_MULTIPLIER
    ) -> pd.DataFrame:
        """Remove outliers from DataFrame"""
        outliers = self.detect_outliers(df, multiplier)

        if not outliers:
            return df

        # Create combined mask (remove row if ANY column has outlier)
        combined_mask = pd.Series([False] * len(df), index=df.index)
        for col, outlier_mask in outliers.items():
            combined_mask |= outlier_mask
            report.outliers_detected[col] = outlier_mask.sum()

        initial_count = len(df)
        df = df[~combined_mask]
        removed_count = initial_count - len(df)

        if removed_count > 0:
            report.add_action(
                f"Removed {removed_count} outlier rows across {len(outliers)} columns"
            )

        return df


def generate_cleaning_summary(report: CleaningReport) -> str:
    """
    Generate human-readable cleaning summary

    Args:
        report: CleaningReport to summarize

    Returns:
        Formatted string summary
    """
    summary_lines = [
        "### Data Cleaning Summary",
        "",
        f"**Original Shape:** {report.original_shape[0]:,} rows × {report.original_shape[1]} columns",
        f"**Cleaned Shape:** {report.cleaned_shape[0]:,} rows × {report.cleaned_shape[1]} columns",
        ""
    ]

    if report.rows_removed > 0:
        summary_lines.append(f"- Removed {report.rows_removed:,} rows")
    if report.columns_removed > 0:
        summary_lines.append(f"- Removed {report.columns_removed} columns")
    if report.duplicates_removed > 0:
        summary_lines.append(f"- Removed {report.duplicates_removed:,} duplicate rows")

    if report.type_conversions:
        summary_lines.append(f"\n**Type Conversions:** {len(report.type_conversions)}")
        for col, conversion in list(report.type_conversions.items())[:5]:
            summary_lines.append(f"  - {col}: {conversion}")
        if len(report.type_conversions) > 5:
            summary_lines.append(f"  - ... and {len(report.type_conversions) - 5} more")

    if report.missing_values_handled:
        total_filled = sum(report.missing_values_handled.values())
        summary_lines.append(f"\n**Missing Values Filled:** {total_filled:,} across {len(report.missing_values_handled)} columns")

    if report.outliers_detected:
        total_outliers = sum(report.outliers_detected.values())
        summary_lines.append(f"\n**Outliers Detected:** {total_outliers:,} across {len(report.outliers_detected)} columns")

    if report.actions:
        summary_lines.append(f"\n**Actions Performed:** {len(report.actions)}")
        for action in report.actions:
            summary_lines.append(f"  - {action}")

    return "\n".join(summary_lines)
