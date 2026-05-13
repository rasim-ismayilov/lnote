import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QToolButton, QFileDialog,
    QMessageBox, QStatusBar, QLabel, QApplication, QWidget,
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence

from .editor import NoteEditor
from .find_replace import FindReplacePanel
from .theme import LIGHT, DARK, make_stylesheet


MAX_RECENT = 12


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._cfg = QSettings('LNote', 'LNote')
        self._dark: bool        = self._cfg.value('dark', False, type=bool)
        self._wrap: bool        = self._cfg.value('wrap', True,  type=bool)
        self._zoom: int         = self._cfg.value('zoom', 0,     type=int)
        self._recent: list[str] = self._cfg.value('recent', [],  type=list)

        self._build_ui()
        self._apply_theme()
        self._restore_geometry()
        self.new_tab()

    # ═══════════════════════════════════════════════════════════════
    # Build UI
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self):
        self.setWindowTitle('LNote')
        self.setMinimumSize(720, 480)

        # ── Tab widget ──────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        add_btn = QToolButton()
        add_btn.setText(' + ')
        add_btn.setToolTip('Новая вкладка (Ctrl+T)')
        add_btn.clicked.connect(self.new_tab)
        self.tabs.setCornerWidget(add_btn, Qt.Corner.TopRightCorner)

        self.setCentralWidget(self.tabs)

        # ── Find/Replace overlay ────────────────────────────────────
        self.find_panel = FindReplacePanel(self.tabs)

        # ── Menus ────────────────────────────────────────────────────
        self._build_menus()

        # ── Status bar ───────────────────────────────────────────────
        self._build_statusbar()

    def _build_menus(self):
        mb = self.menuBar()

        # File
        fm = mb.addMenu('Файл')
        self._act(fm, 'Создать',          'Ctrl+N',       self.new_tab)
        self._act(fm, 'Открыть…',         'Ctrl+O',       self.open_file)
        fm.addSeparator()
        self._act(fm, 'Сохранить',        'Ctrl+S',       self.save_file)
        self._act(fm, 'Сохранить как…',   'Ctrl+Shift+S', self.save_file_as)
        fm.addSeparator()
        self.recent_menu = fm.addMenu('Недавние файлы')
        self._rebuild_recent_menu()
        fm.addSeparator()
        self._act(fm, 'Закрыть вкладку',  'Ctrl+W',       self._close_current_tab)
        fm.addSeparator()
        self._act(fm, 'Выход',            'Ctrl+Q',       self.close)

        # Edit
        em = mb.addMenu('Правка')
        self._act(em, 'Отменить',         'Ctrl+Z',       lambda: self._ed() and self._ed().undo())
        self._act(em, 'Повторить',        'Ctrl+Y',       lambda: self._ed() and self._ed().redo())
        em.addSeparator()
        self._act(em, 'Вырезать',         'Ctrl+X',       lambda: self._ed() and self._ed().cut())
        self._act(em, 'Копировать',       'Ctrl+C',       lambda: self._ed() and self._ed().copy())
        self._act(em, 'Вставить',         'Ctrl+V',       lambda: self._ed() and self._ed().paste())
        em.addSeparator()
        self._act(em, 'Найти и заменить', 'Ctrl+F',       self.show_find)
        em.addSeparator()
        self._act(em, 'Выделить всё',     'Ctrl+A',       lambda: self._ed() and self._ed().selectAll())
        em.addSeparator()
        self._act(em, 'Дата и время',     'F5',           self._insert_dt)

        # View
        vm = mb.addMenu('Вид')

        self._wrap_action = QAction('Перенос слов', self)
        self._wrap_action.setCheckable(True)
        self._wrap_action.setChecked(self._wrap)
        self._wrap_action.setShortcut('Alt+Z')
        self._wrap_action.triggered.connect(self._toggle_wrap)
        vm.addAction(self._wrap_action)

        vm.addSeparator()
        self._act(vm, 'Увеличить',        'Ctrl+=',       self.zoom_in)
        self._act(vm, 'Уменьшить',        'Ctrl+-',       self.zoom_out)
        self._act(vm, 'Обычный размер',   'Ctrl+0',       self.zoom_reset)
        vm.addSeparator()

        self._theme_action = QAction('Тёмная тема', self)
        self._theme_action.setCheckable(True)
        self._theme_action.setChecked(self._dark)
        self._theme_action.triggered.connect(self._toggle_theme)
        vm.addAction(self._theme_action)

        # New-tab shortcut not in menu
        new_tab_action = QAction(self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.new_tab)
        self.addAction(new_tab_action)

    def _act(self, menu, label: str, shortcut: str | None, slot) -> QAction:
        action = QAction(label, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_statusbar(self):
        sb = self.statusBar()
        self._lbl_pos  = QLabel('Строка 1, столбец 1')
        self._lbl_enc  = QLabel('UTF-8')
        self._lbl_lines = QLabel('Строк: 1')
        for lbl in (self._lbl_lines, self._lbl_enc, self._lbl_pos):
            sb.addPermanentWidget(lbl)

    # ═══════════════════════════════════════════════════════════════
    # Tab management
    # ═══════════════════════════════════════════════════════════════

    def new_tab(self) -> NoteEditor:
        editor = NoteEditor()
        editor.apply_theme(self._dark)
        editor.set_word_wrap(self._wrap)
        self._apply_zoom_to(editor)

        editor.modified_changed.connect(lambda mod, e=editor: self._on_modified(e, mod))
        editor.cursor_moved.connect(self._update_pos_label)

        idx = self.tabs.addTab(editor, 'Без имени')
        self.tabs.setCurrentIndex(idx)
        editor.setFocus()
        return editor

    def _tab_label(self, editor: NoteEditor) -> str:
        name = os.path.basename(editor.file_path) if editor.file_path else 'Без имени'
        return ('● ' if editor.is_modified() else '') + name

    def _on_modified(self, editor: NoteEditor, _mod: bool):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) is editor:
                self.tabs.setTabText(i, self._tab_label(editor))
                break
        self._update_window_title()

    def _on_tab_changed(self, _idx: int):
        editor = self._ed()
        self.find_panel.update_editor(editor)
        if editor:
            cur = editor.textCursor()
            self._update_pos_label(cur.blockNumber() + 1, cur.columnNumber() + 1)
            self._lbl_lines.setText(f'Строк: {editor.document().blockCount()}')
        self._update_window_title()

    def _close_tab(self, index: int):
        editor = self.tabs.widget(index)
        if not isinstance(editor, NoteEditor):
            return
        if editor.is_modified():
            name = os.path.basename(editor.file_path) if editor.file_path else 'Без имени'
            reply = QMessageBox.question(
                self, 'Несохранённые изменения',
                f'«{name}» был изменён. Сохранить?',
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                self.tabs.setCurrentIndex(index)
                if not self.save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.new_tab()

    def _close_current_tab(self):
        self._close_tab(self.tabs.currentIndex())

    def _ed(self) -> NoteEditor | None:
        w = self.tabs.currentWidget()
        return w if isinstance(w, NoteEditor) else None

    # ═══════════════════════════════════════════════════════════════
    # File operations
    # ═══════════════════════════════════════════════════════════════

    def open_file(self, path: str | None = None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, 'Открыть файл', os.path.expanduser('~'),
                'Текстовые файлы (*.txt *.md *.rst *.log *.csv *.json *.yaml *.yml '
                '*.toml *.ini *.cfg *.conf *.py *.js *.ts *.html *.css *.sh *.xml);; '
                'Все файлы (*)',
            )
        if not path:
            return

        # Don't open twice
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            if isinstance(ed, NoteEditor) and ed.file_path == path:
                self.tabs.setCurrentIndex(i)
                return

        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                content = f.read()
        except OSError as exc:
            QMessageBox.critical(self, 'Ошибка открытия', str(exc))
            return

        # Reuse current clean empty tab
        editor = self._ed()
        if not (editor and not editor.file_path and not editor.is_modified() and not editor.toPlainText()):
            editor = self.new_tab()

        editor.setPlainText(content)
        editor.file_path = path
        editor.mark_clean()

        idx = self.tabs.indexOf(editor)
        self.tabs.setTabText(idx, self._tab_label(editor))
        self._update_window_title()
        self._add_recent(path)
        self._lbl_lines.setText(f'Строк: {editor.document().blockCount()}')

    def save_file(self) -> bool:
        editor = self._ed()
        if not editor:
            return False
        if not editor.file_path:
            return self.save_file_as()
        return self._write(editor, editor.file_path)

    def save_file_as(self) -> bool:
        editor = self._ed()
        if not editor:
            return False
        default = editor.file_path or os.path.expanduser('~/Без имени.txt')
        path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить как', default,
            'Текстовые файлы (*.txt);;Все файлы (*)',
        )
        if not path:
            return False
        return self._write(editor, path)

    def _write(self, editor: NoteEditor, path: str) -> bool:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
        except OSError as exc:
            QMessageBox.critical(self, 'Ошибка сохранения', str(exc))
            return False
        editor.file_path = path
        editor.mark_clean()
        idx = self.tabs.indexOf(editor)
        self.tabs.setTabText(idx, self._tab_label(editor))
        self._update_window_title()
        self._add_recent(path)
        return True

    # ═══════════════════════════════════════════════════════════════
    # Recent files
    # ═══════════════════════════════════════════════════════════════

    def _add_recent(self, path: str):
        if path in self._recent:
            self._recent.remove(path)
        self._recent.insert(0, path)
        self._recent = self._recent[:MAX_RECENT]
        self._cfg.setValue('recent', self._recent)
        self._rebuild_recent_menu()

    def _rebuild_recent_menu(self):
        self.recent_menu.clear()
        if not self._recent:
            a = self.recent_menu.addAction('(пусто)')
            a.setEnabled(False)
            return
        for p in self._recent:
            a = self.recent_menu.addAction(os.path.basename(p))
            a.setToolTip(p)
            a.triggered.connect(lambda _checked, pp=p: self.open_file(pp))
        self.recent_menu.addSeparator()
        self.recent_menu.addAction('Очистить список', self._clear_recent)

    def _clear_recent(self):
        self._recent = []
        self._cfg.setValue('recent', [])
        self._rebuild_recent_menu()

    # ═══════════════════════════════════════════════════════════════
    # Find / Replace
    # ═══════════════════════════════════════════════════════════════

    def show_find(self):
        editor = self._ed()
        if editor:
            self.find_panel.open_for(editor)

    # ═══════════════════════════════════════════════════════════════
    # View: wrap / zoom / theme
    # ═══════════════════════════════════════════════════════════════

    def _toggle_wrap(self, checked: bool):
        self._wrap = checked
        self._cfg.setValue('wrap', checked)
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            if isinstance(ed, NoteEditor):
                ed.set_word_wrap(checked)

    def zoom_in(self):
        self._zoom += 1
        self._cfg.setValue('zoom', self._zoom)
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            if isinstance(ed, NoteEditor):
                ed.zoom_in()

    def zoom_out(self):
        self._zoom -= 1
        self._cfg.setValue('zoom', self._zoom)
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            if isinstance(ed, NoteEditor):
                ed.zoom_out()

    def zoom_reset(self):
        self._zoom = 0
        self._cfg.setValue('zoom', 0)
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            if isinstance(ed, NoteEditor):
                ed.zoom_reset()

    def _toggle_theme(self, checked: bool):
        self._dark = checked
        self._cfg.setValue('dark', checked)
        self._apply_theme()
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            if isinstance(ed, NoteEditor):
                ed.apply_theme(checked)

    def _apply_theme(self):
        ss = make_stylesheet(DARK if self._dark else LIGHT)
        self.setStyleSheet(ss)
        self.find_panel.setStyleSheet(ss)
        # find panel extra styling
        fp_extra = (
            f"QFrame#findPanel {{ border: 1px solid {'#3e3e3e' if self._dark else '#d0d0d0'};"
            f" border-radius: 6px;"
            f" background: {'#252526' if self._dark else '#ffffff'}; }}"
        )
        self.find_panel.setStyleSheet(ss + fp_extra)

    # ═══════════════════════════════════════════════════════════════
    # Status bar helpers
    # ═══════════════════════════════════════════════════════════════

    def _update_pos_label(self, line: int, col: int):
        self._lbl_pos.setText(f'Строка {line}, столбец {col}')
        editor = self._ed()
        if editor:
            self._lbl_lines.setText(f'Строк: {editor.document().blockCount()}')

    def _update_window_title(self):
        editor = self._ed()
        if editor:
            name = os.path.basename(editor.file_path) if editor.file_path else 'Без имени'
            mod = '● ' if editor.is_modified() else ''
            self.setWindowTitle(f'{mod}{name} — LNote')
        else:
            self.setWindowTitle('LNote')

    # ═══════════════════════════════════════════════════════════════
    # Misc
    # ═══════════════════════════════════════════════════════════════

    def _insert_dt(self):
        editor = self._ed()
        if editor:
            editor.insertPlainText(datetime.now().strftime('%d.%m.%Y %H:%M'))

    def _apply_zoom_to(self, editor: NoteEditor):
        for _ in range(abs(self._zoom)):
            editor.zoom_in() if self._zoom > 0 else editor.zoom_out()

    # ═══════════════════════════════════════════════════════════════
    # Geometry persistence & close
    # ═══════════════════════════════════════════════════════════════

    def _restore_geometry(self):
        geom = self._cfg.value('geometry')
        if geom:
            self.restoreGeometry(geom)
        else:
            self.resize(960, 660)
            screen = QApplication.primaryScreen().geometry()
            self.move(
                (screen.width()  - self.width())  // 2,
                (screen.height() - self.height()) // 2,
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep find panel anchored to top-right
        if self.find_panel.isVisible():
            w = self.find_panel.width()
            self.find_panel.move(self.tabs.width() - w - 6, 0)

    def closeEvent(self, event: QCloseEvent):
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            if not isinstance(ed, NoteEditor):
                continue
            if ed.is_modified():
                name = os.path.basename(ed.file_path) if ed.file_path else 'Без имени'
                reply = QMessageBox.question(
                    self, 'Несохранённые изменения',
                    f'«{name}» был изменён. Сохранить?',
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel,
                )
                if reply == QMessageBox.StandardButton.Save:
                    self.tabs.setCurrentIndex(i)
                    if not self.save_file():
                        event.ignore()
                        return
                elif reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
        self._cfg.setValue('geometry', self.saveGeometry())
        event.accept()
