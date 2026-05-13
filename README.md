# LNote

A modern text editor for Linux, inspired by Windows 11 Notepad.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- Tabs — open multiple files, drag to reorder
- Dark / Light theme toggle
- Line numbers + current line highlight
- Find & Replace panel (Ctrl+F)
- Word wrap toggle (Alt+Z)
- Zoom in/out/reset (Ctrl+= / Ctrl+- / Ctrl+0)
- Auto-indent
- Recent files list
- Date/time insert (F5)
- Open files from command line: `lnote file.txt`
- Remembers window size and settings between sessions

## Install

```bash
curl -sSL https://raw.githubusercontent.com/rasim-ismayilov/lnote/main/install.sh | bash
```

Then run:

```bash
lnote
```

Or find **LNote** in your application launcher.

## Uninstall

```bash
curl -sSL https://raw.githubusercontent.com/rasim-ismayilov/lnote/main/uninstall.sh | bash
```

## Requirements

- Python 3.10+
- PyQt6 (installed automatically by the install script)

## Keyboard shortcuts

| Action | Shortcut |
|---|---|
| New tab | Ctrl+T |
| Open | Ctrl+O |
| Save | Ctrl+S |
| Save as | Ctrl+Shift+S |
| Close tab | Ctrl+W |
| Find & Replace | Ctrl+F |
| Select all | Ctrl+A |
| Undo / Redo | Ctrl+Z / Ctrl+Y |
| Word wrap | Alt+Z |
| Zoom in / out | Ctrl+= / Ctrl+- |
| Reset zoom | Ctrl+0 |
| Date & time | F5 |

## License

MIT
