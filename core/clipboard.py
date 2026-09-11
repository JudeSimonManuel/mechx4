import asyncio
import hashlib
import pyperclip
from plyer import notification
from datetime import datetime

from core.sanitizer import sanitize_payload
from config import load_config, log_sanitization

class ClipboardDaemon:
    def __init__(self):
        self.last_inspected_hash = ""
        self.running = False
        self.stats = {
            "threats_cleaned": 0
        }

    def _get_hash(self, text: str) -> str:
        if not text:
            return ""
        return hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()

    def _notify(self, message: str):
        config = load_config()
        if config.get("silent_mode", False):
            return
            
        try:
            notification.notify(
                title="Aegis Shield Alert",
                message=message,
                app_name="Aegis Tray",
                timeout=5
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")

    async def run(self):
        self.running = True
        
        # Initialize hash with current clipboard to avoid immediate trigger on start
        try:
            current_clipboard = pyperclip.paste()
            self.last_inspected_hash = self._get_hash(current_clipboard)
        except Exception:
            pass

        while self.running:
            try:
                current_clipboard = pyperclip.paste()
                
                # We only process if it's text and changed since last inspection
                if current_clipboard:
                    current_hash = self._get_hash(current_clipboard)
                    
                    if current_hash != self.last_inspected_hash:
                        import subprocess
                        import sys
                        
                        def ask_global_permission():
                            script = """
import tkinter as tk
import sys

def on_yes():
    root.destroy()
    sys.exit(0)

def on_no():
    root.destroy()
    sys.exit(1)

def on_timeout():
    root.destroy()
    sys.exit(1) # Default to deny if ignored

root = tk.Tk()
root.overrideredirect(True) # Remove OS window borders
root.attributes('-topmost', True)

# Modern Dark Theme Colors
bg_color = "#1E1E2E"
fg_color = "#CDD6F4"
accent = "#89B4FA"
deny_color = "#F38BA8"
font_main = ("Helvetica", 10)
font_btn = ("Helvetica", 9, "bold")

root.configure(bg=bg_color)

# Position at bottom right (Toast style)
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
w, h = 320, 110
x = ws - w - 30
y = hs - h - 60
root.geometry(f'{w}x{h}+{x}+{y}')

# Border frame
frame = tk.Frame(root, bg=bg_color, highlightbackground=accent, highlightthickness=1)
frame.pack(fill='both', expand=True, padx=0, pady=0)

lbl = tk.Label(frame, text="🛡️ Aegis Intercept\\nNew clipboard data detected.\\nAllow security scan?", 
               bg=bg_color, fg=fg_color, font=font_main, justify="left")
lbl.pack(pady=12, padx=15, anchor="w")

btn_frame = tk.Frame(frame, bg=bg_color)
btn_frame.pack(fill='x', padx=15, pady=(0, 10))

btn_yes = tk.Button(btn_frame, text="Scan (Allow)", bg=accent, fg="#11111B", 
                    activebackground="#B4BEFE", relief="flat", command=on_yes, font=font_btn, cursor="hand2")
btn_yes.pack(side="left", expand=True, fill='x', padx=(0, 5))

btn_no = tk.Button(btn_frame, text="Ignore (Private)", bg=deny_color, fg="#11111B", 
                   activebackground="#F9E2AF", relief="flat", command=on_no, font=font_btn, cursor="hand2")
btn_no.pack(side="right", expand=True, fill='x', padx=(5, 0))

# Auto-dismiss after 8 seconds to prevent workflow blocking
root.after(8000, on_timeout)

root.mainloop()
"""
                            try:
                                # Run tkinter in a completely separate process to avoid background thread crashes
                                subprocess.check_call([sys.executable, "-c", script])
                                return True
                            except subprocess.CalledProcessError:
                                return False
                            
                        # Ask permission on every copy
                        if ask_global_permission():
                            # Analyze and sanitize
                            result = await sanitize_payload(current_clipboard)
                            
                            if result.is_modified:
                                # Update clipboard with clean text
                                pyperclip.copy(result.sanitized_text)
                                
                                # Update our known hash to the cleaned version so we don't re-process it
                                self.last_inspected_hash = self._get_hash(result.sanitized_text)
                                self.stats["threats_cleaned"] += 1
                                
                                log_msg = f"[{datetime.now().isoformat()}] Cleaned threat: {result.reason}"
                                log_sanitization(log_msg)
                                self._notify("Cleaned hidden prompt injection / steganography from clipboard.")
                            else:
                                self.last_inspected_hash = current_hash
                        else:
                            # User declined, ignore this hash so we don't prompt again for the same text
                            self.last_inspected_hash = current_hash
            
            except Exception as e:
                # Don't crash daemon on clipboard access errors
                print(f"Clipboard access error: {e}")
                
            # Adaptive backoff / polling interval
            await asyncio.sleep(0.5)

    def stop(self):
        self.running = False
