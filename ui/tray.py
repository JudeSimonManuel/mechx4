import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import sys
import subprocess
import platform
import os

from config import load_config, save_config, LOG_FILE
from core.clipboard import ClipboardDaemon

class TrayApp:
    def __init__(self, daemon: ClipboardDaemon):
        self.daemon = daemon
        self.icon = None

    def create_image(self, color):
        # Generate a 64x64 dynamic shield/circle icon
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        # Draw a simple circle as the shield
        dc.ellipse(
            (8, 8, width - 8, height - 8),
            fill=color,
            outline="white"
        )
        return image

    def toggle_silent_mode(self, icon, item):
        config = load_config()
        config["silent_mode"] = not config.get("silent_mode", False)
        save_config(config)

    def is_silent_mode(self, item):
        config = load_config()
        return config.get("silent_mode", False)

    def get_threats_text(self, item):
        return f"Threats Cleaned: {self.daemon.stats['threats_cleaned']}"

    def view_log(self, icon, item):
        if not LOG_FILE.exists():
            LOG_FILE.touch()
            
        filepath = str(LOG_FILE)
        if platform.system() == 'Windows':
            os.startfile(filepath)
        elif platform.system() == 'Darwin':
            subprocess.call(('open', filepath))
        else:
            subprocess.call(('xdg-open', filepath))

    def on_quit(self, icon, item):
        self.daemon.stop()
        icon.stop()
        # Ensure we terminate
        sys.exit(0)

    def run(self):
        menu = pystray.Menu(
            item('Status: Active / Shielding', lambda: None, enabled=False),
            item(self.get_threats_text, lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Silent Mode', self.toggle_silent_mode, checked=self.is_silent_mode),
            item('View Audit Log', self.view_log),
            pystray.Menu.SEPARATOR,
            item('Exit', self.on_quit)
        )
        
        self.icon = pystray.Icon("AegisTray", self.create_image("green"), "Aegis Shield", menu)
        self.icon.run()
