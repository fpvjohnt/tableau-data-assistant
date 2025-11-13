"""
Screen recording and live analysis for Tableau dashboards
Captures screen activity and provides real-time feedback using Claude Vision
"""
import cv2
import numpy as np
import tempfile
import base64
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime
import time
from PIL import Image, ImageGrab
import threading
import queue

try:
    from mss import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenRecorder:
    """Record and analyze screen activity in real-time"""

    def __init__(self, fps: int = 2, quality: int = 80):
        """
        Initialize screen recorder

        Args:
            fps: Frames per second to capture (lower = less API calls)
            quality: JPEG quality (1-100)
        """
        self.fps = fps
        self.quality = quality
        self.is_recording = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.analysis_callback = None
        self.capture_thread = None

        logger.info(f"Screen recorder initialized: fps={fps}, quality={quality}")

    def start_recording(self, monitor: int = 1, region: Optional[tuple] = None):
        """
        Start recording screen

        Args:
            monitor: Monitor number to capture (1 = primary)
            region: Optional (x, y, width, height) to capture specific region
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return

        self.is_recording = True

        if MSS_AVAILABLE:
            self.capture_thread = threading.Thread(
                target=self._capture_loop_mss,
                args=(monitor, region),
                daemon=True
            )
        else:
            self.capture_thread = threading.Thread(
                target=self._capture_loop_pil,
                args=(region,),
                daemon=True
            )

        self.capture_thread.start()
        logger.info("Screen recording started")

    def stop_recording(self):
        """Stop recording screen"""
        self.is_recording = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        logger.info("Screen recording stopped")

    def _capture_loop_mss(self, monitor: int, region: Optional[tuple]):
        """Capture loop using mss (faster)"""
        with mss() as sct:
            # Get monitor info
            if region:
                monitor_config = {
                    "top": region[1],
                    "left": region[0],
                    "width": region[2],
                    "height": region[3]
                }
            else:
                monitor_config = sct.monitors[monitor]

            frame_delay = 1.0 / self.fps

            while self.is_recording:
                start_time = time.time()

                try:
                    # Capture screen
                    screenshot = sct.grab(monitor_config)

                    # Convert to PIL Image
                    img = Image.frombytes(
                        'RGB',
                        screenshot.size,
                        screenshot.bgra,
                        'raw',
                        'BGRX'
                    )

                    # Add to queue (non-blocking)
                    try:
                        self.frame_queue.put_nowait({
                            'timestamp': datetime.now(),
                            'image': img
                        })
                    except queue.Full:
                        # Skip frame if queue is full
                        logger.debug("Frame queue full, skipping frame")

                except Exception as e:
                    logger.error(f"Error capturing frame: {e}")

                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_delay - elapsed)
                time.sleep(sleep_time)

    def _capture_loop_pil(self, region: Optional[tuple]):
        """Capture loop using PIL (fallback)"""
        frame_delay = 1.0 / self.fps

        while self.is_recording:
            start_time = time.time()

            try:
                # Capture screen
                if region:
                    bbox = (region[0], region[1],
                           region[0] + region[2],
                           region[1] + region[3])
                    img = ImageGrab.grab(bbox=bbox)
                else:
                    img = ImageGrab.grab()

                # Add to queue (non-blocking)
                try:
                    self.frame_queue.put_nowait({
                        'timestamp': datetime.now(),
                        'image': img
                    })
                except queue.Full:
                    logger.debug("Frame queue full, skipping frame")

            except Exception as e:
                logger.error(f"Error capturing frame: {e}")

            # Maintain FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_delay - elapsed)
            time.sleep(sleep_time)

    def get_latest_frame(self) -> Optional[Dict]:
        """
        Get latest captured frame

        Returns:
            Dictionary with timestamp and image, or None
        """
        try:
            # Clear queue and get latest
            latest_frame = None
            while not self.frame_queue.empty():
                latest_frame = self.frame_queue.get_nowait()
            return latest_frame
        except queue.Empty:
            return None

    def get_frame_as_base64(self, frame_data: Dict) -> str:
        """
        Convert frame to base64 for Claude API

        Args:
            frame_data: Frame dictionary with image

        Returns:
            Base64 encoded JPEG string
        """
        img = frame_data['image']

        # Resize if too large (max 1280px width)
        max_width = 1280
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Convert to JPEG bytes
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=self.quality, optimize=True)
        buffer.seek(0)

        # Encode to base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return img_base64

    def save_frame(self, frame_data: Dict, filepath: Path):
        """
        Save frame to disk

        Args:
            frame_data: Frame dictionary
            filepath: Path to save image
        """
        img = frame_data['image']
        img.save(filepath, format='JPEG', quality=self.quality, optimize=True)
        logger.debug(f"Frame saved: {filepath}")


class LiveAnalysisSession:
    """Manages a live analysis session with Claude"""

    def __init__(self, claude_client, analysis_prompt: str = None):
        """
        Initialize live analysis session

        Args:
            claude_client: Anthropic client instance
            analysis_prompt: Custom prompt for analysis
        """
        self.client = claude_client
        self.recorder = ScreenRecorder(fps=1, quality=75)  # 1 FPS to save API calls
        self.analysis_history = []

        self.default_prompt = analysis_prompt or """
        Analyze this Tableau dashboard/worksheet screenshot and provide:

        1. **Immediate Issues**: Any errors, problems, or concerns visible
        2. **Design Feedback**: Quick wins to improve visual clarity
        3. **Data Insights**: What the data is telling us
        4. **Next Steps**: What the user should focus on next

        Keep the response concise and actionable (2-3 sentences per section).
        """

        logger.info("Live analysis session initialized")

    def start_session(self, region: Optional[tuple] = None):
        """
        Start live analysis session

        Args:
            region: Optional screen region to capture
        """
        self.recorder.start_recording(region=region)
        logger.info("Live analysis session started")

    def stop_session(self):
        """Stop live analysis session"""
        self.recorder.stop_recording()
        logger.info("Live analysis session stopped")

    def analyze_current_screen(self, custom_prompt: Optional[str] = None) -> Dict:
        """
        Analyze current screen state

        Args:
            custom_prompt: Optional custom prompt

        Returns:
            Analysis result dictionary
        """
        # Get latest frame
        frame_data = self.recorder.get_latest_frame()

        if not frame_data:
            return {
                'success': False,
                'error': 'No frame available',
                'timestamp': datetime.now()
            }

        try:
            # Convert to base64
            img_base64 = self.recorder.get_frame_as_base64(frame_data)

            # Analyze with Claude
            prompt = custom_prompt or self.default_prompt

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": img_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            analysis_result = {
                'success': True,
                'timestamp': frame_data['timestamp'],
                'analysis': response.content[0].text,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens
            }

            # Store in history
            self.analysis_history.append(analysis_result)

            logger.info(f"Screen analyzed successfully ({analysis_result['tokens_used']} tokens)")
            return analysis_result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': frame_data['timestamp']
            }

    def get_analysis_history(self) -> List[Dict]:
        """Get all analysis history"""
        return self.analysis_history

    def clear_history(self):
        """Clear analysis history"""
        self.analysis_history.clear()
        logger.info("Analysis history cleared")


def create_live_session(claude_client) -> LiveAnalysisSession:
    """
    Convenience function to create a live analysis session

    Args:
        claude_client: Anthropic client

    Returns:
        LiveAnalysisSession instance
    """
    return LiveAnalysisSession(claude_client)
