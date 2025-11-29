import os
import sys
import subprocess
from pathlib import Path

# Constants
REQUIREMENTS = ["PySide6"]
PKG_DIR = Path(__file__).resolve().parent / "_1626_pkgs"
NEW_SCORE_ICON = PKG_DIR / "new_score.png" # TODO: Fetch from resources

def bootstrapper(): # auto-install PySide6 into a controolable folder, avoiding 'it doesn’t work on my PC'
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

def exception_importing(context="importing"):
    print(f"[{context}] Failed to import dependencies.", file=sys.stderr)
    print("[hint] The program did not work as expected.", file=sys.stderr)
    print("[hint] If this keeps failing on your PC, delete the package folder and run it again.", file=sys.stderr)
    print(f"[hint] Using packages from: {PKG_DIR}", file=sys.stderr)
    sys.exit(1)

def get_nav_bar(view_switcher):
    try:
        from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup
    except:
        exception_importing("get_nav_bar")
    nav_bar = QWidget()
    nav_layout = QHBoxLayout(nav_bar)
    nav_layout.setContentsMargins(0, 0, 0, 0)
    nav_layout.setSpacing(0)

    button_group = QButtonGroup(nav_bar)
    button_group.setExclusive(True) # Exclusive selection
    buttons = []
    for idx, text in enumerate(["Home", "Score", "Publish"]):
        button = QPushButton(text)
        button.setCheckable(True)
        buttons.append(button)
        nav_layout.addWidget(button)
        button_group.addButton(button, idx)
        if idx == 0:
            button.setChecked(True)

    nav_layout.addStretch() # Push buttons to the left

    nav_style = """
        QPushButton {
            border: 3px solid transparent;
            padding: 10px;
            font-size: 14px;
            background-color: #f5f5f6;
        }
        QPushButton:hover {
            background-color: #e2e5e9;
        }
        QPushButton:checked {
            background-color: #e5eef5;
            border-bottom: 3px solid #5ab1ef;
        }
    """
    nav_bar.setStyleSheet(nav_style)
    # Button click handling
    button_group.idClicked.connect(view_switcher.setCurrentIndex)
    return nav_bar

def get_home():
    try:
        from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QStyle
        from PySide6.QtGui import QIcon
    except:
        exception_importing("get_home")

    home_tab = QWidget()
    home_tab.setStyleSheet("background-color: #e5e9ed;")

    # VSTACK
    home_layout = QVBoxLayout(home_tab)
    home_layout.setContentsMargins(50, 100, 50, 0)

    # Scores Label
    scores_label = QLabel("Scores")
    scores_label.setStyleSheet("font-size: 24px; font-weight: bold;")
    home_layout.addWidget(scores_label)

    # New Score Button
    new_score_button = QPushButton("New Score")
    new_score_button.setIcon(QIcon(str(NEW_SCORE_ICON)))
    new_score_button.setStyleSheet("""
        QPushButton {
            height: 50px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            text-align: left;
            padding-left: 12px;
        }
        QPushButton:hover {
            background-color: #e2e5e9;
        }
    """)
    home_layout.addWidget(new_score_button)

    home_layout.addStretch() # Push content to the top
    return home_tab

def get_score():
    try:
        from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsRectItem
        from PySide6.QtGui import QBrush, QColor, QPainter
        from PySide6.QtCore import Qt, QObject, QEvent
    except:
        exception_importing("get_score")

    score_tab = QWidget()
    score_tab.setStyleSheet("background-color: grey;")
    
    score_layout = QVBoxLayout(score_tab)
    score_layout.setContentsMargins(0, 0, 0, 0)
    score_layout.setSpacing(0)

    top_bar = QWidget()
    top_bar.setStyleSheet("background-color: #d0d0d0;")
    top_bar_layout = QHBoxLayout(top_bar)
    top_bar_layout.setContentsMargins(5, 5, 5, 5)
    for label in ["A", "B", "C"]:
        btn = QPushButton(label)
        top_bar_layout.addWidget(btn)
    top_bar_layout.addStretch()
    score_layout.addWidget(top_bar)

    score = QGraphicsScene()
    score.setSceneRect(-2500, -2500, 5000, 5000)

    paper = QGraphicsRectItem(0, 0, 794, 1123) # A4 at 96 DPI
    paper.setBrush(QBrush(QColor("White")))
    score.addItem(paper)

    view = QGraphicsView(score)
    view.setStyleSheet("background-color: #f5f5f6; border: none;")
    view.setRenderHint(QPainter.Antialiasing)
    view.setDragMode(QGraphicsView.ScrollHandDrag)
    view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    class WheelZoom(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Wheel:
                zoom_factor = 1.05
                
                # Check current scale (m11 is the horizontal scale)
                current_scale = view.transform().m11()

                if event.angleDelta().y() > 0:
                    # Zoom In
                    view.scale(zoom_factor, zoom_factor)
                else:
                    # Zoom Out: Only allow if we are above the limit (0.1 = 10%)
                    if current_scale > 0.1:
                        view.scale(1 / zoom_factor, 1 / zoom_factor)
                return True 
            return False

    zoom_filter = WheelZoom()
    view.viewport().installEventFilter(zoom_filter)

    view.my_scene_ref = score
    view.my_filter_ref = zoom_filter

    view.centerOn(paper)

    score_layout.addWidget(view)
    
    return score_tab

def main():
    print("[main] Starting...")
    try:
        from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QStackedWidget, QSizePolicy
        from PySide6.QtCore import Qt, QObject, QEvent
        from PySide6.QtGui import QKeySequence
    except:
        exception_importing("main")

    app = QApplication(sys.argv)

    class GlobalInput(QObject):
        def eventFilter(self, obj, event):
            # We only care about KeyPress events
            if event.type() == QEvent.KeyPress:
                if obj is not app.focusWidget() and app.focusWidget() is not None:
                    return False # Let focused widget handle it
                key = event.key()
                key = QKeySequence(key).toString()
                if key == 'Esc':
                    print("[Global] Escape pressed - Exiting")
                    app.quit()
                    return True # True = "We handled this, don't pass it on"
                # Debug: Print any key pressed
                print(f"[Global] Key Pressed: {key}")

            return False
    global_listener = GlobalInput()
    app.installEventFilter(global_listener)

    # Main window
    main_window = QWidget()
    main_window.setWindowTitle("Zuoyuequ")
    main_window.setStyleSheet("background-color: #f5f5f6;")

    # VSTACK
    layout = QVBoxLayout(main_window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # VSTACK > View Switcher
    view_switcher = QStackedWidget()

    # View > Home
    home = get_home()
    view_switcher.addWidget(home)

    # View > Score
    score = get_score()
    score.setMinimumSize(900, 1200)  # Ensure it's visible and large enough
    score.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    view_switcher.addWidget(score)

    # View > Publish
    publish_label = QLabel("Welcome to the Publish Page")
    publish_label.setAlignment(Qt.AlignCenter)
    view_switcher.addWidget(publish_label)

    nav_bar = get_nav_bar(view_switcher)

    # Arrangement
    layout.addWidget(nav_bar)
    layout.addWidget(view_switcher)
    layout.setStretch(1, 1) 

    # Render
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    bootstrapper()
    sys.path.insert(0, str(PKG_DIR))
    main()
