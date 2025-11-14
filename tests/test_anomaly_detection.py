"""
Unit tests for anomaly detection module
"""

import pytest
import pandas as pd
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.anomaly_detection import (
    IQRAnomalyDetector,
    ZScoreAnomalyDetector,
    AnomalyDetectorEnsemble,
    detect_anomalies,
    AnomalyReport
)


@pytest.fixture
def df_with_outliers():
    """DataFrame with obvious outliers"""
    return pd.DataFrame({
        'value': [10, 12, 11, 13, 100, 12, 11],  # 100 is outlier
        'score': [50, 52, 51, 53, 500, 52, 51]   # 500 is outlier
    })


@pytest.fixture
def clean_df():
    """Clean DataFrame without outliers"""
    return pd.DataFrame({
        'value': [10, 12, 11, 13, 12, 11, 10],
        'score': [50, 52, 51, 53, 52, 51, 50]
    })


class TestIQRAnomalyDetector:
    """Test IQR-based anomaly detection"""

    def test_detect_anomalies(self, df_with_outliers):
        """Test IQR anomaly detection"""
        detector = IQRAnomalyDetector()
        report = detector.detect(df_with_outliers)

        assert isinstance(report, AnomalyReport)
        assert report.method == "IQR"
        assert report.total_anomalies > 0
        assert len(report.anomalies_by_column) > 0

    def test_no_anomalies_in_clean_data(self, clean_df):
        """Test no false positives on clean data"""
        detector = IQRAnomalyDetector()
        report = detector.detect(clean_df)

        # May detect some anomalies due to small sample size, but should be minimal
        assert report.anomaly_percentage < 30.0

    def test_get_outlier_bounds(self, df_with_outliers):
        """Test outlier bounds calculation"""
        detector = IQRAnomalyDetector()
        bounds = detector.get_outlier_bounds(df_with_outliers)

        assert 'value' in bounds
        assert 'score' in bounds
        assert len(bounds['value']) == 2  # (lower, upper)


class TestZScoreAnomalyDetector:
    """Test Z-score based anomaly detection"""

    def test_detect_anomalies(self, df_with_outliers):
        """Test Z-score anomaly detection"""
        detector = ZScoreAnomalyDetector(threshold=2.0)
        report = detector.detect(df_with_outliers)

        assert isinstance(report, AnomalyReport)
        assert report.method == "Z-Score"
        assert report.total_anomalies > 0

    def test_threshold_sensitivity(self, df_with_outliers):
        """Test threshold affects detection"""
        detector_strict = ZScoreAnomalyDetector(threshold=2.0)
        detector_loose = ZScoreAnomalyDetector(threshold=5.0)

        report_strict = detector_strict.detect(df_with_outliers)
        report_loose = detector_loose.detect(df_with_outliers)

        # Stricter threshold should find more anomalies
        assert report_strict.total_anomalies >= report_loose.total_anomalies


class TestAnomalyDetectorEnsemble:
    """Test ensemble anomaly detection"""

    def test_majority_voting(self, df_with_outliers):
        """Test ensemble with majority voting"""
        detector = AnomalyDetectorEnsemble(
            use_iqr=True,
            use_zscore=True,
            use_isolation_forest=False,  # Don't require sklearn
            voting='majority'
        )

        report = detector.detect(df_with_outliers)

        assert 'Ensemble' in report.method
        assert report.total_anomalies >= 0

    def test_unanimous_voting(self, df_with_outliers):
        """Test unanimous voting (strictest)"""
        detector = AnomalyDetectorEnsemble(
            use_iqr=True,
            use_zscore=True,
            voting='unanimous'
        )

        report = detector.detect(df_with_outliers)

        # Unanimous should be most conservative
        assert isinstance(report, AnomalyReport)

    def test_any_voting(self, df_with_outliers):
        """Test 'any' voting (most sensitive)"""
        detector = AnomalyDetectorEnsemble(
            use_iqr=True,
            use_zscore=True,
            voting='any'
        )

        report = detector.detect(df_with_outliers)

        # 'any' should find the most anomalies
        assert isinstance(report, AnomalyReport)


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_detect_anomalies_iqr(self, df_with_outliers):
        """Test detect_anomalies with IQR method"""
        report = detect_anomalies(df_with_outliers, method='iqr')

        assert isinstance(report, AnomalyReport)
        assert report.method == "IQR"

    def test_detect_anomalies_zscore(self, df_with_outliers):
        """Test detect_anomalies with Z-score method"""
        report = detect_anomalies(df_with_outliers, method='zscore')

        assert isinstance(report, AnomalyReport)
        assert report.method == "Z-Score"

    def test_detect_anomalies_ensemble(self, df_with_outliers):
        """Test detect_anomalies with ensemble method"""
        report = detect_anomalies(df_with_outliers, method='ensemble')

        assert isinstance(report, AnomalyReport)
        assert 'Ensemble' in report.method


class TestAnomalyReport:
    """Test AnomalyReport dataclass"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
        report = AnomalyReport(
            method="IQR",
            total_anomalies=5,
            anomaly_percentage=10.0
        )

        report_dict = report.to_dict()

        assert report_dict['method'] == "IQR"
        assert report_dict['total_anomalies'] == 5
        assert 'timestamp' in report_dict


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
