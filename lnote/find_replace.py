from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QCheckBox, QLabel, QFrame,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QTextDocument, QTextCursor, QKeyEvent, QColor

from .editor import NoteEditor


class FindReplacePanel(QFrame):
    """Floating panel that overlays the top-right corner of the window."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName('findPanel')
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._editor: NoteEditor | None = None
        self._highlights: list = []
        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        self.setFixedWidth(400)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(6)

        # ── Find row ────────────────────────────────────────────────────────
        fr = QHBoxLayout()
        fr.setSpacing(6)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText('Найти...')
        self.find_input.returnPressed.connect(self.find_next)
        self.find_input.textChanged.connect(self._on_find_changed)

        self.prev_btn = self._icon_btn('◀', 'Предыдущее (Shift+F3)', self.find_prev)
        self.next_btn = self._icon_btn('▶', 'Следующее (F3)', self.find_next)
        self.close_btn = self._icon_btn('✕', 'Закрыть (Esc)', self.close_panel)

        fr.addWidget(self.find_input)
        fr.addWidget(self.prev_btn)
        fr.addWidget(self.next_btn)
        fr.addWidget(self.close_btn)
        root.addLayout(fr)

        # ── Replace row ──────────────────────────────────────────────────────
        rr = QHBoxLayout()
        rr.setSpacing(6)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText('Заменить...')
        self.replace_input.returnPressed.connect(self.replace_one)

        self.rep_one_btn = QPushButton('Заменить')
        self.rep_one_btn.setFixedWidth(90)
        self.rep_one_btn.clicked.connect(self.replace_one)

        self.rep_all_btn = QPushButton('Все')
        self.rep_all_btn.setFixedWidth(50)
        self.rep_all_btn.clicked.connect(self.replace_all)

        rr.addWidget(self.replace_input)
        rr.addWidget(self.rep_one_btn)
        rr.addWidget(self.rep_all_btn)
        root.addLayout(rr)

        # ── Options row ──────────────────────────────────────────────────────
        or_ = QHBoxLayout()
        or_.setSpacing(14)

        self.case_cb = QCheckBox('Рег.')
        self.case_cb.setToolTip('С учётом регистра')
        self.word_cb = QCheckBox('Слово')
        self.word_cb.setToolTip('Только целые слова')

        self.status_lbl = QLabel('')
        self.status_lbl.setObjectName('findStatus')

        or_.addWidget(self.case_cb)
        or_.addWidget(self.word_cb)
        or_.addStretch()
        or_.addWidget(self.status_lbl)
        root.addLayout(or_)

    def _icon_btn(self, text: str, tooltip: str, slot) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty('secondary', True)
        btn.setFixedSize(QSize(28, 28))
        btn.setToolTip(tooltip)
        btn.clicked.connect(slot)
        return btn

    # ── Public ───────────────────────────────────────────────────────────────

    def open_for(self, editor: NoteEditor):
        self._editor = editor
        cur = editor.textCursor()
        if cur.hasSelection():
            self.find_input.setText(cur.selectedText())
        self.find_input.selectAll()
        self.show()
        self.raise_()
        self.find_input.setFocus()
        self._reposition()

    def close_panel(self):
        self.hide()
        if self._editor:
            self._editor.setFocus()

    def update_editor(self, editor: NoteEditor | None):
        self._editor = editor

    # ── Internal ─────────────────────────────────────────────────────────────

    def _flags(self, backward=False) -> QTextDocument.FindFlag:
        flags = QTextDocument.FindFlag(0)
        if self.case_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.word_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        if backward:
            flags |= QTextDocument.FindFlag.FindBackward
        return flags

    def find_next(self):
        self._find(backward=False)

    def find_prev(self):
        self._find(backward=True)

    def _find(self, backward: bool):
        if not self._editor:
            return
        text = self.find_input.text()
        if not text:
            return
        found = self._editor.find(text, self._flags(backward))
        if not found:
            cur = self._editor.textCursor()
            cur.movePosition(
                QTextCursor.MoveOperation.End if backward
                else QTextCursor.MoveOperation.Start
            )
            self._editor.setTextCursor(cur)
            found = self._editor.find(text, self._flags(backward))
        self._set_status('' if found else 'Не найдено')

    def replace_one(self):
        if not self._editor:
            return
        cur = self._editor.textCursor()
        find_text = self.find_input.text()
        if not find_text:
            return
        if cur.hasSelection():
            sel = cur.selectedText()
            match = (sel == find_text) if self.case_cb.isChecked() else (sel.lower() == find_text.lower())
            if match:
                cur.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        if not self._editor:
            return
        text = self.find_input.text()
        if not text:
            return
        replacement = self.replace_input.text()
        doc = self._editor.document()

        cur = QTextCursor(doc)
        cur.movePosition(QTextCursor.MoveOperation.Start)
        self._editor.setTextCursor(cur)

        count = 0
        cur.beginEditBlock()
        while True:
            found = self._editor.find(text, self._flags())
            if not found:
                break
            self._editor.textCursor().insertText(replacement)
            count += 1
        cur.endEditBlock()

        self._set_status(f'Заменено: {count}' if count else 'Не найдено')

    def _on_find_changed(self, _text: str):
        self._set_status('')

    def _set_status(self, msg: str):
        self.status_lbl.setText(msg)

    def _reposition(self):
        if self.parentWidget():
            pw = self.parentWidget()
            margin = 6
            x = pw.width() - self.width() - margin
            y = 0
            self.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close_panel()
        elif event.key() == Qt.Key.Key_F3:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.find_prev()
            else:
                self.find_next()
        else:
            super().keyPressEvent(event)
