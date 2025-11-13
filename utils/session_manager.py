"""
Session management for saving and loading chat sessions
Allows users to persist and restore conversation history
"""
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

from config.settings import SESSIONS_DIR, SESSION_TIMEOUT, MAX_CHAT_HISTORY
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manage chat sessions with persistence"""

    def __init__(self, sessions_dir: Path = SESSIONS_DIR):
        """
        Initialize session manager

        Args:
            sessions_dir: Directory for session files
        """
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(exist_ok=True)
        logger.info(f"Session manager initialized: {sessions_dir}")

    def _generate_session_id(self, session_name: str = None) -> str:
        """
        Generate unique session ID

        Args:
            session_name: Optional custom session name

        Returns:
            Session ID string
        """
        if session_name:
            # Use hash of name for consistency
            return hashlib.md5(session_name.encode()).hexdigest()[:16]
        else:
            # Generate from timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"session_{timestamp}"

    def save_session(
        self,
        messages: List[Dict],
        files_info: List[Dict],
        session_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save current session to disk

        Args:
            messages: Chat messages
            files_info: Uploaded files information
            session_name: Optional session name
            metadata: Additional metadata

        Returns:
            Session ID
        """
        session_id = self._generate_session_id(session_name)

        session_data = {
            'session_id': session_id,
            'session_name': session_name or session_id,
            'created_at': datetime.now().isoformat(),
            'messages': messages[-MAX_CHAT_HISTORY:],  # Limit history
            'files_info': files_info,
            'metadata': metadata or {},
            'version': '1.0'
        }

        # Save as JSON for readability
        json_file = self.sessions_dir / f"{session_id}.json"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Session saved: {session_id} ({len(messages)} messages)")

            # Also save as pickle for complete state
            pkl_file = self.sessions_dir / f"{session_id}.pkl"
            with open(pkl_file, 'wb') as f:
                pickle.dump(session_data, f)

            return session_id

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            raise

    def load_session(self, session_id: str) -> Optional[Dict]:
        """
        Load session from disk

        Args:
            session_id: Session ID to load

        Returns:
            Session data dictionary or None
        """
        # Try pickle first (more complete)
        pkl_file = self.sessions_dir / f"{session_id}.pkl"
        if pkl_file.exists():
            try:
                with open(pkl_file, 'rb') as f:
                    session_data = pickle.load(f)
                logger.info(f"Session loaded (pickle): {session_id}")
                return session_data
            except Exception as e:
                logger.warning(f"Failed to load pickle session: {e}")

        # Fall back to JSON
        json_file = self.sessions_dir / f"{session_id}.json"
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                logger.info(f"Session loaded (JSON): {session_id}")
                return session_data
            except Exception as e:
                logger.error(f"Failed to load JSON session: {e}")

        logger.warning(f"Session not found: {session_id}")
        return None

    def list_sessions(self) -> List[Dict]:
        """
        List all available sessions

        Returns:
            List of session metadata dictionaries
        """
        sessions = []

        for json_file in self.sessions_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                sessions.append({
                    'session_id': session_data['session_id'],
                    'session_name': session_data.get('session_name', 'Unnamed'),
                    'created_at': session_data['created_at'],
                    'message_count': len(session_data.get('messages', [])),
                    'file_count': len(session_data.get('files_info', []))
                })
            except Exception as e:
                logger.warning(f"Failed to read session {json_file}: {e}")

        # Sort by creation date, newest first
        sessions.sort(key=lambda x: x['created_at'], reverse=True)

        logger.debug(f"Found {len(sessions)} sessions")
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session ID to delete

        Returns:
            True if successful, False otherwise
        """
        deleted = False

        # Delete JSON file
        json_file = self.sessions_dir / f"{session_id}.json"
        if json_file.exists():
            try:
                json_file.unlink()
                deleted = True
            except Exception as e:
                logger.error(f"Failed to delete JSON session: {e}")

        # Delete pickle file
        pkl_file = self.sessions_dir / f"{session_id}.pkl"
        if pkl_file.exists():
            try:
                pkl_file.unlink()
                deleted = True
            except Exception as e:
                logger.error(f"Failed to delete pickle session: {e}")

        if deleted:
            logger.info(f"Session deleted: {session_id}")
        else:
            logger.warning(f"Session not found for deletion: {session_id}")

        return deleted

    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """
        Delete sessions older than specified days

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of sessions deleted
        """
        deleted_count = 0
        current_time = datetime.now()

        for json_file in self.sessions_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                created_at = datetime.fromisoformat(session_data['created_at'])
                age_days = (current_time - created_at).days

                if age_days > max_age_days:
                    session_id = session_data['session_id']
                    if self.delete_session(session_id):
                        deleted_count += 1

            except Exception as e:
                logger.warning(f"Failed to process session {json_file}: {e}")

        logger.info(f"Cleaned up {deleted_count} old sessions")
        return deleted_count

    def export_session(self, session_id: str, export_format: str = 'markdown') -> Optional[str]:
        """
        Export session to readable format

        Args:
            session_id: Session to export
            export_format: Format ('markdown', 'text', 'html')

        Returns:
            Exported content as string
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return None

        messages = session_data.get('messages', [])
        session_name = session_data.get('session_name', session_id)
        created_at = session_data.get('created_at', 'Unknown')

        if export_format == 'markdown':
            export = f"# {session_name}\n\n"
            export += f"**Created:** {created_at}\n\n"
            export += f"**Messages:** {len(messages)}\n\n"
            export += "---\n\n"

            for msg in messages:
                role = msg.get('role', 'unknown').capitalize()
                content = msg.get('content', '')
                export += f"## {role}\n\n{content}\n\n"

        elif export_format == 'text':
            export = f"{session_name}\n"
            export += f"Created: {created_at}\n"
            export += f"Messages: {len(messages)}\n"
            export += "=" * 80 + "\n\n"

            for msg in messages:
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                export += f"{role}:\n{content}\n\n"
                export += "-" * 80 + "\n\n"

        elif export_format == 'html':
            export = f"""<!DOCTYPE html>
<html>
<head>
    <title>{session_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .message {{ margin: 20px 0; padding: 15px; border-radius: 5px; }}
        .user {{ background-color: #e3f2fd; }}
        .assistant {{ background-color: #f5f5f5; }}
        .role {{ font-weight: bold; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <h1>{session_name}</h1>
    <p><strong>Created:</strong> {created_at}</p>
    <p><strong>Messages:</strong> {len(messages)}</p>
    <hr>
"""
            for msg in messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '').replace('\n', '<br>')
                export += f"""
    <div class="message {role}">
        <div class="role">{role.capitalize()}</div>
        <div>{content}</div>
    </div>
"""
            export += """
</body>
</html>
"""
        else:
            logger.error(f"Unsupported export format: {export_format}")
            return None

        logger.info(f"Session exported: {session_id} as {export_format}")
        return export


# Global session manager instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    return _session_manager


def save_session(**kwargs) -> str:
    """Convenience function to save session"""
    return _session_manager.save_session(**kwargs)


def load_session(session_id: str) -> Optional[Dict]:
    """Convenience function to load session"""
    return _session_manager.load_session(session_id)
