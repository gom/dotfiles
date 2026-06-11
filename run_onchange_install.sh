#!/usr/bin/env bash

set -e

# The XDG_CONFIG_HOME directory.
CONFIG_DIR=${XDG_CONFIG_HOME:-"${HOME}/.config"}
mkdir -p "${CONFIG_DIR}"

# --- Declarative Dependencies ---
BREW_PACKAGES=(bash zsh)
BREW_CASKS=(font-noto-nerd-font font-noto-sans-cjk-jp)

ARCH_PACKAGES=(base-devel zsh ttf-noto-nerd noto-fonts-cjk)
APT_PACKAGES=(build-essential zsh fonts-noto-cjk)

# --- System Package Installation ---
echo "Checking and installing system dependencies and fonts..."
if command -v brew &>/dev/null; then
    echo "Using Homebrew..."
    brew install "${BREW_PACKAGES[@]}" || true
    brew install --cask "${BREW_CASKS[@]}" || true
elif command -v paru &>/dev/null; then
    echo "Using paru..."
    paru -S --needed --noconfirm "${ARCH_PACKAGES[@]}"
elif command -v pacman &>/dev/null; then
    echo "Using pacman..."
    sudo pacman -S --needed --noconfirm "${ARCH_PACKAGES[@]}"
elif command -v apt-get &>/dev/null; then
    echo "Using apt..."
    sudo apt-get update
    sudo apt-get install -y "${APT_PACKAGES[@]}"
else
    echo "⚠️ No supported package manager found. Skipping system dependencies."
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
