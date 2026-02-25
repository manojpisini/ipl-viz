import os
import subprocess
import sys
from pathlib import Path

def build():
    # Define paths relative to this script
    script_dir = Path(__file__).parent.resolve()
    root = script_dir.parent
    main_script = root / "main.py"
    name = "ipl-viz"

    print(f"Starting build for {name}...")
    print(f"Root directory: {root}")

    # Build command
    # --noconsole: Hide the terminal window for GUI apps
    # --onedir: Bundle into a directory (usually more stable and faster startup)
    # --clean: Clean PyInstaller cache and remove temporary files before building
    # --noconfirm: Replace output directory without asking
    
    # OS-specific separator for --add-data
    sep = ";" if os.name == "nt" else ":"
    
    # We include 'data' and 'images' folders
    # Format is: "source_path;dest_path" (on Windows)
    data_path = f"{root / 'data'}{sep}data"
    images_path = f"{root / 'images'}{sep}images"

    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onedir",
        "--clean",
        "--noconfirm",
        "--add-data", data_path,
        "--add-data", images_path,
        "--name", name,
        str(main_script)
    ]

    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # We run via 'uv run' to ensure we use the project's environment
        subprocess.run(["uv", "run"] + cmd, cwd=str(root), check=True)
        print("\n" + "="*50)
        print(f"BUILD SUCCESSFUL!")
        print(f"Executable: {root / 'dist' / name / (name + ('.exe' if os.name == 'nt' else ''))}")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Please ensure uv is installed.")
        sys.exit(1)

if __name__ == "__main__":
    build()
