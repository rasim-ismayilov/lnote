LIGHT = {
    'bg':             '#ffffff',
    'bg2':            '#f5f5f5',
    'bg3':            '#e8e8e8',
    'text':           '#1e1e1e',
    'text2':          '#666666',
    'border':         '#d0d0d0',
    'sel_bg':         '#0078d4',
    'sel_fg':         '#ffffff',
    'line_num_bg':    '#f5f5f5',
    'line_num_fg':    '#aaaaaa',
    'cur_line':       '#f0f7ff',
    'tab_active':     '#ffffff',
    'tab_inactive':   '#ececec',
    'toolbar':        '#f8f8f8',
    'statusbar':      '#0078d4',
    'statusbar_fg':   '#ffffff',
    'accent':         '#0078d4',
    'find_bg':        '#ffffff',
    'find_highlight': '#ffeb3b',
}

DARK = {
    'bg':             '#1e1e1e',
    'bg2':            '#252526',
    'bg3':            '#2d2d2d',
    'text':           '#d4d4d4',
    'text2':          '#858585',
    'border':         '#3e3e3e',
    'sel_bg':         '#264f78',
    'sel_fg':         '#ffffff',
    'line_num_bg':    '#1e1e1e',
    'line_num_fg':    '#606060',
    'cur_line':       '#282828',
    'tab_active':     '#1e1e1e',
    'tab_inactive':   '#2d2d2d',
    'toolbar':        '#252526',
    'statusbar':      '#007acc',
    'statusbar_fg':   '#ffffff',
    'accent':         '#007acc',
    'find_bg':        '#252526',
    'find_highlight': '#f9a825',
}


def make_stylesheet(c: dict) -> str:
    return f"""
QMainWindow, QWidget {{
    background-color: {c['bg2']};
    color: {c['text']};
    font-size: 13px;
}}
QMenuBar {{
    background-color: {c['bg2']};
    color: {c['text']};
    border-bottom: 1px solid {c['border']};
    padding: 2px 0;
}}
QMenuBar::item {{
    background: transparent;
    padding: 5px 10px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {c['bg3']};
}}
QMenu {{
    background: {c['bg2']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 24px 7px 12px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {c['accent']};
    color: white;
}}
QMenu::item:disabled {{
    color: {c['text2']};
}}
QMenu::separator {{
    height: 1px;
    background: {c['border']};
    margin: 3px 6px;
}}
QMenu::indicator {{
    width: 18px;
    height: 18px;
    padding-left: 4px;
}}
QTabWidget::pane {{
    border: none;
    background: {c['bg']};
}}
QTabBar {{
    background: {c['bg3']};
    border-bottom: 1px solid {c['border']};
}}
QTabBar::tab {{
    background: {c['tab_inactive']};
    color: {c['text2']};
    padding: 8px 20px 8px 14px;
    border: none;
    border-right: 1px solid {c['border']};
    min-width: 80px;
    max-width: 220px;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background: {c['tab_active']};
    color: {c['text']};
    border-top: 2px solid {c['accent']};
}}
QTabBar::tab:hover:!selected {{
    background: {c['bg']};
    color: {c['text']};
}}
QTabBar::close-button {{
    subcontrol-position: right;
    padding: 2px;
}}
QPlainTextEdit {{
    background: {c['bg']};
    color: {c['text']};
    border: none;
    selection-background-color: {c['sel_bg']};
    selection-color: {c['sel_fg']};
    padding: 0;
}}
QScrollBar:vertical {{
    background: {c['bg2']};
    width: 10px;
    border: none;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c['bg3']};
    border-radius: 5px;
    min-height: 24px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c['text2']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
QScrollBar:horizontal {{
    background: {c['bg2']};
    height: 10px;
    border: none;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {c['bg3']};
    border-radius: 5px;
    min-width: 24px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {c['text2']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
QStatusBar {{
    background: {c['statusbar']};
    color: {c['statusbar_fg']};
    font-size: 12px;
}}
QStatusBar::item {{ border: none; }}
QStatusBar QLabel {{
    color: {c['statusbar_fg']};
    padding: 0 10px;
    border-right: 1px solid rgba(255,255,255,0.3);
}}
QToolButton {{
    background: transparent;
    color: {c['text']};
    border: none;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 16px;
    font-weight: bold;
}}
QToolButton:hover {{
    background: {c['bg3']};
}}
QToolButton:pressed {{
    background: {c['border']};
}}
QPushButton {{
    background: {c['accent']};
    color: white;
    border: none;
    border-radius: 5px;
    padding: 7px 16px;
    font-size: 13px;
    min-width: 70px;
}}
QPushButton:hover {{
    background: {c['accent']}dd;
}}
QPushButton:pressed {{
    background: {c['accent']}aa;
}}
QPushButton[secondary="true"] {{
    background: {c['bg3']};
    color: {c['text']};
    border: 1px solid {c['border']};
}}
QPushButton[secondary="true"]:hover {{
    background: {c['border']};
}}
QLineEdit {{
    background: {c['bg']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 13px;
    selection-background-color: {c['sel_bg']};
}}
QLineEdit:focus {{
    border-color: {c['accent']};
    outline: none;
}}
QCheckBox {{
    color: {c['text']};
    spacing: 6px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1.5px solid {c['border']};
    border-radius: 3px;
    background: {c['bg']};
}}
QCheckBox::indicator:checked {{
    background: {c['accent']};
    border-color: {c['accent']};
    image: url(none);
}}
QLabel {{
    color: {c['text']};
    font-size: 13px;
}}
QMessageBox {{
    background: {c['bg2']};
    color: {c['text']};
}}
QFileDialog {{
    background: {c['bg2']};
    color: {c['text']};
}}
"""
