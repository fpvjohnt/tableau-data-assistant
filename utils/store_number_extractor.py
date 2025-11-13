"""
Store Number Extraction Utility
Extracts store numbers from summary text and formats them properly
"""
import pandas as pd
import re
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_store_number(summary_text: str) -> Optional[str]:
    """
    Extract store number from summary text

    Args:
        summary_text: The summary column text

    Returns:
        Store number as string (no decimals) or None if not found
    """
    if pd.isna(summary_text) or not isinstance(summary_text, str):
        return None

    # Common patterns for store numbers:
    # "Store 521 - ..." or "Store 521" or "521 - ..." or just "521"
    # "Store #521" or "#521"
    # At the beginning: "521 - Break/Fix..."
    # In text: "...Store 230..."

    patterns = [
        r'[Ss]tore\s*#?\s*(\d{3,4})',  # "Store 521" or "Store #521" or "store 521"
        r'^(\d{3,4})\s*[-–]',           # "521 - " or "521- " at start
        r'\b(\d{3,4})\s+[-–]',          # "521 - " anywhere with word boundary
        r'#(\d{3,4})',                  # "#521"
        r'\b(\d{3,4})\.\d\b',           # Match "521.0" pattern and extract just the number
    ]

    for pattern in patterns:
        match = re.search(pattern, summary_text)
        if match:
            store_num = match.group(1)
            # Validate it's a reasonable store number (3-4 digits)
            if len(store_num) >= 3 and len(store_num) <= 4:
                logger.debug(f"Extracted store number {store_num} from: {summary_text[:50]}")
                return store_num

    logger.debug(f"No store number found in: {summary_text[:50]}")
    return None


def clean_store_numbers(df: pd.DataFrame, summary_column: str = 'Summary', store_column: str = 'Store Number') -> pd.DataFrame:
    """
    Clean store number column by extracting from summary

    Args:
        df: DataFrame to clean
        summary_column: Name of the summary column
        store_column: Name of the store number column

    Returns:
        DataFrame with cleaned store numbers
    """
    logger.info("Cleaning store numbers from summary column...")

    if summary_column not in df.columns:
        logger.warning(f"Summary column '{summary_column}' not found")
        return df

    # Create or clean the store number column
    if store_column not in df.columns:
        df[store_column] = None
        logger.info(f"Created new column '{store_column}'")

    # Extract store numbers from summary
    df[store_column] = df[summary_column].apply(extract_store_number)

    # Count results
    total_rows = len(df)
    found_count = df[store_column].notna().sum()
    blank_count = df[store_column].isna().sum()

    logger.info(f"Store number extraction complete:")
    logger.info(f"  - Found store numbers: {found_count}/{total_rows} ({found_count/total_rows*100:.1f}%)")
    logger.info(f"  - Blank (no store number): {blank_count}/{total_rows} ({blank_count/total_rows*100:.1f}%)")

    return df


def remove_decimal_from_store_numbers(df: pd.DataFrame, store_column: str = 'Store Number') -> pd.DataFrame:
    """
    Remove decimal points from store numbers (convert 521.0 to 521)

    Args:
        df: DataFrame to clean
        store_column: Name of the store number column

    Returns:
        DataFrame with cleaned store numbers
    """
    if store_column not in df.columns:
        logger.warning(f"Store number column '{store_column}' not found")
        return df

    logger.info("Removing decimals from store numbers...")

    def clean_number(value):
        if pd.isna(value):
            return None

        # If it's already a number, convert to int then string
        if isinstance(value, (int, float)):
            if pd.notna(value):
                return str(int(value))
            return None

        # If it's a string, remove decimal if present
        if isinstance(value, str):
            # Remove .0 suffix if present
            cleaned = value.strip().replace('.0', '')
            # Remove any other decimals
            if '.' in cleaned:
                cleaned = cleaned.split('.')[0]
            return cleaned if cleaned else None

        return None

    original_count = df[store_column].notna().sum()
    df[store_column] = df[store_column].apply(clean_number)
    final_count = df[store_column].notna().sum()

    logger.info(f"Cleaned {original_count} store numbers (now {final_count} non-blank)")

    return df


def process_store_data(df: pd.DataFrame,
                       summary_column: str = 'Summary',
                       store_column: str = 'Store Number') -> pd.DataFrame:
    """
    Complete store number processing pipeline

    Args:
        df: DataFrame to process
        summary_column: Name of summary column
        store_column: Name of store number column

    Returns:
        DataFrame with properly formatted store numbers
    """
    logger.info("Starting complete store number processing...")

    # Step 1: Remove decimals from existing store numbers
    df = remove_decimal_from_store_numbers(df, store_column)

    # Step 2: Extract store numbers from summary where missing
    # Only extract if store number is blank
    mask = df[store_column].isna()
    missing_count = mask.sum()

    if missing_count > 0:
        logger.info(f"Attempting to extract {missing_count} missing store numbers from summary...")
        df.loc[mask, store_column] = df.loc[mask, summary_column].apply(extract_store_number)

        # Count how many we recovered
        recovered = (df.loc[mask, store_column].notna()).sum()
        logger.info(f"Recovered {recovered} store numbers from summary text")

    # Final stats
    total = len(df)
    with_store = df[store_column].notna().sum()
    without_store = df[store_column].isna().sum()

    logger.info("=" * 60)
    logger.info("Store Number Processing Complete:")
    logger.info(f"  Total rows: {total}")
    logger.info(f"  With store numbers: {with_store} ({with_store/total*100:.1f}%)")
    logger.info(f"  Without store numbers (blank): {without_store} ({without_store/total*100:.1f}%)")
    logger.info("=" * 60)

    return df
