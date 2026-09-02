import json
import os
from urllib.parse import unquote

from aqt import gui_hooks
from aqt.qt import QDialog, QDialogButtonBox, QShortcut, QKeySequence, QVBoxLayout, Qt, pyqtSignal, QApplication
from aqt.webview import AnkiWebView


class SvgEditorWebView(AnkiWebView):
    def __init__(self, parent, web_path):
        super().__init__(parent)
        self.web_path = web_path

    def bundledScript(self, fname):
        return f'<script src="{self.web_path}{fname}"></script>'

    def bundledCSS(self, fname):
        return f'<link rel="stylesheet" href="{self.web_path}{fname}">'


class SvgEditorDialog(QDialog):
    saved = pyqtSignal(str)

    def __init__(self, editor, html_content, web_path):
        super().__init__(editor.widget)
        self.editor = editor
        self.web = SvgEditorWebView(self, web_path)
        self.setWindowTitle("Anki SVG editor")
        self.resize(1200, 760)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Save,
            Qt.Orientation.Horizontal,
            self,
        )
        buttons.accepted.connect(self.accept_changes)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.accept_changes)

        template_path = os.path.join(os.path.dirname(__file__), "web", "editor.html")
        with open(template_path, encoding="utf-8") as template_file:
            page = template_file.read()
        page = page.replace("__INITIAL_HTML__", json.dumps(html_content))
        self.web.stdHtml(body=page, css=[], js=[], head="", context=self)

    def accept_changes(self):
        content = self.web.page().runJavaScript("window.getEditedHtml ? window.getEditedHtml() : null")
        if content is not None:
            self.saved.emit(content)
            self.accept()
        else:
            self.web.page().runJavaScript(
                "window.getEditedHtml ? window.getEditedHtml() : null",
                self._finish_with_content,
            )

    def _finish_with_content(self, content):
        if isinstance(content, str):
            self.saved.emit(content)
            self.accept()

    def closeEvent(self, event):
        self.reject()
        event.accept()


def _on_js_message(handled, message: str, context):
    if isinstance(context, SvgEditorDialog) and message.startswith("copy_to_clipboard:"):
        raw_payload = message[len("copy_to_clipboard:"):]
        text = unquote(raw_payload)
        QApplication.clipboard().setText(text)
        return (True, None)
    return handled


gui_hooks.webview_did_receive_js_message.append(_on_js_message)