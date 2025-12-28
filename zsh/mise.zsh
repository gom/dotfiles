## Mise
typeset -gx MISE_DATA_DIR="${XDG_DATA_HOME:-${HOME}/.local/share}/mise"
typeset -gx MISE_INSTALL_PATH="${HOME}/.local/bin/mise"

if [ ! -e "${MISE_INSTALL_PATH}" ]; then
  mkdir -p "$(dirname "${MISE_INSTALL_PATH}")"
  curl https://mise.run/zsh | sh
  mise install
fi
eval "$(mise activate zsh)"
