#!/usr/bin/env bash
# LNote installer
# Usage (from cloned repo):  bash install.sh
# Usage (one-liner):         curl -sSL https://raw.githubusercontent.com/rasim-ismayilov/lnote/main/install.sh | bash

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}  ✔ $*${NC}"; }
info() { echo -e "${BLUE}  → $*${NC}"; }
warn() { echo -e "${YELLOW}  ⚠ $*${NC}"; }
die()  { echo -e "${RED}  ✘ $*${NC}" >&2; exit 1; }

echo -e "\n${BOLD}${BLUE}╔══════════════════════════════════╗"
echo -e "║        LNote  Installer          ║"
echo -e "╚══════════════════════════════════╝${NC}\n"

INSTALL_DIR="$HOME/.local/share/lnote"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
REPO_URL="https://github.com/rasim-ismayilov/lnote"

# ── 1. Python ─────────────────────────────────────────────────────────────────
info "Checking Python..."
command -v python3 &>/dev/null || die "Python 3 not found. Install Python 3.10+ and retry."

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
[[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 10 ]] || die "Python 3.10+ required (found $PY_VER)."
ok "Python $PY_VER"

# ── 2. Download / copy source ─────────────────────────────────────────────────
# Detect if running from a local clone (handles both `bash install.sh` and curl|bash)
_script_dir=""
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "bash" ]]; then
    _script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [[ -n "$_script_dir" && -f "$_script_dir/lnote/__main__.py" ]]; then
    info "Installing from local source..."
    rm -rf "$INSTALL_DIR"
    cp -r "$_script_dir" "$INSTALL_DIR"
    ok "Source copied to $INSTALL_DIR"
else
    command -v git &>/dev/null || die "git not found. Install git and retry."
    info "Cloning from $REPO_URL..."
    rm -rf "$INSTALL_DIR"
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" || die "git clone failed."
    ok "Repository cloned"
fi

# ── 3. PyQt6 ─────────────────────────────────────────────────────────────────
info "Installing PyQt6..."
_pyqt_ok=false

# Already available?
if python3 -c "import PyQt6.QtWidgets" 2>/dev/null; then
    ok "PyQt6 already available"; _pyqt_ok=true
fi

# pacman (Arch / Manjaro / CachyOS / EndeavourOS)
if ! $_pyqt_ok && command -v pacman &>/dev/null; then
    if sudo pacman -S --noconfirm --needed python-pyqt6; then
        ok "PyQt6 installed via pacman"; _pyqt_ok=true
    fi
fi

# apt (Ubuntu / Debian / Mint)
if ! $_pyqt_ok && command -v apt-get &>/dev/null; then
    if sudo apt-get install -y python3-pyqt6; then
        ok "PyQt6 installed via apt"; _pyqt_ok=true
    fi
fi

# dnf (Fedora / RHEL)
if ! $_pyqt_ok && command -v dnf &>/dev/null; then
    if sudo dnf install -y python3-pyqt6; then
        ok "PyQt6 installed via dnf"; _pyqt_ok=true
    fi
fi

# Fallback: venv inside INSTALL_DIR (works on any distro, no root needed)
if ! $_pyqt_ok; then
    info "Creating virtual environment (no system package found)..."
    python3 -m venv "$INSTALL_DIR/.venv" || die "Failed to create venv."
    "$INSTALL_DIR/.venv/bin/pip" install --quiet "PyQt6>=6.4.0" \
        || die "Failed to install PyQt6 in venv."
    ok "PyQt6 installed in venv"
fi

# ── 4. Launcher ───────────────────────────────────────────────────────────────
info "Creating launcher..."
mkdir -p "$BIN_DIR"

# The launcher auto-detects venv vs system Python
cat > "$BIN_DIR/lnote" <<LAUNCHER
#!/usr/bin/env bash
INSTALL_DIR="$INSTALL_DIR"
if [[ -x "\$INSTALL_DIR/.venv/bin/python" ]]; then
    PYTHON="\$INSTALL_DIR/.venv/bin/python"
else
    PYTHON="python3"
fi
export PYTHONPATH="\$INSTALL_DIR:\${PYTHONPATH:-}"
exec "\$PYTHON" -m lnote "\$@"
LAUNCHER
chmod +x "$BIN_DIR/lnote"
ok "Launcher: $BIN_DIR/lnote"

# ── 5. Icon ───────────────────────────────────────────────────────────────────
if [[ -f "$INSTALL_DIR/assets/icon.svg" ]]; then
    mkdir -p "$ICON_DIR"
    cp "$INSTALL_DIR/assets/icon.svg" "$ICON_DIR/lnote.svg"
    command -v gtk-update-icon-cache &>/dev/null \
        && gtk-update-icon-cache -qtf "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    ok "Icon installed"
fi

# ── 6. Desktop entry ──────────────────────────────────────────────────────────
mkdir -p "$APP_DIR"
cat > "$APP_DIR/lnote.desktop" <<DESKTOP
[Desktop Entry]
Name=LNote
GenericName=Text Editor
Comment=Modern text editor for Linux
Exec=$BIN_DIR/lnote %F
Icon=lnote
Terminal=false
Type=Application
Categories=Utility;TextEditor;
MimeType=text/plain;text/x-python;application/json;text/markdown;text/x-shellscript;
StartupNotify=true
StartupWMClass=LNote
Keywords=editor;text;notepad;
DESKTOP
chmod +x "$APP_DIR/lnote.desktop"
command -v update-desktop-database &>/dev/null \
    && update-desktop-database "$APP_DIR" 2>/dev/null || true
ok "Desktop entry installed"

# ── 7. PATH warning ───────────────────────────────────────────────────────────
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    warn "$BIN_DIR is not in your PATH. Add one of these to your shell config:"
    echo -e "   ${BOLD}bash/zsh:${NC}  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo -e "   ${BOLD}fish:${NC}      fish_add_path \$HOME/.local/bin"
    echo ""
fi

echo -e "\n${GREEN}${BOLD}✔ LNote installed successfully!${NC}"
echo -e "  Run:  ${BOLD}lnote${NC}"
echo -e "  Or find LNote in your app launcher.\n"
