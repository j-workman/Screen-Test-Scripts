import tkinter as tk
import numpy as np
import colour
from screeninfo import get_monitors

# =====================================================================
# CONFIGURATION
# =====================================================================
START_MONITOR_INDEX = 0  # Which monitor to start on

COLORS_TO_DISPLAY = [
    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", 
    "#FF00FF", "#00FFFF", "#FFFFFF", "#808080", "#000000"
]
# =====================================================================

# Force DPI awareness for accurate multi-monitor coordinates on Windows
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

class FullScreenColorViewer:
    def __init__(self, root, colors, monitor_index):
        self.root = root
        self.colors = colors
        self.current_color_index = 0
        
        # Detect and store all available monitors
        self.monitors = get_monitors()
        self.current_monitor_index = monitor_index % len(self.monitors)

        # Strip window borders
        self.root.overrideredirect(True)

        # State for single vs all-monitor display
        self.all_monitors = False

        # Keep lists of windows/labels and mapping to monitor indices
        self.windows = [self.root]
        self.labels = []
        self.window_monitor_indices = []

        # Move to the initial monitor (for the main/root window)
        self.match_window_to_monitor()

        # UI layout anchored to the top right for root window
        self.display_label = tk.Label(
            self.root,
            font=("Courier New", 16, "bold"),
            justify=tk.LEFT,
            anchor=tk.NW,
            padx=50,
            pady=50
        )
        self.display_label.pack(fill=tk.BOTH, expand=True)
        self.labels.append(self.display_label)
        self.window_monitor_indices.append(self.current_monitor_index)

        # Keyboard & Mouse Bindings
        self.root.bind("<Escape>", lambda e: self.close_all())
        self.root.bind("<space>", self.next_color)
        self.root.bind("<Button-1>", self.next_color)

        # Monitor navigation key bindings
        self.root.bind("<Right>", lambda e: self.cycle_monitor(1))
        self.root.bind("<Left>", lambda e: self.cycle_monitor(-1))

        # Toggle display on all monitors (press 'a')
        self.root.bind("<a>", self.toggle_all_monitors)
        self.root.bind("<A>", self.toggle_all_monitors)

        self.update_screen()

    def create_additional_windows(self):
        """Create a Toplevel window on each monitor except the current/root monitor."""
        # Destroy any existing extra windows first
        self.destroy_additional_windows()

        for idx, mon in enumerate(self.monitors):
            if idx == self.current_monitor_index:
                continue
            top = tk.Toplevel(self.root)
            top.overrideredirect(True)
            top.geometry(f"{mon.width}x{mon.height}+{mon.x}+{mon.y}")
            try:
                top.attributes("-topmost", True)
            except Exception:
                pass

            lbl = tk.Label(
                top,
                font=("Courier New", 16, "bold"),
                justify=tk.LEFT,
                anchor=tk.NW,
                padx=50,
                pady=50
            )
            lbl.pack(fill=tk.BOTH, expand=True)

            # Mouse click and escape should behave like root
            top.bind("<Button-1>", self.next_color)
            top.bind("<Escape>", lambda e: self.close_all())

            self.windows.append(top)
            self.labels.append(lbl)
            self.window_monitor_indices.append(idx)

    def destroy_additional_windows(self):
        """Destroy all windows except the main/root window and reset lists."""
        # keep root at index 0
        for w in self.windows[1:]:
            try:
                w.destroy()
            except Exception:
                pass
        self.windows = [self.root]
        self.labels = [self.display_label]
        self.window_monitor_indices = [self.current_monitor_index]

    def toggle_all_monitors(self, event=None):
        """Toggle showing the color on all monitors simultaneously."""
        self.all_monitors = not self.all_monitors
        if self.all_monitors:
            self.create_additional_windows()
        else:
            self.destroy_additional_windows()
            # ensure root matches the current monitor after toggling off
            self.match_window_to_monitor()
        self.update_screen()

    def match_window_to_monitor(self):
        """Reshapes and teleports the window to match the current target monitor."""
        target = self.monitors[self.current_monitor_index]
        self.root.geometry(f"{target.width}x{target.height}+{target.x}+{target.y}")

    def close_all(self):
        """Close all windows cleanly."""
        try:
            self.destroy_additional_windows()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def cycle_monitor(self, step):
        """Switches the target monitor index and instantly moves the window."""
        # Do nothing when in all-monitors mode
        if getattr(self, "all_monitors", False):
            return

        self.current_monitor_index = (self.current_monitor_index + step) % len(self.monitors)
        # keep the root/window mapping in sync
        try:
            self.window_monitor_indices[0] = self.current_monitor_index
        except Exception:
            pass
        self.match_window_to_monitor()
        self.update_screen()

    def calculate_XYZ(self, hex_color):
        """Converts a hex string into normalized sRGB, then computes CIE XYZ and xy values."""
        clean_hex = hex_color.lstrip('#')
        rgb_255 = tuple(int(clean_hex[i:i+2], 16) for i in (0, 2, 4))
        rgb_normalized = np.array(rgb_255) / 255.0
        XYZ = colour.sRGB_to_XYZ(rgb_normalized)
        X, Y, Z = XYZ
        total = X + Y + Z
        if total == 0:
            x = y = 0.0
        else:
            x = X / total
            y = Y / total
        return X, Y, Z, x, y
    

    def update_screen(self):
        """Calculates color metrics, updates background color, and formats overlay text."""
        current_hex = self.colors[self.current_color_index]
        X, Y, Z, x, y = self.calculate_XYZ(current_hex)
        # Build per-window overlays so each shows its monitor index when relevant
        base_overlay = (
            f"HEX CODE: {current_hex}\n"
            f"-----------------------\n"
            f"CIE XYZ Coordinates:\n"
            f"  X = {X:.5f}\n"
            f"  Y = {Y:.5f}\n"
            f"  Z = {Z:.5f}\n"
            f"CIE xy Chromaticity:\n"
            f"  x = {x:.5f}\n"
            f"  y = {y:.5f}\n\n"
        )

        text_color = "#000000" if Y > 0.5 else "#FFFFFF"

        for lbl, mon_idx in zip(self.labels, self.window_monitor_indices):
            if self.all_monitors:
                monitor_line = f"MONITOR  : {mon_idx + 1} of {len(self.monitors)}\n"
                mode_line = "MODE     : ALL MONITORS\n"
            else:
                monitor_line = f"MONITOR  : {self.current_monitor_index + 1} of {len(self.monitors)}\n"
                mode_line = "MODE     : SINGLE MONITOR\n"

            controls = (
                f"-----------------------\n"
                f"[Space/Click] -> Next Color\n"
                f"[Left/Right]  -> Switch Monitor\n"
                f"[A]           -> Toggle All Monitors\n"
                f"[Escape]      -> Exit"
            )

            text_overlay = base_overlay + monitor_line + mode_line + controls

            lbl.config(bg=current_hex, fg=text_color, text=text_overlay)

    def next_color(self, event=None):
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)
        self.update_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = FullScreenColorViewer(root, COLORS_TO_DISPLAY, START_MONITOR_INDEX)
    root.mainloop()