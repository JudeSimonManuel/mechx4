import threading
import asyncio
from core.clipboard import ClipboardDaemon
from ui.tray import TrayApp

def run_daemon(daemon: ClipboardDaemon):
    # Create a new event loop for the background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(daemon.run())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    daemon = ClipboardDaemon()
    
    # Run the clipboard monitor in a daemon thread
    daemon_thread = threading.Thread(target=run_daemon, args=(daemon,), daemon=True)
    daemon_thread.start()
    
    # Run the system tray app on the main thread
    try:
        app = TrayApp(daemon)
        app.run()
    except Exception as e:
        print(f"Warning: System tray failed to launch ({e}).")
        print("Aegis is continuing to run silently in the background...")
        # Keep the main thread alive so the daemon thread continues to run
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nAegis shutting down.")
