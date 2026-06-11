#!/bin/sh

set -e

# The XDG_CONFIG_HOME directory.
CONFIG_DIR=${XDG_CONFIG_HOME:-"${HOME}/.config"}
mkdir -p "${CONFIG_DIR}"

# --- Font Installation ---
echo "Checking and installing necessary fonts..."
if command -v brew &>/dev/null; then
    # macOS (and Linux running Homebrew)
    # Use || true to prevent the script from exiting if the user already has them installed and brew complains
    brew install --cask font-noto-nerd-font font-noto-sans-cjk-jp || true
elif command -v paru &>/dev/null; then
    # Arch Linux with paru AUR helper
    paru -S --needed --noconfirm ttf-noto-nerd noto-fonts-cjk
elif command -v pacman &>/dev/null; then
    # Arch Linux default
    sudo pacman -S --needed --noconfirm ttf-noto-nerd noto-fonts-cjk
fi

# --- Mise Installation ---
MISE_INSTALL_PATH="${HOME}/.local/bin/mise"
if [ ! -e "${MISE_INSTALL_PATH}" ]; then
    echo "Installing mise..."
    mkdir -p "$(dirname "${MISE_INSTALL_PATH}")"
    curl https://mise.run | sh
fi

# Install tools via mise
if [ -e "${MISE_INSTALL_PATH}" ]; then
    echo "Installing tools via mise..."
    "${MISE_INSTALL_PATH}" install
fi
