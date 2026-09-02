import json
import os

from anki.hooks import addHook
from aqt import mw
from aqt.qt import QKeySequence
from aqt.utils import tooltip

from .dialog import SvgEditorDialog


ADDON_PATH = os.path.dirname(__file__)
WEB_PATH = f"/_addons/{os.path.basename(ADDON_PATH)}/web/"

mw.addonManager.setWebExports(__name__, r"web/.*")


def save_svg_content(editor, field_index, content):
    if not isinstance(content, str):
        tooltip("SVG editor returned invalid content")
        return

    editor.note.fields[field_index] = content
    if not editor.addMode:
        editor.note.flush()
    editor.loadNote(focusTo=field_index)


def open_svg_editor(editor):
    if editor.currentField is None:
        tooltip("No field focused. Select a card field first.")
        return

    field_index = editor.currentField
    editor.saveNow(
        lambda: show_svg_dialog(editor, field_index)
    )


def show_svg_dialog(editor, field_index):
    dialog = SvgEditorDialog(
        editor=editor,
        html_content=editor.note.fields[field_index],
        web_path=WEB_PATH,
    )
    dialog.saved.connect(
        lambda content: save_svg_content(editor, field_index, content)
    )
    dialog.setModal(True)
    dialog.show()
    dialog.web.setFocus()


def setup_editor_button(buttons, editor):
    shortcut = QKeySequence("Ctrl+Alt+S").toString(QKeySequence.SequenceFormat.NativeText)
    button = editor.addButton(
        icon=None,
        cmd="SVG",
        func=lambda e=editor: open_svg_editor(e),
        tip=f"Edit SVGs in the current field ({shortcut})",
        keys=shortcut,
    )
    buttons.append(button)
    return buttons


addHook("setupEditorButtons", setup_editor_button)
