import os
import sys
import subprocess
from pathlib import Path

# Constants
PKG_DIR = Path(__file__).resolve().parent / "_1626_pkgs"
ASSETS_DIR = Path(__file__).resolve().parent / "_1626_pkgs" / "zuoyuequ_assets"
NEW_SCORE_ICON = ASSETS_DIR / "new_score.svg" # TODO: Fetch from resources

def fetch_with_curl(url):
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "5", url],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"curl failed: {e.stderr.strip()}")

def exception_importing(context="importing"):
    import shutil
    print(f"[{context}] Failed to import dependencies.", file=sys.stderr)
    print("[hint] The program did not work as expected.", file=sys.stderr)
    shutil.rmtree(PKG_DIR, ignore_errors=True)
    print("[hint] Please run the program again to reinstall dependencies.", file=sys.stderr)
    sys.exit(1)

def bootstrapper(): # auto-install PySide6 into a controolable folder, avoiding 'it doesn’t work on my PC'
    import shutil
    os.remove("1626_temp.py") if Path("1626_temp.py").exists() else None
    # mandatory check
    try:
        import pip
    except:
        print("[bootstrapper] pip is not installed, install pip and try again.", file=sys.stderr)
        sys.exit(1)
    print("[bootstrapper] pip is available.")

    # Fetch v.txt and req.txt
    remote_v = ""
    remote_req = []
    try:
        remote_v = fetch_with_curl("https://raw.githubusercontent.com/lanzarote0tr/zuoyuequ/main/v.txt").strip()
        remote_req = fetch_with_curl("https://raw.githubusercontent.com/lanzarote0tr/zuoyuequ/main/req.txt").strip().splitlines()
    except Exception as e:
        print(f"[bootstrapper] Failed to fetch: {e}", file=sys.stderr)
        print("[hint] The program did not work as expected.", file=sys.stderr)
        print("[hint] Check the internet connection and try again.", file=sys.stderr)
        sys.exit(1)

    # If ASSETS_DIR does not exist, skip reading v.txt and req.txt
    local_v = ""
    local_req = []
    if ASSETS_DIR.exists():
        # Read v.txt and req.txt
        local_v = ASSETS_DIR / "v.txt"
        try:
            if local_v.exists():
                with open(local_v, 'r', encoding='utf-8') as f:
                    local_v = f.read().strip()
            else:
                local_v = ""
            local_req = ASSETS_DIR / "req.txt"
            if local_req.exists():
                with open(local_req, 'r', encoding='utf-8') as f:
                    local_req = f.read().strip().splitlines()
            else:
                local_req = []
        except Exception as e:
            print(f"[bootstrapper] Failed to read local files: {e}", file=sys.stderr)
            print(f"[tip] Check instance already running or file permissions.", file=sys.stderr)
            sys.exit(1)
    
    # v diff > replace
    if remote_v != local_v:
        print("[bootstrapper] v.txt mismatch!")
        # Fetch v.py
        file = None
        try:
            file = fetch_with_curl("https://raw.githubusercontent.com/lanzarote0tr/zuoyuequ/main/1626_%EC%A1%B0%EC%9B%90.py")
        except Exception as e:
            print(f"[bootstrapper] Failed to fetch: {e}", file=sys.stderr)
            print("[hint] The program did not work as expected.", file=sys.stderr)
            print("[hint] Check the internet connection and try again.", file=sys.stderr)
            sys.exit(1)
        try:
            if not ASSETS_DIR.exists():
                ASSETS_DIR.mkdir(parents=True, exist_ok=True)
            with open(ASSETS_DIR / "v.txt", 'w', encoding='utf-8') as f:
                f.write(remote_v)
            os.rename(Path(sys.argv[0]), "1626_temp.py")
            with open(Path(sys.argv[0]), 'w', encoding='utf-8') as f:
                f.write(file)
        except Exception as e:
            print(f"[bootstrapper] Failed to write files: {e}", file=sys.stderr)
            print(f"[tip] Check instance already running or file permissions.", file=sys.stderr)
            sys.exit(1)
        print("[!] Please re-run the program.")
        sys.exit(0)
    
    # req diff > reinstall
    if sorted(remote_req) != sorted(local_req):
        print("[bootstrapper] req.txt mismatch!")
        if PKG_DIR.exists():
            try:
                shutil.rmtree(PKG_DIR, ignore_errors=True)
            except Exception as e:
                print(f"[bootstrapper] Failed to clear old packages: {e}", file=sys.stderr)
                print(f"[tip] Check instance already running or file permissions.", file=sys.stderr)
                sys.exit(1)
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        with open(ASSETS_DIR / "v.txt", 'w', encoding='utf-8') as f:
            f.write(remote_v)
        with open(ASSETS_DIR / "req.txt", 'w', encoding='utf-8') as f:
            f.write('\n'.join(remote_req))
        print(f"[bootstrapper] Installing to \"{PKG_DIR}\"...")
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(PKG_DIR)] + remote_req
        try:
            # Prevent conflicts with packages from the main Python environment.
            install_env = os.environ.copy()
            install_env["PYTHONNOUSERSITE"] = "1"
            subprocess.run(cmd, check=True, env=install_env)
        except subprocess.CalledProcessError as e:
            print(f"\n[bootstrapper] pip failed. ({e.returncode})", file=sys.stderr)
            sys.exit(e.returncode)
        sys.path.insert(0, str(PKG_DIR))
        print("[bootstrapper] Dependencies ready.")


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
        from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
        from PySide6.QtCore import QSize, Qt
        from PySide6.QtGui import QIcon, QMouseEvent
    except:
        exception_importing("get_home")

    home_tab = QWidget()
    home_tab.setStyleSheet("background-color: #e5e9ed;")
    home_layout = QVBoxLayout(home_tab)
    home_layout.setContentsMargins(50, 100, 50, 0)

    scores_label = QLabel("Scores")
    scores_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
    home_layout.addWidget(scores_label)

    class ClickableButton(QWidget):
        def __init__(self, icon_path, text, parent=None):
            super().__init__(parent)
            self.setObjectName("ClickableButton")
            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setCursor(Qt.PointingHandCursor)
            self.setFixedHeight(70)
            self.default_style = """
                #ClickableButton {
                    background-color: #e4e9ed;
                    border-radius: 5px;
                    height: 1000px;
                }
                #ClickableButton QLabel {
                    background-color: transparent;
                }
            """
            self.hover_style = """
                #ClickableButton {
                    background-color: #dAdfe6;
                    border-radius: 5px;
                }
                #ClickableButton QLabel {
                    background-color: transparent;
                }
            """
            layout = QHBoxLayout(self)
            layout.setContentsMargins(24, 0, 0, 0)
            layout.setSpacing(16)
            icon_label = QLabel()
            icon_pix = QIcon(str(icon_path)).pixmap(QSize(32, 50))
            icon_label.setPixmap(icon_pix)
            text_label = QLabel(text)
            text_label.setStyleSheet("font-size: 20px;")
            layout.addWidget(icon_label)
            layout.addWidget(text_label)
            layout.addStretch()
            self.setStyleSheet(self.default_style)

        def enterEvent(self, event):
            self.setStyleSheet(self.hover_style)

        def leaveEvent(self, event):
            self.setStyleSheet(self.default_style)

        def mousePressEvent(self, event: QMouseEvent):
            print("New Score button clicked!")
    new_score_button = ClickableButton(NEW_SCORE_ICON, "New Score")
    home_layout.addWidget(new_score_button)

    home_layout.addStretch()
    return home_tab

def main():
    print("[main] Starting...")
    try:
        from PySide6.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, 
                                       QStackedWidget, QSizePolicy, QGraphicsView, QGraphicsScene, 
                                       QGraphicsRectItem, QGraphicsLineItem, QPushButton)
        from PySide6.QtCore import Qt, QObject, QEvent, Signal
        from PySide6.QtGui import QKeySequence, QFont, QPainter, QBrush, QColor, QPen
    except Exception as e:
        print(e)
        exception_importing("main")

    class GlobalInput(QObject):
        command = Signal(str)

        def eventFilter(self, obj, event):
            # Only KeyPress events
            if event.type() == QEvent.KeyPress:
                if obj is not app.focusWidget() and app.focusWidget() is not None:
                    return False # Let focused widget handle it
                key_str = QKeySequence(event.key()).toString()
                if key_str == 'Up':
                    self.command.emit("UP")
                    return True
                elif key_str == 'Down':
                    self.command.emit("DOWN")
                    return True
                elif key_str == 'Esc':
                    app.quit()
                    return True
            return False
    
    class InteractiveView(QGraphicsView):
        def __init__(self, scene, parent=None):
            super().__init__(scene, parent)
            self.setStyleSheet("background-color: #bbc1cd; border: none;")
            self.setRenderHint(QPainter.Antialiasing)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        def wheelEvent(self, event):
            zoom_factor = 1.05
            if event.angleDelta().y() > 0:
                self.scale(zoom_factor, zoom_factor)
            else:
                if self.transform().m11() > 0.1:
                    self.scale(1 / zoom_factor, 1 / zoom_factor)

    class ScoreEditor(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.layout = QVBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self._setup_toolbar()
            
            self.scene = QGraphicsScene()
            self.scene.setSceneRect(-2500, -2500, 5000, 5000)
            
            self.view = InteractiveView(self.scene)
            self.layout.addWidget(self.view)
            
            self.cursor = None 
            self._draw_paper_and_staves()
            self._create_cursor()


        def _setup_toolbar(self):
            top_bar = QWidget()
            top_bar.setStyleSheet("background-color: #d0d0d0;")
            tb_layout = QHBoxLayout(top_bar)
            tb_layout.setContentsMargins(5, 5, 5, 5)
            for label in ["A", "B", "C"]:
                tb_layout.addWidget(QPushButton(label))
            tb_layout.addStretch()
            self.layout.addWidget(top_bar)

        def _draw_paper_and_staves(self):
            PAPER_W, PAPER_H = 794, 1123
            MARGIN_X, MARGIN_Y = 50, 100
            LINE_SPACING = 10
            SYSTEM_GAP = 80
            
            paper = QGraphicsRectItem(0, 0, PAPER_W, PAPER_H)
            paper.setBrush(QBrush(QColor("White")))
            self.scene.addItem(paper)
            
            current_y = MARGIN_Y
            for _ in range(8):
                for i in range(5):
                    y = current_y + (i * LINE_SPACING)
                    line = QGraphicsLineItem(MARGIN_X, y, PAPER_W - MARGIN_X, y)
                    line.setPen(QPen(Qt.GlobalColor.black, 1))
                    line.setParentItem(paper)
                current_y += (4 * LINE_SPACING) + SYSTEM_GAP

        def _create_cursor(self):
            self.cursor = QGraphicsRectItem(0, 0, 794, 40)
            self.cursor.setBrush(QBrush(QColor(0, 0, 255, 50)))
            self.cursor.setPen(QPen(Qt.NoPen))
            self.cursor.setZValue(10)
            self.cursor.setPos(0, 100)
            self.scene.addItem(self.cursor)

        def move_cursor_vertical(self, amount):
            if self.cursor:
                self.cursor.setY(self.cursor.y() + amount)
                self.view.ensureVisible(self.cursor)


    # -- Application Execution --
    app = QApplication(sys.argv)
    
    global_listener = GlobalInput()
    app.installEventFilter(global_listener)

    app.setStyleSheet("""
        QWidget {
            font-family: "Pretendard Variable", "Pretendard", "Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", sans-serif;
        }
    """)

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
    score_editor = ScoreEditor()
    score_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    view_switcher.addWidget(score_editor)

    # View > Publish
    view_switcher.addWidget(QLabel("Publish Page"))
    
    # Navigation Bar
    nav_bar = get_nav_bar(view_switcher)

    # Arrangement
    layout.addWidget(nav_bar)
    layout.addWidget(view_switcher)
    layout.setStretch(1, 1) 

    # Connector
    def handle_global_command(cmd):
        if view_switcher.currentWidget() == score_editor:
            if cmd == "UP":
                score_editor.move_cursor_vertical(-10)
            elif cmd == "DOWN":
                score_editor.move_cursor_vertical(10)

    global_listener.command.connect(handle_global_command)

    # Render
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    bootstrapper()
    main()
