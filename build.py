import os
import subprocess
import sys
from pathlib import Path

def build():
    print("Building Aegis Tray executable...")
    
    # Ensure dependencies are installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing pyinstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    main_script = Path("main.py").resolve()
    
    if not main_script.exists():
        print(f"Error: Could not find {main_script}")
        sys.exit(1)
        
    # Run PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "aegis_tray",
        str(main_script)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("Build complete! Check the 'dist' folder for the executable.")

if __name__ == "__main__":
    build()
