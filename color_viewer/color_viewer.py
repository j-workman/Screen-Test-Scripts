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
        
        # Move to the initial monitor
        self.match_window_to_monitor()
        
        # UI layout anchored to the top right
        self.display_label = tk.Label(
            self.root, 
            font=("Courier New", 16, "bold"), 
            justify=tk.LEFT, 
            anchor=tk.NW,
            padx=50,
            pady=50
        )
        self.display_label.pack(fill=tk.BOTH, expand=True)

        # Keyboard & Mouse Bindings
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<space>", self.next_color)
        self.root.bind("<Button-1>", self.next_color)
        
        # NEW: Monitor navigation key bindings
        self.root.bind("<Right>", lambda e: self.cycle_monitor(1))
        self.root.bind("<Left>", lambda e: self.cycle_monitor(-1))

        self.update_screen()

    def match_window_to_monitor(self):
        """Reshapes and teleports the window to match the current target monitor."""
        target = self.monitors[self.current_monitor_index]
        self.root.geometry(f"{target.width}x{target.height}+{target.x}+{target.y}")

    def cycle_monitor(self, step):
        """Switches the target monitor index and instantly moves the window."""
        self.current_monitor_index = (self.current_monitor_index + step) % len(self.monitors)
        self.match_window_to_monitor()
        self.update_screen()

    def calculate_xyz(self, hex_color):
        """Converts a hex string into normalized sRGB, then computes CIE XYZ values."""
        clean_hex = hex_color.lstrip('#')
        rgb_255 = tuple(int(clean_hex[i:i+2], 16) for i in (0, 2, 4))
        rgb_normalized = np.array(rgb_255) / 255.0
        return colour.sRGB_to_XYZ(rgb_normalized)

    def update_screen(self):
        """Calculates color metrics, updates background color, and formats overlay text."""
        current_hex = self.colors[self.current_color_index]
        X, Y, Z = self.calculate_xyz(current_hex)

        text_overlay = (
            f"HEX CODE: {current_hex}\n"
            f"-----------------------\n"
            f"CIE XYZ Coordinates:\n"
            f"  X = {X:.5f}\n"
            f"  Y = {Y:.5f}\n"
            f"  Z = {Z:.5f}\n\n"
            f"MONITOR  : {self.current_monitor_index + 1} of {len(self.monitors)}\n"
            f"-----------------------\n"
            f"[Space/Click] -> Next Color\n"
            f"[Left/Right]  -> Switch Monitor\n"
            f"[Escape]      -> Exit"
        )

        text_color = "#000000" if Y > 0.5 else "#FFFFFF"

        self.display_label.config(
            bg=current_hex,
            fg=text_color,
            text=text_overlay
        )

    def next_color(self, event=None):
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)
        self.update_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = FullScreenColorViewer(root, COLORS_TO_DISPLAY, START_MONITOR_INDEX)
    root.mainloop()