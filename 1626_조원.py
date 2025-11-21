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

def get_nav_bar():
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
    nav_bar = QWidget()
    nav_layout = QHBoxLayout(nav_bar)
    nav_layout.setContentsMargins(0, 0, 0, 0)
    nav_layout.setSpacing(0)

    buttons = []
    for text in ["Home", "Score", "Publish"]:
        button = QPushButton(text)
        button.setProperty("selected", "False")
        buttons.append(button)
        nav_layout.addWidget(button)

    nav_layout.addStretch() # Pushes buttons to the left

    def update_selection(selected_button):
        for btn in buttons:
            is_selected = (btn == selected_button)
            btn.setProperty("selected", str(is_selected))
            # Force style refresh
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    for button in buttons:
        button.clicked.connect(lambda checked, b=button: update_selection(b))

    # Set default selection
    update_selection(buttons[0])

    # Apply stylesheet for navigation buttons
    nav_style = """
        QPushButton {
            border: none;
            padding: 10px;
            font-size: 14px;
            background-color: #f0f0f0;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton[selected="True"] {
            background-color: #aed6f1; /* light blue */
            border-bottom: 3px solid #2980b9; /* confident blue */
        }
    """
    nav_bar.setStyleSheet(nav_style)
    return nav_bar

def main():
    print("[main] Starting...")
    try:
        from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
        from PySide6.QtCore import Qt
    except:
        print("[main] Failed to import PySide6. Did bootstrapping work?", file=sys.stderr)
        print("[tip] If the program does not work as expected, ", file=sys.stderr)
        print("[tip] try deleting the package directory and run again.", file=sys.stderr)
        print("[tip] This will reinstall all dependencies.", file=sys.stderr)
        print(f"[tip] Using packages from: {PKG_DIR}", file=sys.stderr)
        sys.exit(1)

    app = QApplication(sys.argv)

    # 1. Main window
    main_window = QWidget()
    main_window.setWindowTitle("Zuoyuequ")

    # 2. Vertical layout
    layout = QVBoxLayout(main_window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # 3. Navigation bar
    nav_bar = get_nav_bar()

    # 4. Main content
    content_label = QLabel("Hello, World!")
    content_label.setAlignment(Qt.AlignCenter)

    # 5. Widget arrangement
    layout.addWidget(nav_bar)
    layout.addWidget(content_label)
    layout.setStretch(1, 1) 

    # 6. Window display
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    bootstrapper()
    sys.path.insert(0, str(PKG_DIR))
    main()
