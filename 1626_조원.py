import os
import sys
import subprocess
from pathlib import Path

# Constants
PKG_DIR = Path(__file__).resolve().parent / "_1626_pkgs"
ASSETS_DIR = Path(__file__).resolve().parent / "_1626_pkgs" / "zuoyuequ_assets"

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
        remote_v = fetch_with_curl("https://zuoyuequ.trillion-won.com/v.txt").strip()
        remote_req = fetch_with_curl("https://zuoyuequ.trillion-won.com/req.txt").strip().splitlines()
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
            file = fetch_with_curl("https://zuoyuequ.trillion-won.com/1626_%EC%A1%B0%EC%9B%90.py")
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
        print("[bootstrapper] Dependencies ready.")

def asset_fetch():
    print("[bootstrapper] Fetching assets...")
    assets = ["new_score.svg", "quarter_note_up.svg", "quarter_note_down.svg", "treble.svg"]
    for asset in assets:
        try:
            content = fetch_with_curl(f"https://zuoyuequ.trillion-won.com/assets/{asset}")
            print(content)
            with open(ASSETS_DIR / asset, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"[bootstrapper] Failed to fetch asset {asset}: {e}", file=sys.stderr)
            print("[hint] The program did not work as expected.", file=sys.stderr)
            print("[hint] Check the internet connection and try again.", file=sys.stderr)
            sys.exit(1)
    print("[bootstrapper] Assets ready.")


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

    nav_bar.button_group = button_group # Attach for external access
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

def get_home(view_switcher, nav_bar):
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
        def __init__(self, parent=None):
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
            icon_pix = QIcon(str(ASSETS_DIR / "new_score.svg")).pixmap(QSize(32, 50))
            icon_label.setPixmap(icon_pix)
            text_label = QLabel("New Score")
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
            if event.button() == Qt.LeftButton:
                # Switch the StackedWidget to Index 1 (Score View)
                view_switcher.setCurrentIndex(1)
                
                # 2. Update the Nav Bar visuals so "Score" is selected
                # We access the 'button_group' attribute we added to nav_bar
                if hasattr(nav_bar, 'button_group'):
                    nav_bar.button_group.button(1).setChecked(True)
            
            event.accept()
    new_score_button = ClickableButton()
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
        from PySide6.QtSvgWidgets import QGraphicsSvgItem
        from PySide6.QtSvg import QSvgRenderer
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
                elif key_str == 'Return' or key_str == 'Enter':
                    self.command.emit("ENTER")
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
            self.paper = None
            
            self.renderer_up = QSvgRenderer(str(ASSETS_DIR / "quarter_note_up.svg"))
            self.renderer_down = QSvgRenderer(str(ASSETS_DIR / "quarter_note_down.svg"))

            self.renderer_treble = QSvgRenderer(str(ASSETS_DIR / "treble.svg"))

            self._draw_paper_and_staves()
            self._create_cursor()
            self.render_treble()

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
            
            self.paper = QGraphicsRectItem(0, 0, PAPER_W, PAPER_H)
            self.paper.setBrush(QBrush(QColor("White")))
            self.scene.addItem(self.paper)
            
            self.view.centerOn(self.paper)

            current_y = MARGIN_Y
            for _ in range(8):
                for i in range(5):
                    y = current_y + (i * LINE_SPACING)
                    line = QGraphicsLineItem(MARGIN_X, y, PAPER_W - MARGIN_X, y)
                    line.setPen(QPen(Qt.GlobalColor.black, 1))
                    line.setZValue(1)
                    line.setParentItem(self.paper)
                current_y += (4 * LINE_SPACING) + SYSTEM_GAP
        
        def add_note(self, x, y, stem="up"):
            note_item = QGraphicsSvgItem()
            
            # Select the correct renderer based on the argument
            if stem == "down":
                note_item.setSharedRenderer(self.renderer_down)
            else:
                note_item.setSharedRenderer(self.renderer_up)
            
            # Scale adjustment (SVGs are 100x120, stave space is ~10px)
            note_item.setScale(0.4)
            note_item.setPos(x, y)
            note_item.setParentItem(self.paper)
            note_item.setZValue(5)

        def render_treble(self):
            treble_item = QGraphicsSvgItem()
            treble_item.setSharedRenderer(self.renderer_treble)
            treble_item.setScale(0.068)
            treble_item.setPos(50.5, 93)
            treble_item.setParentItem(self.paper)
            treble_item.setZValue(5)

        def _create_cursor(self):
            self.cursor = QGraphicsSvgItem()
            self.cursor.setSharedRenderer(self.renderer_down)
            self.cursor.setScale(0.4)
            self.cursor.setPos(80, 81.8)
            self.cursor.setParentItem(self.paper)
            self.cursor.setZValue(6)
            self.scene.addItem(self.cursor)

        def move_cursor_horizontal(self, amount):
            if self.cursor:
                self.cursor.setX(self.cursor.x() + amount)
                self.view.ensureVisible(self.cursor)

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

    # Navigation Bar
    nav_bar = get_nav_bar(view_switcher)

    # View > Home
    home = get_home(view_switcher, nav_bar)
    view_switcher.addWidget(home)

    # View > Score
    score_editor = ScoreEditor()
    score_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    view_switcher.addWidget(score_editor)

    # View > Publish
    view_switcher.addWidget(QLabel("Publish Page"))
    
    # Arrangement
    layout.addWidget(nav_bar)
    layout.addWidget(view_switcher)
    layout.setStretch(1, 1) 

    # Connector
    def handle_global_command(cmd):
        if view_switcher.currentWidget() == score_editor:
            if cmd == "UP":
                score_editor.move_cursor_vertical(-5)
            elif cmd == "DOWN":
                score_editor.move_cursor_vertical(5)
            elif cmd == "ENTER":
                score_editor.add_note(score_editor.cursor.x(), score_editor.cursor.y(), stem="down")
                score_editor.move_cursor_horizontal(30)

    global_listener.command.connect(handle_global_command)

    # Render
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    bootstrapper()
    asset_fetch()
    sys.path.insert(0, str(PKG_DIR))
    main()
