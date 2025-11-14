"""
Logging utilities for Tableau Data Assistant
Provides audit logging, session tracking, and PII-safe logging
"""

import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from config.settings import (
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    ENABLE_AUDIT_LOG,
    LOG_RETENTION_DAYS,
    LOG_PII_SAFE,
    LOGS_DIR
)


@dataclass
class AuditLogEntry:
    """Single audit log entry"""
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    user_id: str = "anonymous"
    action: str = ""
    resource: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"  # success, failure, warning
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class PIISafeFormatter(logging.Formatter):
    """
    Custom log formatter that sanitizes PII
    Ensures sensitive data is never written to logs
    """

    SENSITIVE_KEYS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'api_key',
        'apikey', 'access_token', 'refresh_token', 'auth',
        'email', 'phone', 'ssn', 'credit_card', 'card_number'
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with PII sanitization"""
        # Sanitize message if it contains dict/json
        if hasattr(record, 'msg') and isinstance(record.msg, (dict, list)):
            record.msg = self._sanitize_data(record.msg)

        # Sanitize args
        if hasattr(record, 'args') and record.args:
            record.args = tuple(
                self._sanitize_data(arg) if isinstance(arg, (dict, list)) else arg
                for arg in record.args
            )

        return super().format(record)

    def _sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize sensitive data"""
        if isinstance(data, dict):
            return {
                key: '***REDACTED***' if self._is_sensitive_key(key) else self._sanitize_data(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # Mask potential email/phone patterns
            return self._mask_patterns(data)
        return data

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if key contains sensitive information"""
        key_lower = str(key).lower()
        return any(sensitive in key_lower for sensitive in self.SENSITIVE_KEYS)

    def _mask_patterns(self, text: str) -> str:
        """Mask common PII patterns in text"""
        import re

        # Mask emails
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '***EMAIL***',
            text
        )

        # Mask phone numbers
        text = re.sub(
            r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            '***PHONE***',
            text
        )

        # Mask SSN
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***SSN***', text)

        return text


class AuditLogger:
    """
    Audit logger for tracking user actions and data operations
    Maintains PII-safe audit trail
    """

    def __init__(self, log_dir: Path = LOGS_DIR):
        """
        Initialize audit logger

        Args:
            log_dir: Directory for audit logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.audit_file = self.log_dir / "audit.jsonl"
        self.enabled = ENABLE_AUDIT_LOG

    def log(self, entry: AuditLogEntry):
        """
        Log an audit entry

        Args:
            entry: AuditLogEntry to log
        """
        if not self.enabled:
            return

        # Sanitize details if PII-safe logging is enabled
        if LOG_PII_SAFE:
            entry.details = self._sanitize_details(entry.details)

        # Append to JSONL file
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(entry.to_json() + '\n')

    def log_action(
        self,
        session_id: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        duration_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """
        Convenience method to log an action

        Args:
            session_id: Session identifier
            action: Action performed (e.g., 'upload', 'clean', 'validate')
            resource: Resource acted upon (e.g., 'dataset', 'file')
            details: Additional details
            status: Action status
            duration_ms: Duration in milliseconds
            error_message: Error message if failed
        """
        entry = AuditLogEntry(
            session_id=session_id,
            action=action,
            resource=resource,
            details=details or {},
            status=status,
            duration_ms=duration_ms,
            error_message=error_message
        )
        self.log(entry)

    def get_logs(
        self,
        session_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with filtering

        Args:
            session_id: Filter by session ID
            action: Filter by action type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries
        """
        if not self.audit_file.exists():
            return []

        entries = []

        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())

                    # Apply filters
                    if session_id and entry.get('session_id') != session_id:
                        continue
                    if action and entry.get('action') != action:
                        continue

                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    if start_time and entry_time < start_time:
                        continue
                    if end_time and entry_time > end_time:
                        continue

                    entries.append(entry)

                    if len(entries) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

        return entries

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a session

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session statistics
        """
        logs = self.get_logs(session_id=session_id, limit=10000)

        if not logs:
            return {}

        actions = [log['action'] for log in logs]
        statuses = [log['status'] for log in logs]
        durations = [log.get('duration_ms', 0) for log in logs if log.get('duration_ms')]

        return {
            'session_id': session_id,
            'total_actions': len(logs),
            'action_counts': {action: actions.count(action) for action in set(actions)},
            'status_counts': {status: statuses.count(status) for status in set(statuses)},
            'avg_duration_ms': sum(durations) / len(durations) if durations else 0,
            'total_duration_ms': sum(durations),
            'first_action': logs[0]['timestamp'] if logs else None,
            'last_action': logs[-1]['timestamp'] if logs else None
        }

    def cleanup_old_logs(self, retention_days: int = LOG_RETENTION_DAYS):
        """
        Clean up audit logs older than retention period

        Args:
            retention_days: Number of days to retain logs
        """
        if not self.audit_file.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        temp_file = self.audit_file.with_suffix('.tmp')

        entries_kept = 0
        entries_deleted = 0

        with open(self.audit_file, 'r', encoding='utf-8') as infile:
            with open(temp_file, 'w', encoding='utf-8') as outfile:
                for line in infile:
                    try:
                        entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(entry['timestamp'])

                        if entry_time >= cutoff_date:
                            outfile.write(line)
                            entries_kept += 1
                        else:
                            entries_deleted += 1

                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Keep malformed entries to avoid data loss
                        outfile.write(line)
                        entries_kept += 1

        # Replace original file with cleaned version
        temp_file.replace(self.audit_file)

        return {
            'entries_kept': entries_kept,
            'entries_deleted': entries_deleted,
            'cutoff_date': cutoff_date.isoformat()
        }

    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize details dictionary for PII-safe logging"""
        sanitized = {}

        for key, value in details.items():
            key_lower = str(key).lower()

            # Check for sensitive keys
            if any(word in key_lower for word in ['password', 'token', 'key', 'secret', 'auth']):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_details(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


class SessionLogger:
    """
    Session-specific logger for tracking operations within a session
    """

    def __init__(self, session_id: str):
        """
        Initialize session logger

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.audit_logger = AuditLogger()
        self.start_time = datetime.now()

    def log_upload(self, filename: str, file_size: int, status: str = "success"):
        """Log file upload action"""
        self.audit_logger.log_action(
            session_id=self.session_id,
            action='upload',
            resource='file',
            details={
                'filename': filename,
                'file_size_bytes': file_size
            },
            status=status
        )

    def log_validation(
        self,
        result: Dict[str, Any],
        duration_ms: float,
        status: str = "success"
    ):
        """Log data validation action"""
        self.audit_logger.log_action(
            session_id=self.session_id,
            action='validate',
            resource='dataset',
            details={
                'passed': result.get('passed', False),
                'total_checks': result.get('total_checks', 0),
                'failed_checks': result.get('failed_checks', 0)
            },
            status=status,
            duration_ms=duration_ms
        )

    def log_cleaning(
        self,
        original_shape: tuple,
        cleaned_shape: tuple,
        duration_ms: float,
        status: str = "success"
    ):
        """Log data cleaning action"""
        self.audit_logger.log_action(
            session_id=self.session_id,
            action='clean',
            resource='dataset',
            details={
                'original_rows': original_shape[0],
                'original_cols': original_shape[1],
                'cleaned_rows': cleaned_shape[0],
                'cleaned_cols': cleaned_shape[1],
                'rows_removed': original_shape[0] - cleaned_shape[0],
                'cols_removed': original_shape[1] - cleaned_shape[1]
            },
            status=status,
            duration_ms=duration_ms
        )

    def log_pii_masking(
        self,
        columns_masked: List[str],
        total_values: int,
        status: str = "success"
    ):
        """Log PII masking action"""
        self.audit_logger.log_action(
            session_id=self.session_id,
            action='mask_pii',
            resource='dataset',
            details={
                'columns_masked_count': len(columns_masked),
                'total_values_masked': total_values
            },
            status=status
        )

    def log_anomaly_detection(
        self,
        method: str,
        anomalies_found: int,
        anomaly_percentage: float,
        duration_ms: float,
        status: str = "success"
    ):
        """Log anomaly detection action"""
        self.audit_logger.log_action(
            session_id=self.session_id,
            action='detect_anomalies',
            resource='dataset',
            details={
                'method': method,
                'anomalies_found': anomalies_found,
                'anomaly_percentage': anomaly_percentage
            },
            status=status,
            duration_ms=duration_ms
        )

    def log_export(self, export_format: str, file_path: str, status: str = "success"):
        """Log data export action"""
        self.audit_logger.log_action(
            session_id=self.session_id,
            action='export',
            resource='file',
            details={
                'format': export_format,
                'filename': Path(file_path).name
            },
            status=status
        )

    def log_ai_query(
        self,
        query_type: str,
        input_rows: int,
        duration_ms: float,
        status: str = "success",
        error: Optional[str] = None
    ):
        """Log AI query action"""
        self.audit_logger.log_action(
            session_id=self.session_id,
            action='ai_query',
            resource='ai_model',
            details={
                'query_type': query_type,
                'input_rows': input_rows
            },
            status=status,
            duration_ms=duration_ms,
            error_message=error
        )

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return self.audit_logger.get_session_summary(self.session_id)


def setup_application_logging(
    log_level: str = LOG_LEVEL,
    log_file: Path = LOG_FILE,
    use_pii_safe: bool = LOG_PII_SAFE
) -> logging.Logger:
    """
    Set up application-wide logging

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        use_pii_safe: Use PII-safe formatter

    Returns:
        Configured logger instance
    """
    from logging.handlers import RotatingFileHandler

    # Create logger
    logger = logging.getLogger('tableau_data_assistant')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatter
    if use_pii_safe:
        formatter = PIISafeFormatter(LOG_FORMAT)
    else:
        formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    log_file = Path(log_file)
    log_file.parent.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def generate_session_id() -> str:
    """
    Generate unique session ID

    Returns:
        Unique session identifier
    """
    timestamp = datetime.now().isoformat()
    random_data = str(datetime.now().timestamp())
    combined = f"{timestamp}_{random_data}"

    hash_obj = hashlib.sha256(combined.encode())
    return hash_obj.hexdigest()[:16]


# Global logger instance
app_logger = setup_application_logging()
