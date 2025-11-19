import hashlib
import os
import sys
import subprocess
from pathlib import Path
from textwrap import dedent

REQUIREMENTS = [
    "PySide6"
]


PKG_DIR = Path(__file__).resolve().parent / "_pkgs"
MARKER = PKG_DIR / ".requirements.hash"

def _hash_requirements(reqs):
    canon = "\n".join(sorted(reqs)).encode("utf-8")
    return hashlib.sha256(canon).hexdigest()

def _read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None

def _write_text(path, s):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s, encoding="utf-8")

def _have_pip():
    try:
        # TODO try not using sys.executable
        cp = subprocess.run([sys.executable, "-m", "pip", "--version"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return cp.returncode == 0
    except Exception:
        return False

def _ensure_pip():
    if _have_pip():
        return
    # TODO Fall back to ensurepip if pip is missing (works on CPython)
    try:
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
    except Exception as e:
        print("Failed to provision pip via ensurepip:", e, file=sys.stderr)
        print("You may need to install pip for this Python.", file=sys.stderr)
        sys.exit(1)

def _need_install():
    want = _hash_requirements(REQUIREMENTS)
    have = _read_text(MARKER)
    if not PKG_DIR.exists():
        return True
    return want != have

def _install():
    if not _need_install():
        return

    _ensure_pip()

    PKG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[bootstrap] Installing to {PKG_DIR} ...")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(PKG_DIR)]
    cmd += REQUIREMENTS

    # TODO On some systems pip warns about script locations; that's harmless
    env = os.environ.copy()
    # TODO Avoid user site interfering
    env.setdefault("PYTHONNOUSERSITE", "1")

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print("\n[bootstrap] pip failed.", file=sys.stderr)
        print("Command:", " ".join(cmd), file=sys.stderr)
        print("Return code:", e.returncode, file=sys.stderr)
        sys.exit(e.returncode)

    _write_text(MARKER, _hash_requirements(REQUIREMENTS))

    sys.path.insert(0, str(PKG_DIR)) # Fresh-installed packages TAKE PRIORITIEEEEEEEEEEEEEEEEEEEEEEEEE
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
    _install()
    main()

