"""
Unit tests for data quality scoring
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils.data_quality import DataQualityScorer, calculate_quality_score


class TestDataQualityScorer:
    """Test suite for DataQualityScorer"""

    def test_perfect_quality_data(self):
        """Test data with perfect quality scores"""
        df = pd.DataFrame({
            'A': range(100),
            'B': np.random.randn(100),
            'C': ['category' + str(i % 5) for i in range(100)]
        })

        result = calculate_quality_score(df)

        assert result['overall_score'] >= 85
        assert result['grade'] in ['A', 'B']
        assert result['dimension_scores']['completeness'] == 100.0
        assert result['dimension_scores']['uniqueness'] == 100.0

    def test_missing_values_impact(self):
        """Test that missing values reduce completeness score"""
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5] * 20,
            'B': [np.nan] * 50 + list(range(50)),
            'C': range(100)
        })

        result = calculate_quality_score(df)

        assert result['dimension_scores']['completeness'] < 100.0
        assert 'missing' in str(result['details']['completeness']).lower()
        assert len(result['recommendations']) > 0

    def test_duplicate_detection(self):
        """Test that duplicates reduce uniqueness score"""
        df = pd.DataFrame({
            'A': [1, 1, 1, 2, 2, 3],
            'B': [1, 1, 1, 2, 2, 3]
        })

        result = calculate_quality_score(df)

        assert result['dimension_scores']['uniqueness'] < 100.0
        assert result['details']['uniqueness']['duplicate_rows'] == 4

    def test_outlier_detection(self):
        """Test outlier detection in consistency score"""
        # Create data with obvious outliers
        normal_data = list(np.random.randn(95) * 10 + 50)
        outliers = [1000, -1000, 999, -999, 998]  # Clear outliers

        df = pd.DataFrame({
            'values': normal_data + outliers
        })

        result = calculate_quality_score(df)

        assert result['dimension_scores']['consistency'] < 100.0
        assert result['details']['consistency']['total_outliers'] >= 5

    def test_timeliness_with_old_dates(self):
        """Test timeliness score with old dates"""
        old_dates = [datetime.now() - timedelta(days=400 + i) for i in range(100)]

        df = pd.DataFrame({
            'date_column': pd.to_datetime(old_dates),
            'value': range(100)
        })

        result = calculate_quality_score(df)

        # Old data should have lower timeliness score
        assert result['dimension_scores']['timeliness'] < 80

    def test_timeliness_with_current_dates(self):
        """Test timeliness score with current dates"""
        recent_dates = [datetime.now() - timedelta(days=i) for i in range(100)]

        df = pd.DataFrame({
            'date_column': pd.to_datetime(recent_dates),
            'value': range(100)
        })

        result = calculate_quality_score(df)

        # Recent data should have high timeliness score
        assert result['dimension_scores']['timeliness'] >= 80

    def test_validity_with_inf_values(self):
        """Test validity detection of infinite values"""
        df = pd.DataFrame({
            'A': [1, 2, 3, np.inf, 5, -np.inf, 7, 8, 9, 10]
        })

        result = calculate_quality_score(df)

        # Should detect inf values as validity issue
        assert len(result['details']['validity']['issues']) > 0

    def test_empty_dataframe(self):
        """Test handling of empty dataframe"""
        df = pd.DataFrame()

        result = calculate_quality_score(df)

        # Should handle gracefully
        assert 'overall_score' in result
        assert result['grade'] is not None

    def test_single_column_dataframe(self):
        """Test handling of single column"""
        df = pd.DataFrame({'A': range(100)})

        result = calculate_quality_score(df)

        assert result['overall_score'] >= 0
        assert result['overall_score'] <= 100

    def test_all_null_column(self):
        """Test handling of completely null column"""
        df = pd.DataFrame({
            'all_null': [np.nan] * 100,
            'some_data': range(100)
        })

        result = calculate_quality_score(df)

        assert result['dimension_scores']['completeness'] < 100.0

    def test_recommendation_generation(self):
        """Test that recommendations are generated"""
        # Create data with multiple quality issues
        df = pd.DataFrame({
            'A': [1, 1, 1, np.nan, np.nan],
            'B': [1, 2, 3, 4, 5],
            'C': [1, 2, 3, 4, 5]
        })

        result = calculate_quality_score(df)

        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0

    def test_grade_assignment(self):
        """Test that grade is assigned correctly"""
        # Perfect data should get A
        df_perfect = pd.DataFrame({
            'A': range(100),
            'B': range(100)
        })

        result = calculate_quality_score(df_perfect)
        assert result['grade'] in ['A', 'B']

        # Poor data should get lower grade
        df_poor = pd.DataFrame({
            'A': [np.nan] * 100,
            'B': [1, 1, 1, 1, 1] * 20
        })

        result_poor = calculate_quality_score(df_poor)
        assert result_poor['grade'] in ['C', 'D', 'F']


class TestDataQualityScorerEdgeCases:
    """Test edge cases and error handling"""

    def test_very_large_dataframe(self):
        """Test performance with large dataframe"""
        df = pd.DataFrame({
            'A': range(100000),
            'B': np.random.randn(100000)
        })

        result = calculate_quality_score(df)

        assert result is not None
        assert 'overall_score' in result

    def test_many_columns(self):
        """Test with many columns"""
        data = {f'col_{i}': range(100) for i in range(50)}
        df = pd.DataFrame(data)

        result = calculate_quality_score(df)

        assert result['dimension_scores']['completeness'] == 100.0

    def test_mixed_data_types(self):
        """Test with mixed data types"""
        df = pd.DataFrame({
            'int_col': range(100),
            'float_col': np.random.randn(100),
            'str_col': ['text'] * 100,
            'date_col': pd.date_range('2024-01-01', periods=100),
            'bool_col': [True, False] * 50
        })

        result = calculate_quality_score(df)

        assert result['overall_score'] >= 0
        assert result['overall_score'] <= 100

    def test_unicode_strings(self):
        """Test handling of unicode characters"""
        df = pd.DataFrame({
            'unicode_col': ['Hello 世界', 'Привет', '🎉', 'Café'] * 25,
            'value': range(100)
        })

        result = calculate_quality_score(df)

        assert result is not None

    def test_special_numeric_values(self):
        """Test handling of special numeric values"""
        df = pd.DataFrame({
            'A': [0, -0, 1e-10, 1e10, np.nan, np.inf, -np.inf]
        })

        result = calculate_quality_score(df)

        assert result['dimension_scores']['validity'] < 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
