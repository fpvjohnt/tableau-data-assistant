"""
Unit tests for privacy module
"""

import pytest
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.privacy import (
    PIIDetector,
    PIIMasker,
    DataMinimizer,
    mask_pii_dataframe,
    PIIReport
)


@pytest.fixture
def df_with_pii():
    """DataFrame containing PII"""
    return pd.DataFrame({
        'customer_id': [1, 2, 3],
        'email': ['alice@example.com', 'bob@test.com', 'charlie@demo.com'],
        'phone': ['555-123-4567', '555-987-6543', '555-456-7890'],
        'revenue': [1000, 2000, 1500]
    })


@pytest.fixture
def df_without_pii():
    """Clean DataFrame without PII"""
    return pd.DataFrame({
        'product_id': [1, 2, 3],
        'category': ['A', 'B', 'C'],
        'price': [10.99, 20.99, 15.99]
    })


class TestPIIDetector:
    """Test PII detection"""

    def test_detect_email_column(self, df_with_pii):
        """Test detection of email column by name"""
        detector = PIIDetector()
        report = detector.detect_pii_columns(df_with_pii)

        assert 'email' in report.detected_columns
        assert report.detection_method['email'] in ['keyword_match', 'email_pattern']

    def test_detect_phone_column(self, df_with_pii):
        """Test detection of phone column"""
        detector = PIIDetector()
        report = detector.detect_pii_columns(df_with_pii)

        assert 'phone' in report.detected_columns

    def test_no_pii_detected(self, df_without_pii):
        """Test no false positives on clean data"""
        detector = PIIDetector()
        report = detector.detect_pii_columns(df_without_pii)

        assert len(report.detected_columns) == 0


class TestPIIMasker:
    """Test PII masking"""

    def test_partial_mask(self, df_with_pii):
        """Test partial masking"""
        masker = PIIMasker()
        df_masked, report = masker.mask_dataframe(df_with_pii, method='partial')

        # Email should be partially masked
        assert df_masked['email'][0] != df_with_pii['email'][0]
        assert 'email' in report.masked_columns

    def test_full_mask(self, df_with_pii):
        """Test full masking"""
        masker = PIIMasker()
        df_masked, report = masker.mask_dataframe(
            df_with_pii,
            pii_columns=['email'],
            method='full'
        )

        # Should be fully masked
        assert all('*' in str(val) for val in df_masked['email'])

    def test_hash_mask(self, df_with_pii):
        """Test hash masking"""
        masker = PIIMasker()
        df_masked, report = masker.mask_dataframe(
            df_with_pii,
            pii_columns=['email'],
            method='hash'
        )

        # Should be hashed (16 char hex string)
        assert len(df_masked['email'][0]) == 16
        assert df_masked['email'][0] != df_with_pii['email'][0]

    def test_remove_pii(self, df_with_pii):
        """Test PII column removal"""
        masker = PIIMasker()
        df_masked, report = masker.mask_dataframe(
            df_with_pii,
            pii_columns=['email', 'phone'],
            method='remove'
        )

        assert 'email' not in df_masked.columns
        assert 'phone' not in df_masked.columns
        assert 'revenue' in df_masked.columns

    def test_mask_email_format(self):
        """Test email masking preserves domain"""
        masker = PIIMasker()
        masked = masker.mask_email('john.doe@example.com')

        assert '@example.com' in masked
        assert 'john.doe' not in masked

    def test_mask_phone_format(self):
        """Test phone masking shows last 4 digits"""
        masker = PIIMasker()
        masked = masker.mask_phone('555-123-4567')

        assert '4567' in masked
        assert '555' not in masked


class TestDataMinimizer:
    """Test data minimization"""

    def test_row_limit(self):
        """Test row limiting"""
        large_df = pd.DataFrame({
            'id': range(1000),
            'value': range(1000)
        })

        minimizer = DataMinimizer(max_rows=10)
        df_mini, metadata = minimizer.minimize_for_ai(large_df)

        assert len(df_mini) == 10
        assert metadata['original_shape'] == (1000, 2)
        assert metadata['minimized_shape'] == (10, 2)

    def test_sampling_methods(self):
        """Test different sampling methods"""
        df = pd.DataFrame({
            'id': range(100),
            'value': range(100)
        })

        minimizer = DataMinimizer(max_rows=10)

        # Head
        df_head, _ = minimizer.minimize_for_ai(df, sample_method='head')
        assert df_head['id'][0] == 0

        # Tail
        df_tail, _ = minimizer.minimize_for_ai(df, sample_method='tail')
        assert df_tail['id'].iloc[-1] == 99

        # Random
        df_random, _ = minimizer.minimize_for_ai(df, sample_method='random')
        assert len(df_random) == 10

    def test_auto_pii_masking(self, df_with_pii):
        """Test automatic PII masking during minimization"""
        minimizer = DataMinimizer(max_rows=10)
        df_mini, metadata = minimizer.minimize_for_ai(
            df_with_pii,
            auto_mask_pii=True
        )

        assert metadata['pii_masked'] is True
        assert 'pii_columns' in metadata


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_mask_pii_dataframe(self, df_with_pii):
        """Test one-line masking function"""
        df_masked, report = mask_pii_dataframe(df_with_pii, method='partial')

        assert isinstance(report, PIIReport)
        assert len(report.detected_columns) > 0
        assert df_masked.shape == df_with_pii.shape


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
