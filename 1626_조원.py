import os
import sys
import subprocess
from pathlib import Path

# Constants
REQUIREMENTS = ["PySide6"]
PKG_DIR = Path(__file__).resolve().parent / "_1626_pkgs"

def bootstrapper():
    print(f"[bootstrapper] Bootstrapping dependencies into \"{PKG_DIR}\" ...")
    print(f"[bootstrapper] Requirements: {REQUIREMENTS}")

    if PKG_DIR.exists():
        print(f"[bootstrapper] {PKG_DIR} already exists, skipping installation.")
        return

    try:
        import pip
    except ImportError:
        print("[bootstrapper] pip is not installed, install pip and try again.")
        return
    print("[bootstrapper] pip is available.")

    PKG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[bootstrapper] Installing to \"{PKG_DIR}\" ...")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(PKG_DIR)]
    cmd += REQUIREMENTS

    # TODO: On some systems pip warns about script locations; that's harmless
    env = os.environ.copy()
    # TODO: Avoid user site interfering
    env.setdefault("PYTHONNOUSERSITE", "1")

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print("\n[bootstrapper] pip failed.", file=sys.stderr)
        print("Command:", " ".join(cmd), file=sys.stderr)
        print("Return code:", e.returncode, file=sys.stderr)
        sys.exit(e.returncode)

    # ensure freshly-installed packages take precedence
    print("[bootstrap] Dependencies ready.")

def main():
    print("[main] Starting main application ...")
    try:
        from PySide6.QtWidgets import QApplication, QLabel
        import sys
    except ImportError as e:
        print("[main] Failed to import PySide6. Did bootstrapping work?", file=sys.stderr)
        print("ImportError:", e, file=sys.stderr)
        print("[tip] If the program does not work as expected, ")
        print("[tip] try deleting the package directory and run again.")
        print("[tip] This will reinstall all dependencies.")
        print(f"[tip] Using packages from: {PKG_DIR}")
        sys.exit(1)
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
