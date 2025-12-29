typeset -gx ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

if [ ! -d "${ZINIT_HOME}" ]; then
  mkdir -p "$(dirname "${ZINIT_HOME}")"
  git clone https://github.com/zdharma-continuum/zinit.git "${ZINIT_HOME}"
fi

source ${ZINIT_HOME}/zinit.zsh
source ${_ZDOTDIR}/zinit_plugins.zsh

fpath=(${ASDF_DATA_DIR:-${HOME}/.asdf}/completions ${fpath})
autoload -Uz compinit && compinit -u
autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit
