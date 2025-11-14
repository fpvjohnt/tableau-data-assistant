"""
Privacy and PII masking utilities
Provides data minimization and PII detection/masking for responsible AI
"""

from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
import re
import hashlib

from config.settings import PII_COLUMNS_KEYWORDS, MASK_PII


@dataclass
class PIIReport:
    """Report of PII detection and masking operations"""
    detected_columns: List[str] = field(default_factory=list)
    masked_columns: List[str] = field(default_factory=list)
    detection_method: Dict[str, str] = field(default_factory=dict)
    total_values_masked: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'detected_columns': self.detected_columns,
            'masked_columns': self.masked_columns,
            'detection_method': self.detection_method,
            'total_values_masked': self.total_values_masked,
            'timestamp': self.timestamp.isoformat()
        }


class PIIDetector:
    """Detect personally identifiable information in DataFrames"""

    # Common PII patterns (regex)
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    CREDIT_CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    IP_ADDRESS_PATTERN = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

    def __init__(self, keywords: List[str] = None):
        """
        Initialize PII detector

        Args:
            keywords: List of column name keywords that indicate PII
        """
        self.keywords = keywords or PII_COLUMNS_KEYWORDS

    def detect_pii_columns(self, df: pd.DataFrame) -> PIIReport:
        """
        Detect columns containing PII

        Args:
            df: DataFrame to analyze

        Returns:
            PIIReport with detected PII columns
        """
        report = PIIReport()

        for col in df.columns:
            col_lower = str(col).lower()

            # Check 1: Column name contains PII keywords
            if self._matches_keyword(col_lower):
                report.detected_columns.append(col)
                report.detection_method[col] = 'keyword_match'
                continue

            # Check 2: Content pattern analysis (sample first 100 non-null values)
            sample = df[col].dropna().head(100)
            if len(sample) == 0:
                continue

            detection_result = self._detect_pii_pattern(sample)
            if detection_result:
                report.detected_columns.append(col)
                report.detection_method[col] = detection_result

        return report

    def _matches_keyword(self, col_name: str) -> bool:
        """Check if column name matches PII keywords"""
        for keyword in self.keywords:
            if keyword.lower() in col_name:
                return True
        return False

    def _detect_pii_pattern(self, series: pd.Series) -> Optional[str]:
        """
        Detect PII patterns in series content

        Args:
            series: Series to analyze

        Returns:
            Detection method string if PII found, None otherwise
        """
        # Convert to strings
        str_series = series.astype(str)

        # Email detection
        if self._pattern_match_rate(str_series, self.EMAIL_PATTERN) > 0.5:
            return 'email_pattern'

        # Phone detection
        if self._pattern_match_rate(str_series, self.PHONE_PATTERN) > 0.5:
            return 'phone_pattern'

        # SSN detection
        if self._pattern_match_rate(str_series, self.SSN_PATTERN) > 0.5:
            return 'ssn_pattern'

        # Credit card detection
        if self._pattern_match_rate(str_series, self.CREDIT_CARD_PATTERN) > 0.3:
            return 'credit_card_pattern'

        # IP address detection
        if self._pattern_match_rate(str_series, self.IP_ADDRESS_PATTERN) > 0.5:
            return 'ip_address_pattern'

        return None

    def _pattern_match_rate(self, series: pd.Series, pattern: str) -> float:
        """Calculate percentage of values matching a pattern"""
        matches = series.str.contains(pattern, regex=True, na=False).sum()
        total = len(series)
        return matches / total if total > 0 else 0.0


class PIIMasker:
    """Mask personally identifiable information"""

    def __init__(self, mask_char: str = '*'):
        """
        Initialize PII masker

        Args:
            mask_char: Character to use for masking
        """
        self.mask_char = mask_char

    def mask_dataframe(
        self,
        df: pd.DataFrame,
        pii_columns: Optional[List[str]] = None,
        method: str = 'partial'
    ) -> Tuple[pd.DataFrame, PIIReport]:
        """
        Mask PII in DataFrame

        Args:
            df: DataFrame to mask
            pii_columns: List of columns to mask (if None, will auto-detect)
            method: Masking method - 'partial', 'full', 'hash', or 'remove'

        Returns:
            Tuple of (masked DataFrame, PIIReport)
        """
        df_masked = df.copy()
        report = PIIReport()

        # Auto-detect PII if not specified
        if pii_columns is None:
            detector = PIIDetector()
            detection_report = detector.detect_pii_columns(df)
            pii_columns = detection_report.detected_columns
            report.detected_columns = detection_report.detected_columns
            report.detection_method = detection_report.detection_method
        else:
            report.detected_columns = pii_columns

        # Mask each column
        for col in pii_columns:
            if col not in df.columns:
                continue

            original_null_count = df_masked[col].isnull().sum()

            if method == 'partial':
                df_masked[col] = df_masked[col].apply(self._partial_mask)
            elif method == 'full':
                df_masked[col] = df_masked[col].apply(self._full_mask)
            elif method == 'hash':
                df_masked[col] = df_masked[col].apply(self._hash_value)
            elif method == 'remove':
                df_masked = df_masked.drop(columns=[col])
                report.masked_columns.append(col)
                report.total_values_masked[col] = len(df) - original_null_count
                continue
            else:
                raise ValueError(f"Unknown masking method: {method}")

            report.masked_columns.append(col)
            report.total_values_masked[col] = len(df) - original_null_count

        return df_masked, report

    def _partial_mask(self, value: Any) -> str:
        """Partially mask a value (show first/last chars)"""
        if pd.isna(value):
            return value

        str_value = str(value)
        length = len(str_value)

        if length <= 4:
            # Too short, full mask
            return self.mask_char * length

        # Show first 2 and last 2 characters
        visible_chars = 2
        masked_length = length - (2 * visible_chars)

        return (
            str_value[:visible_chars] +
            self.mask_char * masked_length +
            str_value[-visible_chars:]
        )

    def _full_mask(self, value: Any) -> str:
        """Fully mask a value"""
        if pd.isna(value):
            return value

        str_value = str(value)
        return self.mask_char * len(str_value)

    def _hash_value(self, value: Any) -> str:
        """Hash a value using SHA256"""
        if pd.isna(value):
            return value

        str_value = str(value)
        hash_obj = hashlib.sha256(str_value.encode())
        return hash_obj.hexdigest()[:16]  # Truncate for readability

    def mask_email(self, email: str) -> str:
        """Mask email address (show first char and domain)"""
        if pd.isna(email) or '@' not in str(email):
            return email

        parts = str(email).split('@')
        if len(parts) != 2:
            return email

        username, domain = parts

        if len(username) == 0:
            return email

        # Show first character of username
        masked_username = username[0] + self.mask_char * (len(username) - 1)

        return f"{masked_username}@{domain}"

    def mask_phone(self, phone: str) -> str:
        """Mask phone number (show last 4 digits)"""
        if pd.isna(phone):
            return phone

        # Remove non-digits
        digits = re.sub(r'\D', '', str(phone))

        if len(digits) < 4:
            return self.mask_char * len(digits)

        # Show last 4 digits
        return self.mask_char * (len(digits) - 4) + digits[-4:]

    def mask_ssn(self, ssn: str) -> str:
        """Mask SSN (show last 4 digits)"""
        if pd.isna(ssn):
            return ssn

        str_ssn = str(ssn)

        # Check for XXX-XX-XXXX format
        if '-' in str_ssn:
            parts = str_ssn.split('-')
            if len(parts) == 3:
                return f"{self.mask_char * 3}-{self.mask_char * 2}-{parts[2]}"

        # Plain digits
        digits = re.sub(r'\D', '', str_ssn)
        if len(digits) >= 4:
            return self.mask_char * (len(digits) - 4) + digits[-4:]

        return self.mask_char * len(digits)

    def mask_credit_card(self, card: str) -> str:
        """Mask credit card (show last 4 digits)"""
        if pd.isna(card):
            return card

        # Remove non-digits
        digits = re.sub(r'\D', '', str(card))

        if len(digits) < 4:
            return self.mask_char * len(digits)

        # Show last 4 digits
        masked = self.mask_char * (len(digits) - 4) + digits[-4:]

        # Format in groups of 4
        return ' '.join([masked[i:i+4] for i in range(0, len(masked), 4)])


class DataMinimizer:
    """Minimize data for AI processing (privacy-first approach)"""

    def __init__(self, max_rows: int = 100):
        """
        Initialize data minimizer

        Args:
            max_rows: Maximum rows to send to AI
        """
        self.max_rows = max_rows

    def minimize_for_ai(
        self,
        df: pd.DataFrame,
        auto_mask_pii: bool = True,
        sample_method: str = 'head'
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Minimize DataFrame for AI processing

        Args:
            df: DataFrame to minimize
            auto_mask_pii: Automatically detect and mask PII
            sample_method: Sampling method - 'head', 'tail', 'random', or 'stratified'

        Returns:
            Tuple of (minimized DataFrame, metadata dict)
        """
        metadata = {
            'original_shape': df.shape,
            'minimized_shape': None,
            'pii_masked': False,
            'sample_method': sample_method,
            'columns_removed': []
        }

        # Step 1: Sample rows
        if len(df) > self.max_rows:
            if sample_method == 'head':
                df_min = df.head(self.max_rows)
            elif sample_method == 'tail':
                df_min = df.tail(self.max_rows)
            elif sample_method == 'random':
                df_min = df.sample(n=self.max_rows, random_state=42)
            elif sample_method == 'stratified':
                # Try to get representative sample
                df_min = self._stratified_sample(df, self.max_rows)
            else:
                df_min = df.head(self.max_rows)
        else:
            df_min = df.copy()

        # Step 2: Mask PII if enabled
        if auto_mask_pii and MASK_PII:
            masker = PIIMasker()
            df_min, pii_report = masker.mask_dataframe(df_min, method='partial')
            metadata['pii_masked'] = True
            metadata['pii_columns'] = pii_report.masked_columns

        metadata['minimized_shape'] = df_min.shape

        return df_min, metadata

    def _stratified_sample(self, df: pd.DataFrame, n_samples: int) -> pd.DataFrame:
        """Get stratified sample from DataFrame"""
        # Find a good column for stratification (categorical with reasonable cardinality)
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        stratify_col = None
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 20:  # Reasonable number of categories
                stratify_col = col
                break

        if stratify_col:
            # Stratified sample
            return df.groupby(stratify_col, group_keys=False).apply(
                lambda x: x.sample(min(len(x), max(1, n_samples // df[stratify_col].nunique())), random_state=42)
            ).head(n_samples)
        else:
            # Fallback to random sample
            return df.sample(n=min(n_samples, len(df)), random_state=42)


def generate_pii_report_summary(report: PIIReport) -> str:
    """
    Generate human-readable PII report summary

    Args:
        report: PIIReport to summarize

    Returns:
        Formatted string summary
    """
    summary_lines = [
        "### PII Detection and Masking Report",
        "",
        f"**Detected PII Columns:** {len(report.detected_columns)}",
        f"**Masked Columns:** {len(report.masked_columns)}",
        ""
    ]

    if report.detected_columns:
        summary_lines.append("**Detection Details:**")
        for col in report.detected_columns:
            method = report.detection_method.get(col, 'unknown')
            values_masked = report.total_values_masked.get(col, 0)
            summary_lines.append(f"  - {col}: {method} ({values_masked:,} values masked)")

    if not report.detected_columns:
        summary_lines.append("No PII detected in dataset.")

    return "\n".join(summary_lines)


# Convenience function
def mask_pii_dataframe(
    df: pd.DataFrame,
    method: str = 'partial',
    auto_detect: bool = True
) -> Tuple[pd.DataFrame, PIIReport]:
    """
    One-line function to mask PII in DataFrame

    Args:
        df: DataFrame to mask
        method: Masking method ('partial', 'full', 'hash', 'remove')
        auto_detect: Automatically detect PII columns

    Returns:
        Tuple of (masked DataFrame, PIIReport)
    """
    masker = PIIMasker()
    return masker.mask_dataframe(df, pii_columns=None if auto_detect else [], method=method)
