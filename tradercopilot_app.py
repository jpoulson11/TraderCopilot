"""
TraderCopilot single-file bundle
Run:  python tradercopilot_app.py
"""

import os, sys, json, asyncio
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPlainTextEdit, QSplitter,
    QTableWidget, QToolBar, QAction, QWidget, QVBoxLayout, QTableWidgetItem
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
import qdarkstyle
try:
    import openai
except ImportError:
    openai = None

APP_NAME = "TraderCopilot"
APP_DIR = Path(os.getenv("APPDATA", ".")) / APP_NAME
APP_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS = APP_DIR / "settings.json"

def load_settings():
    if SETTINGS.exists():
        try:
            return json.loads(SETTINGS.read_text())
        except Exception:
            pass
    return {"openai_key": ""}

def save_settings(data):
    SETTINGS.write_text(json.dumps(data, indent=2))

class GPTChat:
    def __init__(self):
        self.settings = load_settings()
        self.api_key = self.settings.get("openai_key")
        if openai:
            openai.api_key = self.api_key

    async def ask(self, prompt: str) -> str:
        if not openai:
            return "⚠️ OpenAI SDK missing. Run 'pip install openai'."
        if not self.api_key:
            return "⚠️ Please set your OpenAI key (settings.json)."
        try:
            resp = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ Error: {e}"

class Worker(QThread):
    finished = Signal(str)
    def __init__(self, prompt: str, chat: GPTChat):
        super().__init__()
        self.prompt = prompt
        self.chat = chat
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ans = loop.run_until_complete(self.chat.ask(self.prompt))
        self.finished.emit(ans)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TraderCopilot")
        self.resize(1280, 720)

        # Toolbar
        tb = QToolBar()
        self.addToolBar(tb)
        self.act_analyze = QAction("Analyze Screen (stub)", self)
        tb.addAction(self.act_analyze)

        # Split layout
        splitter = QSplitter(Qt.Horizontal)
        self.chat_view = QTextEdit(readOnly=True)
        self.chat_input = QPlainTextEdit()
        self.chat_input.setPlaceholderText("Ctrl+Enter to send…")

        left = QSplitter(Qt.Vertical)
        left.addWidget(self.chat_view)
        left.addWidget(self.chat_input)

        self.main_thread = QTextEdit(readOnly=True)
        self.pos_table = QTableWidget(0, 6)
        self.pos_table.setHorizontalHeaderLabels([
            "Instrument", "Side", "Qty", "Entry", "P&L", "Status"
        ])

        splitter.addWidget(left)
        splitter.addWidget(self.main_thread)
        splitter.addWidget(self.pos_table)

        cw = QWidget()
        lay = QVBoxLayout(cw)
        lay.addWidget(splitter)
        self.setCentralWidget(cw)

        # Chat engine
        self.chat_engine = GPTChat()
        self.chat_input.keyPressEvent = self._chat_keypress

    # --- Chat helpers ---
    def _chat_keypress(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter) and e.modifiers() & Qt.ControlModifier:
            self._send_chat()
        else:
            QPlainTextEdit.keyPressEvent(self.chat_input, e)

    def _send_chat(self):
        prompt = self.chat_input.toPlainText().strip()
        if not prompt:
            return
        self.chat_view.append(f"<b>You:</b> {prompt}")
        self.chat_input.clear()
        worker = Worker(prompt, self.chat_engine)
        worker.finished.connect(self._display_reply)
        worker.start()

    def _display_reply(self, text):
        self.chat_view.append(f"<b>GPT‑4o:</b> {text}")

# --- Entry point ---

def launch():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch()
