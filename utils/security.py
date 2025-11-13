"""
Security utilities for Tableau Data Assistant
Handles API key encryption, file validation, and input sanitization
"""
import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

# Optional import for python-magic
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from config.settings import (
    ALLOWED_FILE_EXTENSIONS,
    DANGEROUS_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    MAX_API_KEY_LENGTH,
    MIN_API_KEY_LENGTH
)
from utils.logger import get_logger

logger = get_logger(__name__)


class SecurityManager:
    """Manages security operations"""

    def __init__(self):
        """Initialize security manager"""
        self.key_file = Path.home() / ".tableau_assistant" / "key.key"
        self.key_file.parent.mkdir(exist_ok=True)
        self._encryption_key = self._get_or_create_encryption_key()

    def _get_or_create_encryption_key(self) -> bytes:
        """
        Get or create encryption key for API keys

        Returns:
            Encryption key
        """
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key from machine-specific data
            machine_id = self._get_machine_id()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'tableau_assistant_salt',
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))

            # Save key
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logger.info("Created new encryption key")

            return key

    def _get_machine_id(self) -> str:
        """
        Get machine-specific identifier

        Returns:
            Machine ID string
        """
        try:
            # Try to get MAC address
            import uuid
            mac = uuid.getnode()
            return str(mac)
        except:
            # Fallback to hostname
            import socket
            return socket.gethostname()

    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt API key for secure storage

        Args:
            api_key: Plain API key

        Returns:
            Encrypted API key
        """
        try:
            f = Fernet(self._encryption_key)
            encrypted = f.encrypt(api_key.encode())
            logger.debug("API key encrypted successfully")
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt API key: {e}")
            raise

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt API key

        Args:
            encrypted_key: Encrypted API key

        Returns:
            Plain API key
        """
        try:
            f = Fernet(self._encryption_key)
            decoded = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = f.decrypt(decoded)
            logger.debug("API key decrypted successfully")
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            raise

    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate API key format

        Args:
            api_key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key:
            return False, "API key is empty"

        if len(api_key) < MIN_API_KEY_LENGTH:
            return False, f"API key too short (minimum {MIN_API_KEY_LENGTH} characters)"

        if len(api_key) > MAX_API_KEY_LENGTH:
            return False, f"API key too long (maximum {MAX_API_KEY_LENGTH} characters)"

        if not api_key.replace('-', '').replace('_', '').isalnum():
            return False, "API key contains invalid characters"

        return True, None

    def validate_file(self, file_path: Path, file_content: bytes = None) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file for security

        Args:
            file_path: Path to file
            file_content: File content bytes (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        if file_path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
            return False, f"File type {file_path.suffix} not allowed"

        if file_path.suffix.lower() in DANGEROUS_EXTENSIONS:
            return False, f"Dangerous file type {file_path.suffix} detected"

        # Check file size
        if file_path.exists():
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                return False, f"File too large ({file_size_mb:.1f}MB, max {MAX_FILE_SIZE_MB}MB)"

        # Check MIME type if python-magic is available
        if MAGIC_AVAILABLE:
            try:
                if file_content:
                    mime_type = magic.from_buffer(file_content, mime=True)
                else:
                    mime_type = magic.from_file(str(file_path), mime=True)

                # Validate MIME type matches extension
                valid_mimes = {
                    '.csv': ['text/csv', 'text/plain', 'application/csv'],
                    '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
                    '.xls': ['application/vnd.ms-excel'],
                    '.png': ['image/png'],
                    '.jpg': ['image/jpeg'],
                    '.jpeg': ['image/jpeg'],
                    '.twb': ['text/xml', 'application/xml'],
                    '.twbx': ['application/zip']
                }

                expected_mimes = valid_mimes.get(file_path.suffix.lower(), [])
                if expected_mimes and mime_type not in expected_mimes:
                    logger.warning(f"MIME type mismatch: {mime_type} for {file_path.suffix}")
                    # Don't block, just warn
            except Exception as e:
                logger.warning(f"Could not verify MIME type: {e}")
        else:
            logger.debug("python-magic not available, skipping MIME type validation")

        return True, None

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name

        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', '\x00']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit length
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length-len(ext)] + ext

        return filename

    def hash_file(self, file_path: Path) -> str:
        """
        Generate SHA256 hash of file

        Args:
            file_path: Path to file

        Returns:
            Hex digest of file hash
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def sanitize_sql(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        """
        Basic SQL injection prevention (for display/analysis only)

        Args:
            sql_query: SQL query string

        Returns:
            Tuple of (is_safe, warning_message)
        """
        # Dangerous SQL keywords
        dangerous_keywords = [
            'drop table', 'drop database', 'truncate', 'delete from',
            'insert into', 'update ', 'grant ', 'revoke ',
            'create user', 'drop user', 'alter user',
            'exec ', 'execute ', 'xp_', 'sp_'
        ]

        sql_lower = sql_query.lower()
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return False, f"Potentially dangerous SQL detected: {keyword}"

        # Check for comment injection
        if '--' in sql_query or '/*' in sql_query or '*/' in sql_query:
            logger.warning("SQL contains comments - review carefully")

        return True, None


# Global security manager instance
_security_manager = SecurityManager()


def get_security_manager() -> SecurityManager:
    """Get global security manager instance"""
    return _security_manager


def validate_file(file_path: Path, file_content: bytes = None) -> Tuple[bool, Optional[str]]:
    """Convenience function for file validation"""
    return _security_manager.validate_file(file_path, file_content)


def sanitize_filename(filename: str) -> str:
    """Convenience function for filename sanitization"""
    return _security_manager.sanitize_filename(filename)
