"""
Unit tests for cleaning module
"""

import pytest
import pandas as pd
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cleaning import (
    DataCleaner,
    CleaningReport,
    generate_cleaning_summary
)


@pytest.fixture
def messy_df():
    """DataFrame with various data quality issues"""
    return pd.DataFrame({
        'ID  ': [1, 2, 3, 3, 5],  # Spaces in column name, duplicate
        'Name ': ['  Alice  ', 'Bob', 'Charlie', 'Charlie', 'David'],  # Whitespace
        'Age': [25, None, 35, 35, 45],
        'Salary': ['50000', '60000', 'invalid', '70000', '80000']  # Mixed types
    })


class TestDataCleaner:
    """Test DataCleaner class"""

    def test_auto_clean(self, messy_df):
        """Test automatic cleaning"""
        cleaner = DataCleaner()
        df_clean, report = cleaner.auto_clean_df(messy_df)

        assert isinstance(report, CleaningReport)
        assert report.original_shape == messy_df.shape
        assert len(report.actions) > 0

    def test_standardize_column_names(self, messy_df):
        """Test column name standardization"""
        cleaner = DataCleaner()
        df_clean, report = cleaner.auto_clean_df(messy_df)

        # Column names should be cleaned
        assert 'ID' in df_clean.columns or 'ID_' in df_clean.columns
        assert all(not col.endswith(' ') for col in df_clean.columns)

    def test_remove_duplicates(self, messy_df):
        """Test duplicate removal"""
        cleaner = DataCleaner()
        df_clean, report = cleaner.auto_clean_df(messy_df)

        # Should remove duplicate row
        assert report.duplicates_removed > 0
        assert len(df_clean) < len(messy_df)

    def test_trim_whitespace(self):
        """Test whitespace trimming"""
        df = pd.DataFrame({
            'text': ['  hello  ', '  world  ', '  test  ']
        })

        cleaner = DataCleaner()
        df_clean, report = cleaner.auto_clean_df(df)

        assert df_clean['text'][0] == 'hello'
        assert df_clean['text'][1] == 'world'

    def test_remove_empty_rows_cols(self):
        """Test empty row/column removal"""
        df = pd.DataFrame({
            'a': [1, 2, None, 4],
            'b': [None, None, None, None],  # All null
            'c': [5, 6, 7, 8]
        })

        cleaner = DataCleaner()
        df_clean, report = cleaner.auto_clean_df(df)

        # Column 'b' should be removed
        assert 'b' not in df_clean.columns

    def test_cap_rows(self):
        """Test row capping for Tableau performance"""
        large_df = pd.DataFrame({
            'id': range(2000000),
            'value': range(2000000)
        })

        cleaner = DataCleaner(max_rows=1000000)
        df_clean, report = cleaner.auto_clean_df(large_df)

        assert len(df_clean) <= 1000000

    def test_detect_outliers(self):
        """Test outlier detection"""
        df = pd.DataFrame({
            'value': [10, 12, 11, 13, 100]  # 100 is outlier
        })

        cleaner = DataCleaner()
        outliers = cleaner.detect_outliers(df)

        assert 'value' in outliers
        assert outliers['value'][4] is True  # 100 is outlier

    def test_remove_outliers(self):
        """Test outlier removal"""
        df = pd.DataFrame({
            'value': [10, 12, 11, 13, 100]
        })

        cleaner = DataCleaner()
        report = CleaningReport(original_shape=df.shape)
        df_clean = cleaner.remove_outliers(df, report)

        assert len(df_clean) < len(df)
        assert 100 not in df_clean['value'].values


class TestCleaningReport:
    """Test CleaningReport dataclass"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
        report = CleaningReport(
            original_shape=(100, 10),
            cleaned_shape=(95, 9),
            duplicates_removed=5
        )

        report_dict = report.to_dict()

        assert report_dict['original_shape'] == (100, 10)
        assert report_dict['cleaned_shape'] == (95, 9)
        assert report_dict['duplicates_removed'] == 5


class TestConvenienceFunctions:
    """Test utility functions"""

    def test_generate_cleaning_summary(self, messy_df):
        """Test summary generation"""
        cleaner = DataCleaner()
        df_clean, report = cleaner.auto_clean_df(messy_df)

        summary = generate_cleaning_summary(report)

        assert isinstance(summary, str)
        assert 'Data Cleaning Summary' in summary
        assert 'Original Shape' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
