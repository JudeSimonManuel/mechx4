import os
import json
from pathlib import Path

# Config directory and file
CONFIG_DIR = Path.home() / ".aegis"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "sanitization.log"

DEFAULT_CONFIG = {
    "silent_mode": False
}

def _ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged = DEFAULT_CONFIG.copy()
            merged.update(config)
            return merged
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    _ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def log_sanitization(message: str):
    _ensure_config_dir()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
