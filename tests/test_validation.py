"""
Unit tests for validation module
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validation import (
    DataValidator,
    ValidationResult,
    validate_for_tableau,
    generate_validation_report
)


@pytest.fixture
def sample_df():
    """Create sample DataFrame for testing"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'department': ['Sales', 'IT', 'Sales', 'HR', 'IT']
    })


@pytest.fixture
def df_with_nulls():
    """DataFrame with missing values"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'value': [100, None, 300, None, 500],
        'category': ['A', 'B', None, 'D', 'E']
    })


@pytest.fixture
def df_with_duplicates():
    """DataFrame with duplicate rows"""
    return pd.DataFrame({
        'id': [1, 2, 3, 2, 4],
        'name': ['A', 'B', 'C', 'B', 'D']
    })


class TestDataValidator:
    """Test DataValidator class"""

    def test_infer_schema(self, sample_df):
        """Test schema inference"""
        validator = DataValidator()
        schema = validator.infer_schema(sample_df)

        assert 'columns' in schema
        assert 'row_count' in schema
        assert 'column_count' in schema
        assert schema['row_count'] == 5
        assert schema['column_count'] == 5
        assert 'id' in schema['columns']
        assert 'name' in schema['columns']

    def test_validate_clean_df(self, sample_df):
        """Test validation of clean DataFrame"""
        validator = DataValidator()
        result = validator.validate_df(sample_df)

        assert isinstance(result, ValidationResult)
        assert result.passed
        assert result.failed_checks == 0

    def test_validate_nulls(self, df_with_nulls):
        """Test null threshold validation"""
        validator = DataValidator(null_threshold=30.0)  # 30% threshold
        result = validator.validate_df(df_with_nulls)

        # 'value' column has 40% nulls, should fail
        assert result.failed_checks > 0
        assert any('value' in str(error) for error in result.errors)

    def test_validate_duplicates(self, df_with_duplicates):
        """Test duplicate detection"""
        validator = DataValidator()
        result = validator.validate_df(df_with_duplicates)

        # Should have warnings about duplicates
        assert len(result.warnings) > 0 or len(result.errors) > 0

    def test_required_columns(self, sample_df):
        """Test required columns check"""
        validator = DataValidator()
        checks_config = {
            'required_columns': ['id', 'name', 'missing_column']
        }

        result = validator.validate_df(sample_df, checks_config=checks_config)

        assert result.failed_checks > 0
        assert any('missing_column' in str(error) for error in result.errors)

    def test_value_ranges(self, sample_df):
        """Test value range validation"""
        validator = DataValidator()
        checks_config = {
            'value_ranges': {
                'age': {'min': 0, 'max': 100},
                'salary': {'min': 0, 'max': 50000}  # Should fail
            }
        }

        result = validator.validate_df(sample_df, checks_config=checks_config)

        # Salary has values > 50000, should fail
        assert result.failed_checks > 0


class TestValidationResult:
    """Test ValidationResult dataclass"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
        result = ValidationResult(
            passed=True,
            total_checks=10,
            passed_checks=10,
            failed_checks=0
        )

        result_dict = result.to_dict()

        assert result_dict['passed'] is True
        assert result_dict['total_checks'] == 10
        assert 'timestamp' in result_dict


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_validate_for_tableau(self, sample_df):
        """Test validate_for_tableau function"""
        result, report = validate_for_tableau(
            sample_df,
            required_columns=['id', 'name'],
            unique_columns=['id']
        )

        assert isinstance(result, ValidationResult)
        assert isinstance(report, dict)
        assert 'validation_summary' in report
        assert 'data_summary' in report

    def test_generate_validation_report(self, sample_df):
        """Test report generation"""
        validator = DataValidator()
        validation_result = validator.validate_df(sample_df)

        report = generate_validation_report(sample_df, validation_result)

        assert isinstance(report, dict)
        assert 'validation_summary' in report
        assert 'recommendations' in report


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
