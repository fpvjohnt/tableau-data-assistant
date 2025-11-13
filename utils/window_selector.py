"""
Window selection and visual overlay for screen capture
Allows users to select specific windows (like Tableau) and shows visual feedback
"""
from typing import Optional, Tuple, Dict, List
import threading
import time

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False

try:
    from AppKit import NSWorkspace, NSScreen
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenBorderOverlay:
    """Display a red border around the captured area"""

    def __init__(self, x: int, y: int, width: int, height: int, color: str = "red", thickness: int = 4):
        """
        Initialize border overlay

        Args:
            x, y: Top-left corner position
            width, height: Border dimensions
            color: Border color (default red)
            thickness: Border thickness in pixels
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.thickness = thickness
        self.root = None
        self.is_showing = False

    def show(self):
        """Display the border overlay"""
        if self.is_showing:
            return

        if not TKINTER_AVAILABLE:
            logger.warning("tkinter not available, cannot show border overlay")
            return

        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.8)  # Slightly transparent

        # macOS specific
        try:
            self.root.attributes('-transparent', True)
        except:
            pass

        # Create canvas with transparent background
        canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg='black',
            highlightthickness=0
        )
        canvas.pack()

        # Draw border (hollow rectangle)
        # Top
        canvas.create_rectangle(
            0, 0, self.width, self.thickness,
            fill=self.color, outline=self.color
        )
        # Bottom
        canvas.create_rectangle(
            0, self.height - self.thickness, self.width, self.height,
            fill=self.color, outline=self.color
        )
        # Left
        canvas.create_rectangle(
            0, 0, self.thickness, self.height,
            fill=self.color, outline=self.color
        )
        # Right
        canvas.create_rectangle(
            self.width - self.thickness, 0, self.width, self.height,
            fill=self.color, outline=self.color
        )

        # Add pulsing effect
        self._pulse_border(canvas)

        # Position the window
        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

        # Make clicks pass through (macOS)
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
        except:
            pass

        self.is_showing = True
        self.root.mainloop()

    def _pulse_border(self, canvas):
        """Create pulsing animation effect"""
        def pulse(alpha=0.8, direction=1):
            if not self.is_showing:
                return

            alpha += 0.05 * direction
            if alpha >= 1.0:
                direction = -1
                alpha = 1.0
            elif alpha <= 0.5:
                direction = 1
                alpha = 0.5

            try:
                self.root.attributes('-alpha', alpha)
                self.root.after(100, lambda: pulse(alpha, direction))
            except:
                pass

        self.root.after(100, lambda: pulse())

    def hide(self):
        """Hide the border overlay"""
        self.is_showing = False
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
            self.root = None

    def show_in_thread(self):
        """Show border in a separate thread"""
        thread = threading.Thread(target=self.show, daemon=True)
        thread.start()
        return thread


class WindowSelector:
    """Interactive window selection for macOS and Windows"""

    def __init__(self):
        """Initialize window selector"""
        self.available_windows = []
        logger.info("Window selector initialized")

    def get_tableau_windows(self) -> List[Dict]:
        """
        Find all open Tableau windows

        Returns:
            List of window dictionaries with title, position, size
        """
        tableau_windows = []

        if MACOS_AVAILABLE:
            tableau_windows = self._get_tableau_windows_macos()
        elif PYGETWINDOW_AVAILABLE:
            tableau_windows = self._get_tableau_windows_windows()

        logger.info(f"Found {len(tableau_windows)} Tableau windows")
        return tableau_windows

    def _get_tableau_windows_macos(self) -> List[Dict]:
        """Get Tableau windows on macOS"""
        tableau_windows = []

        try:
            # Get all windows
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID
            )

            for window in window_list:
                window_name = window.get('kCGWindowName', '')
                window_owner = window.get('kCGWindowOwnerName', '')

                # Check if it's a Tableau window
                if 'Tableau' in window_owner or 'Tableau' in window_name:
                    bounds = window.get('kCGWindowBounds', {})

                    tableau_windows.append({
                        'title': window_name or window_owner,
                        'owner': window_owner,
                        'x': int(bounds.get('X', 0)),
                        'y': int(bounds.get('Y', 0)),
                        'width': int(bounds.get('Width', 0)),
                        'height': int(bounds.get('Height', 0)),
                        'window_id': window.get('kCGWindowNumber', 0)
                    })

        except Exception as e:
            logger.error(f"Error getting macOS windows: {e}")

        return tableau_windows

    def _get_tableau_windows_windows(self) -> List[Dict]:
        """Get Tableau windows on Windows"""
        tableau_windows = []

        try:
            all_windows = gw.getAllWindows()

            for window in all_windows:
                if 'Tableau' in window.title:
                    tableau_windows.append({
                        'title': window.title,
                        'x': window.left,
                        'y': window.top,
                        'width': window.width,
                        'height': window.height,
                        'window': window
                    })

        except Exception as e:
            logger.error(f"Error getting Windows windows: {e}")

        return tableau_windows

    def show_selection_dialog(self, on_select_callback) -> Optional[Dict]:
        """
        Show interactive window selection dialog

        Args:
            on_select_callback: Function to call with selected window

        Returns:
            Selected window dictionary
        """
        tableau_windows = self.get_tableau_windows()

        if not tableau_windows:
            logger.warning("No Tableau windows found")
            return None

        # Create selection dialog
        root = tk.Tk()
        root.title("Select Tableau Window")
        root.geometry("500x400")

        selected_window = None

        def on_window_select(event):
            nonlocal selected_window
            selection = listbox.curselection()
            if selection:
                selected_window = tableau_windows[selection[0]]
                root.quit()

        def on_confirm():
            nonlocal selected_window
            selection = listbox.curselection()
            if selection:
                selected_window = tableau_windows[selection[0]]
                root.quit()

        # Header
        header = tk.Label(
            root,
            text="Select Tableau Window to Analyze",
            font=("Arial", 14, "bold"),
            pady=10
        )
        header.pack()

        # Instructions
        instructions = tk.Label(
            root,
            text="Choose the Tableau window you want to monitor:",
            font=("Arial", 10),
            pady=5
        )
        instructions.pack()

        # Listbox with windows
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 11),
            height=10
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox
        for i, window in enumerate(tableau_windows):
            display_text = f"{i+1}. {window['title']} ({window['width']}x{window['height']})"
            listbox.insert(tk.END, display_text)

        listbox.bind('<Double-Button-1>', on_window_select)

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        confirm_btn = tk.Button(
            button_frame,
            text="Select Window",
            command=on_confirm,
            bg="#10a37f",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        )
        confirm_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=root.quit,
            font=("Arial", 11),
            padx=20,
            pady=5
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        root.mainloop()
        root.destroy()

        if selected_window:
            logger.info(f"Selected window: {selected_window['title']}")
            if on_select_callback:
                on_select_callback(selected_window)

        return selected_window

    def get_window_region(self, window: Dict) -> Tuple[int, int, int, int]:
        """
        Get capture region from window dictionary

        Args:
            window: Window dictionary

        Returns:
            Tuple of (x, y, width, height)
        """
        return (
            window['x'],
            window['y'],
            window['width'],
            window['height']
        )


def select_tableau_window() -> Optional[Tuple[int, int, int, int]]:
    """
    Convenience function to select Tableau window and get region

    Returns:
        Tuple of (x, y, width, height) or None
    """
    selector = WindowSelector()
    window = selector.show_selection_dialog(on_select_callback=None)

    if window:
        return selector.get_window_region(window)

    return None


def show_capture_border(x: int, y: int, width: int, height: int) -> ScreenBorderOverlay:
    """
    Convenience function to show capture border

    Args:
        x, y: Top-left position
        width, height: Border dimensions

    Returns:
        ScreenBorderOverlay instance
    """
    overlay = ScreenBorderOverlay(x, y, width, height, color="red", thickness=5)
    overlay.show_in_thread()
    return overlay
