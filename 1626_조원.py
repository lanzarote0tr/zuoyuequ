import os
import sys
import subprocess
from pathlib import Path

REQUIREMENTS = [
    "PySide6"
]

PKG_DIR = Path(__file__).resolve().parent / "_1626_pkgs"
MARKER = PKG_DIR / ".requirements.hash"

def have_pip():
    try:
        import pip
        return True
    except ImportError:
        return False

def bootstrap():
    if PKG_DIR.exists():
        print(f"[bootstrap] {PKG_DIR} already exists, skipping installation.")
        return
    if have_pip():
        print("[bootstrap] pip is available.")
    else:
        print("[bootstrap] pip is not available, install pip and try again.")
        return

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
