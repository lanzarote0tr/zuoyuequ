import os
import sys
import subprocess
from pathlib import Path

# Constants
REQUIREMENTS = ["PySide6"]
PKG_DIR = Path(__file__).resolve().parent / "_1626_pkgs"

def bootstrapper():
    print(f"[bootstrapper] Checking dependencies at \"{PKG_DIR}\"...")
    # Check if already installed
    if PKG_DIR.exists():
        print(f"[bootstrapper] {PKG_DIR} already exists, skipping installation.")
        return
    # Check for pip
    try:
        import pip
    except ImportError:
        print("[bootstrapper] pip is not installed, install pip and try again.", file=sys.stderr)
        return
    print("[bootstrapper] pip is available.")
    # Install packages
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[bootstrapper] Installing to \"{PKG_DIR}\"...")
    print(f"[bootstrapper] Requirements: {REQUIREMENTS}")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(PKG_DIR)] + REQUIREMENTS
    try:
        # Prevent conflicts with packages from the main Python environment.
        install_env = os.environ.copy()
        install_env["PYTHONNOUSERSITE"] = "1"
        subprocess.run(cmd, check=True, env=install_env)
    except subprocess.CalledProcessError as e:
        print(f"\n[bootstrapper] pip failed. ({e.returncode})", file=sys.stderr)
        sys.exit(e.returncode)
    print("[bootstrapper] Dependencies ready.")

def main():
    print("[main] Starting...")
    try:
        from PySide6.QtWidgets import QApplication, QLabel
    except ImportError as e:
        print("[main] Failed to import PySide6. Did bootstrapping work?", file=sys.stderr)
        print("[tip] If the program does not work as expected, ", file=sys.stderr)
        print("[tip] try deleting the package directory and run again.", file=sys.stderr)
        print("[tip] This will reinstall all dependencies.", file=sys.stderr)
        print(f"[tip] Using packages from: {PKG_DIR}", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)
    label = QLabel("Hello, World!")
    label.setWindowTitle("Hello Window")
    label.resize(300, 200)
    label.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    bootstrapper()
    sys.path.insert(0, str(PKG_DIR))
    main()
