"""
Data validation module using Pandera for schema-based validation
Provides deterministic data quality checks for Tableau data imports
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np

try:
    import pandera as pa
    from pandera import Column, DataFrameSchema, Check
    PANDERA_AVAILABLE = True
except ImportError:
    PANDERA_AVAILABLE = False
    pa = None
    Column = None
    DataFrameSchema = None
    Check = None

from config.settings import NULL_THRESHOLD_PERCENT, UNIQUENESS_THRESHOLD, VALIDATION_SAMPLE_SIZE


@dataclass
class ValidationResult:
    """Results from data validation"""
    passed: bool
    schema_name: Optional[str] = None
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'passed': self.passed,
            'schema_name': self.schema_name,
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'warnings': self.warnings,
            'errors': self.errors,
            'issues': self.issues,
            'summary': self.summary,
            'timestamp': self.timestamp.isoformat()
        }


class DataValidator:
    """Schema-based data validator for Tableau imports"""

    def __init__(self, null_threshold: float = NULL_THRESHOLD_PERCENT):
        """
        Initialize validator

        Args:
            null_threshold: Maximum percentage of nulls allowed per column
        """
        self.null_threshold = null_threshold

    def infer_schema(self, df: pd.DataFrame, sample_size: int = VALIDATION_SAMPLE_SIZE) -> Dict[str, Any]:
        """
        Infer schema from DataFrame

        Args:
            df: DataFrame to analyze
            sample_size: Number of rows to sample for inference

        Returns:
            Dictionary describing the inferred schema
        """
        # Sample if needed
        sample_df = df.sample(min(sample_size, len(df))) if len(df) > sample_size else df

        schema = {
            'columns': {},
            'row_count': len(df),
            'column_count': len(df.columns),
            'inferred_at': datetime.now().isoformat()
        }

        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'nullable': df[col].isnull().any(),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': float((df[col].isnull().sum() / len(df)) * 100),
                'unique_count': int(df[col].nunique()),
                'unique_percentage': float((df[col].nunique() / len(df)) * 100)
            }

            # Add type-specific info
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    'min': float(df[col].min()) if not df[col].isnull().all() else None,
                    'max': float(df[col].max()) if not df[col].isnull().all() else None,
                    'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                    'median': float(df[col].median()) if not df[col].isnull().all() else None
                })
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_info.update({
                    'min_date': df[col].min().isoformat() if not df[col].isnull().all() else None,
                    'max_date': df[col].max().isoformat() if not df[col].isnull().all() else None
                })
            elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object':
                # Get sample values
                sample_values = df[col].dropna().unique()[:10].tolist()
                col_info['sample_values'] = [str(v) for v in sample_values]
                col_info['max_length'] = int(df[col].astype(str).str.len().max()) if not df[col].isnull().all() else 0

            schema['columns'][col] = col_info

        return schema

    def validate_df(
        self,
        df: pd.DataFrame,
        schema: Optional[Dict[str, Any]] = None,
        checks_config: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate DataFrame against schema and quality checks

        Args:
            df: DataFrame to validate
            schema: Optional schema dictionary (if None, will infer)
            checks_config: Optional configuration for specific checks

        Returns:
            ValidationResult with details of validation
        """
        result = ValidationResult(passed=True)  # Will be set to False if any checks fail

        # Infer schema if not provided
        if schema is None:
            schema = self.infer_schema(df)
            result.schema_name = "inferred"
        else:
            result.schema_name = schema.get('name', 'custom')

        checks_config = checks_config or {}

        # Run validation checks
        self._check_required_columns(df, schema, result, checks_config)
        self._check_data_types(df, schema, result)
        self._check_null_thresholds(df, schema, result)
        self._check_uniqueness(df, schema, result, checks_config)
        self._check_value_ranges(df, schema, result, checks_config)
        self._check_duplicates(df, result)

        # Calculate summary
        result.total_checks = result.passed_checks + result.failed_checks
        result.passed = result.failed_checks == 0
        result.summary = {
            'pass_rate': (result.passed_checks / result.total_checks * 100) if result.total_checks > 0 else 0,
            'total_issues': len(result.errors) + len(result.warnings),
            'critical_issues': len(result.errors),
            'warnings': len(result.warnings)
        }

        return result

    def _check_required_columns(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        result: ValidationResult,
        checks_config: Dict[str, Any]
    ):
        """Check if required columns are present"""
        required_cols = checks_config.get('required_columns', [])

        for col in required_cols:
            if col in df.columns:
                result.passed_checks += 1
            else:
                result.failed_checks += 1
                result.errors.append({
                    'check': 'required_column',
                    'column': col,
                    'severity': 'error',
                    'message': f"Required column '{col}' is missing"
                })

    def _check_data_types(self, df: pd.DataFrame, schema: Dict[str, Any], result: ValidationResult):
        """Validate data types match expected types"""
        for col in df.columns:
            if col in schema.get('columns', {}):
                expected_dtype = schema['columns'][col].get('dtype')
                actual_dtype = str(df[col].dtype)

                # Normalize dtype strings for comparison
                if expected_dtype and not self._dtypes_match(expected_dtype, actual_dtype):
                    result.failed_checks += 1
                    result.warnings.append({
                        'check': 'data_type',
                        'column': col,
                        'severity': 'warning',
                        'expected': expected_dtype,
                        'actual': actual_dtype,
                        'message': f"Column '{col}' type mismatch: expected {expected_dtype}, got {actual_dtype}"
                    })
                else:
                    result.passed_checks += 1

    def _check_null_thresholds(self, df: pd.DataFrame, schema: Dict[str, Any], result: ValidationResult):
        """Check if null percentages are within acceptable thresholds"""
        for col in df.columns:
            null_pct = (df[col].isnull().sum() / len(df)) * 100

            if null_pct > self.null_threshold:
                result.failed_checks += 1
                result.errors.append({
                    'check': 'null_threshold',
                    'column': col,
                    'severity': 'error',
                    'null_percentage': round(null_pct, 2),
                    'threshold': self.null_threshold,
                    'message': f"Column '{col}' exceeds null threshold: {null_pct:.1f}% (max: {self.null_threshold}%)"
                })
            else:
                result.passed_checks += 1

    def _check_uniqueness(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        result: ValidationResult,
        checks_config: Dict[str, Any]
    ):
        """Check uniqueness constraints"""
        unique_cols = checks_config.get('unique_columns', [])

        for col in unique_cols:
            if col not in df.columns:
                continue

            unique_pct = (df[col].nunique() / len(df)) * 100

            if unique_pct < UNIQUENESS_THRESHOLD:
                result.failed_checks += 1
                result.warnings.append({
                    'check': 'uniqueness',
                    'column': col,
                    'severity': 'warning',
                    'unique_percentage': round(unique_pct, 2),
                    'threshold': UNIQUENESS_THRESHOLD,
                    'message': f"Column '{col}' uniqueness below threshold: {unique_pct:.1f}% (expected: {UNIQUENESS_THRESHOLD}%)"
                })
            else:
                result.passed_checks += 1

    def _check_value_ranges(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        result: ValidationResult,
        checks_config: Dict[str, Any]
    ):
        """Check if values are within expected ranges"""
        range_checks = checks_config.get('value_ranges', {})

        for col, range_spec in range_checks.items():
            if col not in df.columns:
                continue

            if not pd.api.types.is_numeric_dtype(df[col]):
                continue

            min_val = range_spec.get('min')
            max_val = range_spec.get('max')

            if min_val is not None:
                violations = (df[col] < min_val).sum()
                if violations > 0:
                    result.failed_checks += 1
                    result.errors.append({
                        'check': 'value_range',
                        'column': col,
                        'severity': 'error',
                        'violations': int(violations),
                        'min_value': min_val,
                        'message': f"Column '{col}' has {violations} values below minimum {min_val}"
                    })
                else:
                    result.passed_checks += 1

            if max_val is not None:
                violations = (df[col] > max_val).sum()
                if violations > 0:
                    result.failed_checks += 1
                    result.errors.append({
                        'check': 'value_range',
                        'column': col,
                        'severity': 'error',
                        'violations': int(violations),
                        'max_value': max_val,
                        'message': f"Column '{col}' has {violations} values above maximum {max_val}"
                    })
                else:
                    result.passed_checks += 1

    def _check_duplicates(self, df: pd.DataFrame, result: ValidationResult):
        """Check for duplicate rows"""
        duplicate_count = df.duplicated().sum()

        if duplicate_count > 0:
            dup_pct = (duplicate_count / len(df)) * 100
            result.warnings.append({
                'check': 'duplicates',
                'severity': 'warning',
                'count': int(duplicate_count),
                'percentage': round(dup_pct, 2),
                'message': f"Found {duplicate_count} duplicate rows ({dup_pct:.1f}% of data)"
            })
            result.failed_checks += 1
        else:
            result.passed_checks += 1

    def _dtypes_match(self, dtype1: str, dtype2: str) -> bool:
        """Check if two dtype strings match (with normalization)"""
        # Normalize dtype strings
        dtype1 = dtype1.lower().replace(' ', '')
        dtype2 = dtype2.lower().replace(' ', '')

        # Check for exact match
        if dtype1 == dtype2:
            return True

        # Check for compatible types
        numeric_types = ['int', 'int32', 'int64', 'float', 'float32', 'float64', 'number']
        string_types = ['object', 'string', 'str']
        datetime_types = ['datetime', 'datetime64', 'timestamp']

        if any(t in dtype1 for t in numeric_types) and any(t in dtype2 for t in numeric_types):
            return True
        if any(t in dtype1 for t in string_types) and any(t in dtype2 for t in string_types):
            return True
        if any(t in dtype1 for t in datetime_types) and any(t in dtype2 for t in datetime_types):
            return True

        return False


def generate_validation_report(df: pd.DataFrame, validation_result: ValidationResult) -> Dict[str, Any]:
    """
    Generate comprehensive validation report

    Args:
        df: Original DataFrame
        validation_result: Result from validation

    Returns:
        Dictionary containing detailed validation report
    """
    report = {
        'validation_summary': {
            'status': 'PASSED' if validation_result.passed else 'FAILED',
            'total_checks': validation_result.total_checks,
            'passed_checks': validation_result.passed_checks,
            'failed_checks': validation_result.failed_checks,
            'pass_rate': validation_result.summary.get('pass_rate', 0),
            'timestamp': validation_result.timestamp.isoformat()
        },
        'data_summary': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        },
        'issues': {
            'errors': validation_result.errors,
            'warnings': validation_result.warnings,
            'total_issues': len(validation_result.errors) + len(validation_result.warnings)
        },
        'recommendations': _generate_recommendations(validation_result)
    }

    return report


def _generate_recommendations(validation_result: ValidationResult) -> List[str]:
    """Generate actionable recommendations based on validation results"""
    recommendations = []

    # Check for high null percentages
    null_issues = [e for e in validation_result.errors if e.get('check') == 'null_threshold']
    if null_issues:
        recommendations.append(
            f"Address {len(null_issues)} columns with excessive missing values. "
            "Consider imputation, dropping columns, or collecting more complete data."
        )

    # Check for duplicates
    dup_issues = [w for w in validation_result.warnings if w.get('check') == 'duplicates']
    if dup_issues:
        dup_count = dup_issues[0].get('count', 0)
        recommendations.append(
            f"Remove {dup_count} duplicate rows before importing to Tableau for better performance."
        )

    # Check for type mismatches
    type_issues = [w for w in validation_result.warnings if w.get('check') == 'data_type']
    if type_issues:
        recommendations.append(
            f"Correct data type mismatches in {len(type_issues)} columns to ensure proper Tableau field types."
        )

    # Check for range violations
    range_issues = [e for e in validation_result.errors if e.get('check') == 'value_range']
    if range_issues:
        recommendations.append(
            f"Investigate {len(range_issues)} columns with out-of-range values for data quality issues."
        )

    if not recommendations:
        recommendations.append("Data quality looks good! Ready for Tableau import.")

    return recommendations


# Convenience function
def validate_for_tableau(
    df: pd.DataFrame,
    required_columns: Optional[List[str]] = None,
    unique_columns: Optional[List[str]] = None,
    value_ranges: Optional[Dict[str, Dict[str, float]]] = None
) -> Tuple[ValidationResult, Dict[str, Any]]:
    """
    Validate DataFrame for Tableau import with common checks

    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        unique_columns: List of columns that should be unique
        value_ranges: Dictionary of {column: {'min': val, 'max': val}}

    Returns:
        Tuple of (ValidationResult, validation_report)
    """
    validator = DataValidator()

    checks_config = {
        'required_columns': required_columns or [],
        'unique_columns': unique_columns or [],
        'value_ranges': value_ranges or {}
    }

    result = validator.validate_df(df, checks_config=checks_config)
    report = generate_validation_report(df, result)

    return result, report
