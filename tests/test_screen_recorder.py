import base64
import time
from datetime import datetime

import pytest

from utils.screen_recorder import ScreenRecorder, LiveAnalysisSession


class DummyImage:
    def __init__(self, width=100, height=50, color=b"\xff\x00\x00"):
        self.width = width
        self.height = height
        self._color = color

    def copy(self):
        return DummyImage(self.width, self.height, self._color)

    def resize(self, size, resample=None):  # noqa: D401 - simple stub
        return DummyImage(*size, color=self._color)

    def save(self, target, format='JPEG', quality=80, optimize=True):  # noqa: D401 - simple stub
        data = b"FAKEJPEG" + self._color
        if hasattr(target, "write"):
            target.write(data)
        else:
            with open(target, "wb") as fh:
                fh.write(data)


def test_screen_recorder_frame_provider(tmp_path):
    img = DummyImage()

    def provider():
        # Always return a copy to mimic fresh frames
        return img.copy()

    recorder = ScreenRecorder(fps=5, frame_provider=provider)
    recorder.start_recording()

    # Allow the background thread to enqueue at least one frame
    time.sleep(0.2)

    frame = recorder.get_latest_frame()
    recorder.stop_recording()

    assert frame is not None, "Expected a frame from the provider"
    assert isinstance(frame["timestamp"], datetime)

    encoded = recorder.get_frame_as_base64(frame)
    # Base64 encoded JPEGs should be decodable without error
    base64.b64decode(encoded)

    out_file = tmp_path / "captured.jpg"
    recorder.save_frame(frame, out_file)
    assert out_file.exists()


def test_live_analysis_session_success(monkeypatch):
    img = DummyImage(64, 64)

    class FakeRecorder:
        def start_recording(self, region=None):
            pass

        def stop_recording(self):
            pass

        def get_latest_frame(self):
            return {"timestamp": datetime.now(), "image": img}

        def get_frame_as_base64(self, frame):
            return "ZHVtbXk="  # base64 for 'dummy'

        def save_frame(self, frame, filepath):
            filepath.write_bytes(b"data")

    class FakeContent:
        def __init__(self, text):
            self.text = text

    class FakeUsage:
        input_tokens = 10
        output_tokens = 5

    class FakeResponse:
        def __init__(self):
            self.content = [FakeContent("Looks good")]
            self.usage = FakeUsage()

    class FakeMessages:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self):
            self.messages = FakeMessages()

    client = FakeClient()
    session = LiveAnalysisSession(client)
    session.recorder = FakeRecorder()
    session.recorder_error = None

    result = session.analyze_current_screen()
    assert result["success"] is True
    assert "analysis" in result
    assert result["tokens_used"] == 15


def test_live_analysis_session_no_frame(monkeypatch):
    class FakeRecorder:
        def start_recording(self, region=None):
            pass

        def stop_recording(self):
            pass

        def get_latest_frame(self):
            return None

    class FakeClient:
        def __init__(self):
            self.messages = None

    session = LiveAnalysisSession(FakeClient())
    session.recorder = FakeRecorder()
    session.recorder_error = None

    result = session.analyze_current_screen()
    assert result["success"] is False
    assert result["error"] == "No frame available"
