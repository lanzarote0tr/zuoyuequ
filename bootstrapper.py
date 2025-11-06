#!/usr/bin/env python3
"""
run.py — one-file bootstrapper

- Installs Python packages into ./_pkgs (only for this project)
- Imports everything from ./_pkgs by prepending it to sys.path
- Runs your application code at the bottom

How to use:
  1) Put this file in your project root.
  2) Edit REQUIREMENTS below.
  3) Put your app code in `main()` (or import your own module there).
  4) Run:  python3 run.py
"""

from __future__ import annotations
import hashlib
import os
import sys
import subprocess
from pathlib import Path
from textwrap import dedent

# === 1) Declare your dependencies here (PEP 508 specifiers are fine) ===
REQUIREMENTS = [
    # examples:
    "requests=2.30",
    "rich>=13.7",
    # add more...
]

# Optional: extra pip args (e.g., indexes, proxies, no binary rules, etc.)
PIP_ARGS = [
    # "--index-url", "https://pypi.org/simple",
    # "--no-cache-dir",
]

# === 2) Where to install local packages ===
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
    # Fall back to ensurepip if pip is missing (works on CPython)
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

    # Create target folder
    PKG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[bootstrap] Installing to {PKG_DIR} ...")
    # Use `--target` to install into our local folder
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(PKG_DIR)]
    cmd += PIP_ARGS
    cmd += REQUIREMENTS

    # On some systems pip warns about script locations; that's harmless
    env = os.environ.copy()
    # Avoid user site interfering
    env.setdefault("PYTHONNOUSERSITE", "1")

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print("\n[bootstrap] pip failed.", file=sys.stderr)
        print("Command:", " ".join(cmd), file=sys.stderr)
        print("Return code:", e.returncode, file=sys.stderr)
        sys.exit(e.returncode)

    # Record the requirements hash so we only reinstall when they change
    _write_text(MARKER, _hash_requirements(REQUIREMENTS))
    print("[bootstrap] Dependencies ready.")

def _prepend_sys_path():
    # Make our local packages take priority
    sys.path.insert(0, str(PKG_DIR))

def main():
    """
    === 3) Your application starts here ===
    - You can import third-party packages that were just installed.
    - You can import your own modules too.
    """
    # Example usage:
    from rich import print as rprint
    import requests

    rprint("[bold green]Hello from one-file bootstrapper![/bold green]")
    rprint(f"Using _pkgs at: [cyan]{PKG_DIR}[/cyan]")

    # Do something with a dependency:
    r = requests.get("https://httpbin.org/get", timeout=5)
    rprint(f"requests ok? [yellow]{r.status_code}[/yellow]")

    # ...replace with your real program logic...


if __name__ == "__main__":
    # 0) Basic Python version guard (optional)
    if sys.version_info < (3, 8):
        print("Python 3.8+ required.", file=sys.stderr)
        sys.exit(1)

    # 1) Install (if needed)
    if _need_install():
        _install()

    # 2) Load from local folder
    _prepend_sys_path()

    # 3) Run app
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")

