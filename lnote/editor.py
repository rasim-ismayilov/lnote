from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt6.QtGui import (
    QColor, QPainter, QFont, QFontMetrics,
    QTextFormat, QTextCursor, QKeyEvent, QPalette,
)


class _LineNumberArea(QWidget):
    def __init__(self, editor: "NoteEditor"):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_width(), 0)

    def paintEvent(self, event):
        self.editor.paint_line_numbers(event)


class NoteEditor(QPlainTextEdit):
    modified_changed = pyqtSignal(bool)
    cursor_moved = pyqtSignal(int, int)   # line, col

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_path: str | None = None

        self._line_num_bg   = QColor('#f5f5f5')
        self._line_num_fg   = QColor('#aaaaaa')
        self._cur_line_col  = QColor('#f0f7ff')

        self._line_area = _LineNumberArea(self)

        self.blockCountChanged.connect(self._update_margin)
        self.updateRequest.connect(self._update_line_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.cursorPositionChanged.connect(self._emit_cursor)
        self.document().modificationChanged.connect(self.modified_changed)

        self._update_margin()
        self._set_font()
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

    # ── Public API ───────────────────────────────────────────────────────────

    @property
    def file_path(self) -> str | None:
        return self._file_path

    @file_path.setter
    def file_path(self, path: str | None):
        self._file_path = path

    def is_modified(self) -> bool:
        return self.document().isModified()

    def mark_clean(self):
        self.document().setModified(False)

    def apply_theme(self, dark: bool):
        if dark:
            self._line_num_bg  = QColor('#1e1e1e')
            self._line_num_fg  = QColor('#606060')
            self._cur_line_col = QColor('#282828')
        else:
            self._line_num_bg  = QColor('#f5f5f5')
            self._line_num_fg  = QColor('#aaaaaa')
            self._cur_line_col = QColor('#f0f7ff')
        self._highlight_current_line()
        self._line_area.update()

    def set_word_wrap(self, on: bool):
        mode = QPlainTextEdit.LineWrapMode.WidgetWidth if on else QPlainTextEdit.LineWrapMode.NoWrap
        self.setLineWrapMode(mode)

    def zoom_in(self):
        self.zoomIn(1)

    def zoom_out(self):
        self.zoomOut(1)

    def zoom_reset(self):
        self._set_font()

    # ── Line numbers ─────────────────────────────────────────────────────────

    def line_number_width(self) -> int:
        digits = max(3, len(str(self.blockCount())))
        return 8 + self.fontMetrics().horizontalAdvance('9') * digits + 8

    def _update_margin(self, _=None):
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def _update_line_area(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_margin()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_width(), cr.height()))

    def paint_line_numbers(self, event):
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), self._line_num_bg)
        painter.setFont(self.font())
        painter.setPen(self._line_num_fg)

        block = self.firstVisibleBlock()
        num = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        h = self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(
                    0, top,
                    self._line_area.width() - 6, h,
                    Qt.AlignmentFlag.AlignRight,
                    str(num + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            num += 1

    # ── Current-line highlight ────────────────────────────────────────────────

    def _highlight_current_line(self):
        selections = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(self._cur_line_col)
            sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            selections.append(sel)
        self.setExtraSelections(selections)

    # ── Cursor signal ─────────────────────────────────────────────────────────

    def _emit_cursor(self):
        cur = self.textCursor()
        self.cursor_moved.emit(cur.blockNumber() + 1, cur.columnNumber() + 1)

    # ── Font / helpers ────────────────────────────────────────────────────────

    def _set_font(self):
        font = QFont()
        font.setFamilies(['Cascadia Code', 'JetBrains Mono', 'Fira Code',
                          'Consolas', 'Liberation Mono', 'Courier New'])
        font.setPointSize(11)
        self.setFont(font)
        self.setTabStopDistance(4 * QFontMetrics(font).horizontalAdvance(' '))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cur = self.textCursor()
            indent = ''
            for ch in cur.block().text():
                if ch in (' ', '\t'):
                    indent += ch
                else:
                    break
            super().keyPressEvent(event)
            if indent:
                self.insertPlainText(indent)
            return
        super().keyPressEvent(event)
