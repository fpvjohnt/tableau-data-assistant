"""
Multi-monitor support for dual-screen setups
Allows selecting specific monitors for capture while keeping browser separate
"""
from typing import List, Dict, Optional, Tuple

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from mss import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from AppKit import NSScreen
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)


class MonitorSelector:
    """Select specific monitor for screen capture"""

    def __init__(self):
        """Initialize monitor selector"""
        self.monitors = []
        self.detect_monitors()
        logger.info(f"Monitor selector initialized: {len(self.monitors)} monitors detected")

    def detect_monitors(self):
        """Detect all available monitors"""
        self.monitors = []

        if MSS_AVAILABLE:
            with mss() as sct:
                for i, monitor in enumerate(sct.monitors):
                    if i == 0:  # Skip the "all monitors" entry
                        continue

                    self.monitors.append({
                        'id': i,
                        'name': f"Monitor {i}",
                        'x': monitor['left'],
                        'y': monitor['top'],
                        'width': monitor['width'],
                        'height': monitor['height'],
                        'primary': i == 1,
                        'monitor_obj': monitor
                    })

        elif MACOS_AVAILABLE:
            screens = NSScreen.screens()
            for i, screen in enumerate(screens):
                frame = screen.frame()
                self.monitors.append({
                    'id': i + 1,
                    'name': f"Monitor {i + 1}",
                    'x': int(frame.origin.x),
                    'y': int(frame.origin.y),
                    'width': int(frame.size.width),
                    'height': int(frame.size.height),
                    'primary': i == 0,
                    'monitor_obj': screen
                })

        logger.info(f"Detected {len(self.monitors)} monitors")
        for mon in self.monitors:
            logger.debug(f"Monitor {mon['id']}: {mon['width']}x{mon['height']} at ({mon['x']}, {mon['y']})")

    def get_monitors(self) -> List[Dict]:
        """Get list of all monitors"""
        return self.monitors

    def get_monitor_by_id(self, monitor_id: int) -> Optional[Dict]:
        """Get specific monitor by ID"""
        for monitor in self.monitors:
            if monitor['id'] == monitor_id:
                return monitor
        return None

    def get_primary_monitor(self) -> Optional[Dict]:
        """Get primary monitor"""
        for monitor in self.monitors:
            if monitor.get('primary', False):
                return monitor
        return self.monitors[0] if self.monitors else None

    def show_monitor_selector_dialog(self, title: str = "Select Monitor") -> Optional[Dict]:
        """
        Show dialog to select monitor

        Args:
            title: Dialog title

        Returns:
            Selected monitor dictionary or None
        """
        if not self.monitors:
            logger.warning("No monitors detected")
            return None

        if len(self.monitors) == 1:
            logger.info("Only one monitor, auto-selecting")
            return self.monitors[0]

        # If tkinter not available, return primary monitor with warning
        if not TKINTER_AVAILABLE:
            logger.warning("tkinter not available, returning primary monitor")
            logger.info("Install tkinter for interactive monitor selection: brew install python-tk")
            return self.get_primary_monitor()

        # Create selection dialog
        root = tk.Tk()
        root.title(title)
        root.geometry("600x500")

        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        selected_monitor = None

        def on_monitor_select(event):
            nonlocal selected_monitor
            selection = listbox.curselection()
            if selection:
                selected_monitor = self.monitors[selection[0]]
                root.quit()

        def on_confirm():
            nonlocal selected_monitor
            selection = listbox.curselection()
            if selection:
                selected_monitor = self.monitors[selection[0]]
                root.quit()

        def on_preview():
            """Show preview borders on all monitors"""
            selection = listbox.curselection()
            if selection:
                preview_monitor = self.monitors[selection[0]]
                self._show_preview_border(preview_monitor)

        # Header with dual-monitor icon
        header_frame = tk.Frame(root, bg="#10a37f", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="🖥️  Select Monitor for Tableau Capture",
            font=("Arial", 16, "bold"),
            bg="#10a37f",
            fg="white",
            pady=20
        )
        header_label.pack()

        # Instructions
        instructions_frame = tk.Frame(root, bg="white", padx=20, pady=15)
        instructions_frame.pack(fill=tk.X)

        instructions = tk.Label(
            instructions_frame,
            text="Choose the monitor where Tableau is open.\n"
                 "Your browser chat will stay on the other monitor.",
            font=("Arial", 11),
            bg="white",
            fg="#333333",
            justify=tk.LEFT
        )
        instructions.pack()

        # Tip box
        tip_frame = tk.Frame(root, bg="#e8f5e9", padx=15, pady=10)
        tip_frame.pack(fill=tk.X, padx=20, pady=10)

        tip_label = tk.Label(
            tip_frame,
            text="💡 Tip: Select 'Preview' to see a border on each monitor",
            font=("Arial", 10),
            bg="#e8f5e9",
            fg="#2e7d32",
            anchor="w"
        )
        tip_label.pack(fill=tk.X)

        # Monitor list
        list_frame = tk.Frame(root, padx=20)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        list_label = tk.Label(
            list_frame,
            text="Available Monitors:",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        list_label.pack(anchor="w", pady=(0, 5))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier New", 11),
            height=8,
            selectmode=tk.SINGLE,
            bg="#f5f5f5",
            selectbackground="#10a37f",
            selectforeground="white",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightcolor="#10a37f"
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox with monitor info
        for i, monitor in enumerate(self.monitors):
            primary_tag = " [PRIMARY]" if monitor.get('primary') else ""
            position = f"Position: ({monitor['x']}, {monitor['y']})"

            display_text = (
                f"{'🖥️ ' if monitor.get('primary') else '🖵  '}"
                f"Monitor {monitor['id']}{primary_tag}\n"
                f"  Size: {monitor['width']} × {monitor['height']} px\n"
                f"  {position}"
            )

            listbox.insert(tk.END, display_text)

            # Add separator except for last item
            if i < len(self.monitors) - 1:
                listbox.insert(tk.END, "─" * 60)

        # Pre-select primary monitor
        for i, monitor in enumerate(self.monitors):
            if monitor.get('primary'):
                listbox.selection_set(i * 2)  # Account for separators
                break

        listbox.bind('<Double-Button-1>', on_monitor_select)

        # Buttons
        button_frame = tk.Frame(root, bg="white", pady=15)
        button_frame.pack(fill=tk.X)

        preview_btn = tk.Button(
            button_frame,
            text="👁️  Preview",
            command=on_preview,
            font=("Arial", 11),
            bg="white",
            fg="#10a37f",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            borderwidth=1,
            cursor="hand2"
        )
        preview_btn.pack(side=tk.LEFT, padx=(80, 10))

        confirm_btn = tk.Button(
            button_frame,
            text="✓ Select Monitor",
            command=on_confirm,
            bg="#10a37f",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        confirm_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="✕ Cancel",
            command=root.quit,
            font=("Arial", 11),
            bg="white",
            fg="#666666",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            borderwidth=1,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Hover effects
        def on_enter(e, btn, bg_color):
            btn['background'] = bg_color

        def on_leave(e, btn, bg_color):
            btn['background'] = bg_color

        confirm_btn.bind("<Enter>", lambda e: on_enter(e, confirm_btn, "#0d8f6d"))
        confirm_btn.bind("<Leave>", lambda e: on_leave(e, confirm_btn, "#10a37f"))

        root.mainloop()
        root.destroy()

        if selected_monitor:
            logger.info(f"Selected monitor {selected_monitor['id']}: {selected_monitor['width']}x{selected_monitor['height']}")

        return selected_monitor

    def _show_preview_border(self, monitor: Dict):
        """Show temporary border on monitor for preview"""
        if not TKINTER_AVAILABLE:
            logger.warning("tkinter not available, cannot show preview border")
            return

        from utils.window_selector import ScreenBorderOverlay

        overlay = ScreenBorderOverlay(
            monitor['x'],
            monitor['y'],
            monitor['width'],
            monitor['height'],
            color="blue",  # Blue for preview
            thickness=8
        )

        # Show for 2 seconds
        import threading
        def show_and_hide():
            overlay.show()

        thread = threading.Thread(target=show_and_hide, daemon=True)
        thread.start()

    def get_monitor_region(self, monitor: Dict) -> Tuple[int, int, int, int]:
        """
        Get capture region for monitor

        Args:
            monitor: Monitor dictionary

        Returns:
            Tuple of (x, y, width, height)
        """
        return (
            monitor['x'],
            monitor['y'],
            monitor['width'],
            monitor['height']
        )


def select_monitor(title: str = "Select Monitor for Tableau") -> Optional[Tuple[int, int, int, int]]:
    """
    Convenience function to select monitor and get region

    Args:
        title: Dialog title

    Returns:
        Tuple of (x, y, width, height) or None
    """
    selector = MonitorSelector()
    monitor = selector.show_monitor_selector_dialog(title)

    if monitor:
        return selector.get_monitor_region(monitor)

    return None


def get_left_monitor() -> Optional[Dict]:
    """
    Get the leftmost monitor (usually where Tableau would be)

    Returns:
        Monitor dictionary or None
    """
    selector = MonitorSelector()
    monitors = selector.get_monitors()

    if not monitors:
        return None

    # Find leftmost monitor (smallest x coordinate)
    leftmost = min(monitors, key=lambda m: m['x'])
    logger.info(f"Left monitor: Monitor {leftmost['id']}")
    return leftmost


def get_right_monitor() -> Optional[Dict]:
    """
    Get the rightmost monitor (usually where browser would be)

    Returns:
        Monitor dictionary or None
    """
    selector = MonitorSelector()
    monitors = selector.get_monitors()

    if not monitors:
        return None

    # Find rightmost monitor (largest x coordinate)
    rightmost = max(monitors, key=lambda m: m['x'])
    logger.info(f"Right monitor: Monitor {rightmost['id']}")
    return rightmost
