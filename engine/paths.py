import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # This is for --onefile or --onedir mode
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # fallback to current directory if not running in a bundle
        base_path = Path(".")

    return base_path / relative_path
