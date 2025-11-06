from __future__ import annotations
import hashlib
import os
import sys
import subprocess
from pathlib import Path
from textwrap import dedent

REQUIREMENTS = [
    "requests==2.30",
    "rich>=13.7",
]

PIP_ARGS = [
    # "--index-url", "https://pypi.org/simple",
    # "--no-cache-dir",
]

PKG_DIR = Path(__file__).resolve().parent / "_pkgs"
MARKER = PKG_DIR / ".requirements.hash"

def _hash_requirements(reqs: list[str]) -> str:
    canon = "\n".join(sorted(reqs)).encode("utf-8")
    return hashlib.sha256(canon).hexdigest()

def _read_text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return None

def _write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def _have_pip() -> bool:
    try:
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

def _need_install() -> bool:
    want = _hash_requirements(REQUIREMENTS)
    have = _read_text(MARKER)
    if not PKG_DIR.exists():
        return True
    return want != have

def _install():
    if not REQUIREMENTS:
        return
    _ensure_pip()

    PKG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[bootstrap] Installing to {PKG_DIR} ...")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(PKG_DIR)]
    cmd += PIP_ARGS
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
    print("[bootstrap] Dependencies ready.")

def _prepend_sys_path():
    # TODO Make our local packages take priority
    # Disable this
    sys.path.insert(0, str(PKG_DIR))

def main():
    """
    === 3) Your application starts here ===
    - You can import third-party packages that were just installed.
    - You can import your own modules too.
    """
    from rich import print as rprint
    import requests

    rprint("[bold green]Hello from one-file bootstrapper![/bold green]")
    rprint(f"Using _pkgs at: [cyan]{PKG_DIR}[/cyan]")

    r = requests.get("https://google.com", timeout=5)
    rprint(f"requests ok? [yellow]{r.status_code}[/yellow]")



if __name__ == "__main__":
    if sys.version_info < (3, 8):
        print("Python 3.8+ required.", file=sys.stderr)
        sys.exit(1)

    if _need_install():
        _install()

    _prepend_sys_path()

    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")

