#!/usr/bin/env bash
# LNote uninstaller

set -euo pipefail

GREEN='\033[0;32m'; BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'
info() { echo -e "${BLUE}  → $*${NC}"; }
ok()   { echo -e "${GREEN}  ✔ $*${NC}"; }

echo -e "\n${BOLD}LNote Uninstaller${NC}\n"

rm -rf  "$HOME/.local/share/lnote"     && ok "Removed app files"         || true
rm -f   "$HOME/.local/bin/lnote"       && ok "Removed launcher"          || true
rm -f   "$HOME/.local/share/applications/lnote.desktop" && ok "Removed desktop entry" || true
rm -f   "$HOME/.local/share/icons/hicolor/scalable/apps/lnote.svg" && ok "Removed icon" || true

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo -e "\n${GREEN}${BOLD}✔ LNote uninstalled.${NC}\n"
