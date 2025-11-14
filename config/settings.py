"""
Configuration settings for Tableau Data Assistant
Centralized configuration management for the application
"""
from typing import Dict, Any
from pathlib import Path
import os

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
SESSIONS_DIR = BASE_DIR / "sessions"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for directory in [DATA_DIR, CACHE_DIR, SESSIONS_DIR, EXPORTS_DIR, LOGS_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# File processing limits
MAX_FILE_SIZE_MB = 500  # Maximum file size in MB
CHUNK_SIZE_ROWS = 100000  # Rows to read for large files
MAX_UPLOAD_FILES = 10  # Maximum files per upload
LARGE_FILE_THRESHOLD_MB = 200  # When to use chunked reading

# Data cleaning thresholds
MIN_OUTLIER_PERCENTAGE = 1.0  # Minimum % of outliers to report
HIGH_MISSING_THRESHOLD = 50.0  # % missing to flag as high
DATETIME_CONFIDENCE_THRESHOLD = 0.7  # Confidence for datetime conversion
NUMERIC_CONFIDENCE_THRESHOLD = 0.7  # Confidence for numeric conversion
MAX_TABLEAU_ROWS = 1000000  # Cap for Tableau performance

# Visualization suggestions
LOW_CARDINALITY_THRESHOLD = 10  # For bar charts
MEDIUM_CARDINALITY_THRESHOLD = 50  # For tree maps
HIGH_CARDINALITY_THRESHOLD = 20  # For heatmaps
PIE_CHART_MAX_CATEGORIES = 5  # Maximum categories for pie charts

# API Configuration
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
API_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Cache settings
CACHE_TTL = 3600  # Cache time-to-live in seconds (1 hour)
CACHE_MAX_SIZE = 100  # Maximum cached items

# Session settings
SESSION_TIMEOUT = 86400  # 24 hours in seconds
MAX_CHAT_HISTORY = 100  # Maximum messages in chat history

# UI Configuration
THEME_CONFIG = {
    "dark": {
        "background": "#212121",
        "secondary_bg": "#2f2f2f",
        "sidebar_bg": "#171717",
        "text": "#ECECEC",
        "text_secondary": "#B4B4B4",
        "primary": "#10a37f",
        "border": "#3f3f3f"
    },
    "light": {
        "background": "#FFFFFF",
        "secondary_bg": "#F7F7F8",
        "sidebar_bg": "#F9FAFB",
        "text": "#1F2937",
        "text_secondary": "#6B7280",
        "primary": "#10a37f",
        "border": "#E5E7EB"
    }
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "app.log"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# Security settings
ALLOWED_FILE_EXTENSIONS = {".csv", ".xlsx", ".xls", ".twb", ".twbx", ".png", ".jpg", ".jpeg"}
DANGEROUS_EXTENSIONS = {".exe", ".sh", ".bat", ".cmd", ".com", ".scr"}
MAX_API_KEY_LENGTH = 200
MIN_API_KEY_LENGTH = 20

# Statistical analysis settings
OUTLIER_IQR_MULTIPLIER = 1.5  # IQR multiplier for outlier detection
CORRELATION_THRESHOLD = 0.7  # Strong correlation threshold
NORMALITY_TEST_ALPHA = 0.05  # Alpha for normality tests

# Export settings
EXPORT_FORMATS = ["csv", "xlsx", "pdf", "html", "json"]
PDF_PAGE_SIZE = "A4"
HTML_TEMPLATE_NAME = "report_template.html"

# Data quality scoring weights
QUALITY_WEIGHTS = {
    "completeness": 0.30,  # Missing values
    "uniqueness": 0.20,    # Duplicate records
    "validity": 0.25,      # Data type consistency
    "consistency": 0.15,   # Outliers and anomalies
    "timeliness": 0.10     # Date relevance
}

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    "clear_chat": "Ctrl+Shift+C",
    "new_analysis": "Ctrl+N",
    "export_report": "Ctrl+E",
    "save_session": "Ctrl+S",
    "toggle_theme": "Ctrl+T"
}

# Responsible AI Configuration
AI_MODE = os.getenv("AI_MODE", "cloud")  # "cloud" or "offline"
ENABLE_ANOMALY_DETECTION = os.getenv("ENABLE_ANOMALY_DETECTION", "true").lower() == "true"
ENABLE_SCREENSHOT_ANALYSIS = os.getenv("ENABLE_SCREENSHOT_ANALYSIS", "true").lower() == "true"
MAX_ROWS_FOR_AI = int(os.getenv("MAX_ROWS_FOR_AI", "100"))
MASK_PII = os.getenv("MASK_PII", "true").lower() == "true"

# Privacy and Data Minimization
PII_COLUMNS_KEYWORDS = [
    "email", "mail", "e-mail",
    "phone", "telephone", "mobile", "cell",
    "ssn", "social_security",
    "name", "first_name", "last_name", "full_name",
    "address", "street", "city", "zip", "postal",
    "credit_card", "card_number", "cvv",
    "password", "passwd", "pwd",
    "account_number", "account_id",
    "customer_id", "user_id", "employee_id",
    "ip_address", "ip", "mac_address",
    "license", "passport", "driver"
]

# Validation Configuration
VALIDATION_ENABLED = os.getenv("VALIDATION_ENABLED", "true").lower() == "true"
NULL_THRESHOLD_PERCENT = float(os.getenv("NULL_THRESHOLD_PERCENT", "20.0"))  # Max % nulls allowed
UNIQUENESS_THRESHOLD = float(os.getenv("UNIQUENESS_THRESHOLD", "95.0"))  # Min % unique for ID columns
VALIDATION_SAMPLE_SIZE = int(os.getenv("VALIDATION_SAMPLE_SIZE", "10000"))  # Rows to sample for validation

# Anomaly Detection Configuration
ANOMALY_CONTAMINATION = float(os.getenv("ANOMALY_CONTAMINATION", "0.05"))  # Expected % of anomalies
ANOMALY_N_ESTIMATORS = int(os.getenv("ANOMALY_N_ESTIMATORS", "100"))  # For Isolation Forest
ANOMALY_MAX_FEATURES = float(os.getenv("ANOMALY_MAX_FEATURES", "1.0"))  # Features to use

# Screenshot Analysis Configuration
SCREENSHOT_MAX_SIZE_MB = int(os.getenv("SCREENSHOT_MAX_SIZE_MB", "10"))
SCREENSHOT_MIN_DIMENSION = int(os.getenv("SCREENSHOT_MIN_DIMENSION", "400"))  # px
SCREENSHOT_ANALYSIS_ASPECTS = [
    "layout_clarity",
    "label_readability",
    "filter_placement",
    "visual_clutter",
    "accessibility",
    "color_usage"
]

# Logging and Monitoring
ENABLE_AUDIT_LOG = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))
LOG_PII_SAFE = True  # Never log actual PII values

def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a configuration setting

    Args:
        key: Setting key
        default: Default value if key not found

    Returns:
        Setting value or default
    """
    return globals().get(key, default)

def update_setting(key: str, value: Any) -> bool:
    """
    Update a configuration setting at runtime

    Args:
        key: Setting key
        value: New value

    Returns:
        True if successful, False otherwise
    """
    if key in globals():
        globals()[key] = value
        return True
    return False

def get_all_settings() -> Dict[str, Any]:
    """
    Get all configuration settings as a dictionary

    Returns:
        Dictionary of all settings
    """
    return {
        key: value for key, value in globals().items()
        if not key.startswith("_") and key.isupper()
    }

def get_settings() -> Dict[str, Any]:
    """
    Get all settings as a dictionary (alias for get_all_settings)

    Returns:
        Dictionary of all configuration settings
    """
    return get_all_settings()

def is_ai_enabled() -> bool:
    """Check if AI mode is enabled"""
    return AI_MODE == "cloud"

def is_offline_mode() -> bool:
    """Check if running in offline mode"""
    return AI_MODE == "offline"
