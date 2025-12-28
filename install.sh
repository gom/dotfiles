#!/bin/sh

set -e

# The directory of this script.
DOTFILES_DIR=$(cd "$(dirname "$0")"; pwd)

# The XDG_CONFIG_HOME directory.
CONFIG_DIR=${XDG_CONFIG_HOME:-"${HOME}/.config"}

# Create the XDG_CONFIG_HOME directory if it doesn't exist.
mkdir -p "${CONFIG_DIR}"

# A function to safely create a symlink.
# It will back up an existing file or directory at the destination.
safe_symlink() {
    local src=${1}
    local dst=${2}

    if [ -e "${dst}" ] || [ -L "${dst}" ]; then
        if [ "$(readlink "${dst}")" = "${src}" ]; then
            echo "✔ Already linked: ${dst} -> ${src}"
            return
        fi
        echo "Moving ${dst} to ${dst}.bak"
        mv "${dst}" "${dst}.bak"
    fi
    echo "Linking ${dst} -> ${src}"
    ln -s "${src}" "${dst}"
}

# Symlink all directories from our config to the user's .config
for config in "${DOTFILES_DIR}/config/"*; do
    if [ -d "${config}" ]; then
        safe_symlink "${config}" "${CONFIG_DIR}/$(basename "${config}")"
    fi
done

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

# The rest of your setup for zsh and vimrc.
# This part is still not ideal because it appends on every run.
# A better way would be to check if the line already exists.
append_to_file() {
    local line="$1"
    local file="$2"
    [ -f "$file" ] || touch "$file"
    grep -Fxq "$line" "$file" || echo "$line" >> "$file"
}
append_to_file "source ${DOTFILES_DIR}/zsh/zshenv" $HOME/.zshenv
append_to_file "source ${DOTFILES_DIR}/zsh/zshrc" $HOME/.zshrc
append_to_file "source ${DOTFILES_DIR}/config/vim/rc/vimrc" $HOME/.vimrc
append_to_file "source ${DOTFILES_DIR}/.bashrc" $HOME/.bashrc
