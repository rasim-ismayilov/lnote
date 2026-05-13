#!/usr/bin/env bash
# LNote installer
# Usage (from cloned repo):  bash install.sh
# Usage (one-liner):         curl -sSL https://raw.githubusercontent.com/rasim-ismayilov/lnote/main/install.sh | bash

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}  ✔ $*${NC}"; }
info() { echo -e "${BLUE}  → $*${NC}"; }
warn() { echo -e "${YELLOW}  ⚠ $*${NC}"; }
die()  { echo -e "${RED}  ✘ $*${NC}" >&2; exit 1; }

echo -e "\n${BOLD}${BLUE}╔══════════════════════════════════╗"
echo -e "║        LNote  Installer        ║"
echo -e "╚══════════════════════════════════╝${NC}\n"

# ── Directories ───────────────────────────────────────────────────────────────
INSTALL_DIR="$HOME/.local/share/lnote"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

# ── 1. Check Python ───────────────────────────────────────────────────────────
info "Checking Python..."
if ! command -v python3 &>/dev/null; then
    die "Python 3 not found. Install Python 3.10+ and retry."
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 10 ]]; then
    die "Python 3.10+ required (found $PY_VER)."
fi
ok "Python $PY_VER"

# ── 2. Check / install pip ────────────────────────────────────────────────────
info "Checking pip..."
if ! python3 -m pip --version &>/dev/null; then
    info "Installing pip via ensurepip..."
    python3 -m ensurepip --upgrade || die "Failed to install pip."
fi
ok "pip available"

# ── 3. Install PyQt6 ──────────────────────────────────────────────────────────
info "Installing PyQt6..."

# Try system package manager first (faster, better integrated)
_pyqt_installed=false

if command -v pacman &>/dev/null && pacman -Qi python-pyqt6 &>/dev/null 2>&1; then
    ok "PyQt6 already installed (pacman)"
    _pyqt_installed=true
elif command -v pacman &>/dev/null; then
    if sudo pacman -S --noconfirm python-pyqt6 2>/dev/null; then
        ok "PyQt6 installed via pacman"
        _pyqt_installed=true
    fi
fi

if ! $_pyqt_installed; then
    python3 -m pip install --user --quiet "PyQt6>=6.4.0" || die "Failed to install PyQt6."
    ok "PyQt6 installed via pip"
fi

# ── 4. Download / copy source ─────────────────────────────────────────────────
REPO_URL="https://github.com/rasim-ismayilov/lnote"

if [[ -f "$(dirname "$0")/lnote/__main__.py" ]]; then
    # Running from a cloned / extracted repo
    SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
    info "Installing from local source: $SRC_DIR"
    rm -rf "$INSTALL_DIR"
    cp -r "$SRC_DIR" "$INSTALL_DIR"
    ok "Source copied to $INSTALL_DIR"
else
    # Remote install — clone from GitHub
    if ! command -v git &>/dev/null; then
        die "git not found. Install git or run the installer from a cloned repo."
    fi
    info "Cloning from $REPO_URL ..."
    rm -rf "$INSTALL_DIR"
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" || die "git clone failed."
    ok "Repository cloned"
fi

# ── 5. Create launcher script ─────────────────────────────────────────────────
info "Creating launcher..."
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/lnote" <<EOF
#!/usr/bin/env bash
exec python3 -m lnote "\$@"
EOF
# Inject PYTHONPATH so the module is found regardless of pip install
sed -i "1a export PYTHONPATH=\"$INSTALL_DIR:\$PYTHONPATH\"" "$BIN_DIR/lnote"
chmod +x "$BIN_DIR/lnote"
ok "Launcher: $BIN_DIR/lnote"

# ── 6. Install icon ───────────────────────────────────────────────────────────
if [[ -f "$INSTALL_DIR/assets/icon.svg" ]]; then
    mkdir -p "$ICON_DIR"
    cp "$INSTALL_DIR/assets/icon.svg" "$ICON_DIR/lnote.svg"
    ok "Icon installed"
fi

# ── 7. Install .desktop entry ─────────────────────────────────────────────────
mkdir -p "$APP_DIR"
cat > "$APP_DIR/lnote.desktop" <<EOF
[Desktop Entry]
Name=LNote
GenericName=Text Editor
Comment=Modern text editor for Linux
Exec=$BIN_DIR/lnote %F
Icon=lnote
Terminal=false
Type=Application
Categories=Utility;TextEditor;
MimeType=text/plain;text/x-python;application/json;text/markdown;
StartupNotify=true
StartupWMClass=LNote
Keywords=editor;text;notepad;
EOF
chmod +x "$APP_DIR/lnote.desktop"

# Update icon cache if available
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -qtf "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APP_DIR" 2>/dev/null || true
fi
ok "Desktop entry installed"

# ── 8. PATH check ─────────────────────────────────────────────────────────────
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    warn "$BIN_DIR is not in your PATH."
    echo -e "   Add this line to your ${BOLD}~/.bashrc${NC} or ${BOLD}~/.zshrc${NC} or ${BOLD}~/.config/fish/config.fish${NC}:"
    echo ""
    echo -e "     ${BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}   # bash/zsh"
    echo -e "     ${BOLD}fish_add_path \$HOME/.local/bin${NC}           # fish"
    echo ""
fi

echo -e "\n${GREEN}${BOLD}✔ LNote installed successfully!${NC}"
echo -e "  Run:  ${BOLD}lnote${NC}"
echo -e "  Or search for LNote in your app launcher.\n"
