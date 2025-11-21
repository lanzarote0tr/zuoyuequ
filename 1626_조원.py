import os
import sys
import subprocess
from pathlib import Path

# Constants
REQUIREMENTS = [
    "PySide6"
]
PKG_DIR = Path(__file__).resolve().parent / "_1626_pkgs"

def bootstrap():
    if PKG_DIR.exists():
        print(f"[bootstrap] {PKG_DIR} already exists, skipping installation.")
        return
    try:
        import pip
    except ImportError:
        print("[bootstrap] pip is not installed, install pip and try again.")
        return
    
    print("[bootstrap] pip is available.")

    PKG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[bootstrap] Installing to {PKG_DIR} ...")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(PKG_DIR)]
    cmd += REQUIREMENTS

    # TODO: On some systems pip warns about script locations; that's harmless
    env = os.environ.copy()
    # TODO: Avoid user site interfering
    env.setdefault("PYTHONNOUSERSITE", "1")

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print("\n[bootstrap] pip failed.", file=sys.stderr)
        print("Command:", " ".join(cmd), file=sys.stderr)
        print("Return code:", e.returncode, file=sys.stderr)
        sys.exit(e.returncode)

    # ensure freshly-installed packages take precedence
    print("[bootstrap] Dependencies ready.")

def main():
    from PySide6.QtWidgets import QApplication, QLabel
    import sys
    app = QApplication(sys.argv)

    label = QLabel("Hello, World!")
    label.setWindowTitle("Hello Window")
    label.resize(300, 200)
    label.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    bootstrap()
    sys.path.insert(0, str(PKG_DIR))
    main()
