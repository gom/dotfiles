autoload -Uz colors && colors

setopt prompt_subst
setopt prompt_percent
setopt transient_rprompt
PROMPT="${USER}@${HOST} %(!.#.$) "

autoload -Uz add-zsh-hook
autoload -Uz vcs_info
zstyle ':vcs_info:*' formats '(%s)-[%b]'
zstyle ':vcs_info:*' actionformats '(%s)-[%b|%a]'
_update_prompt() {
    psvar=()
    LANG=C vcs_info >&/dev/null
    [[ -n "$vcs_info_msg_0_" ]] && psvar[1]="$vcs_info_msg_0_"
}
add-zsh-hook precmd _update_prompt
RPROMPT="%1(v|%F{green}%1v%f|)"
RPROMPT+="[%~]"

setopt no_flow_control      # disabled C-s, C-q
setopt no_beep
setopt interactive_comments # behind '#' is comment in cmd line
WORDCHARS=${WORDCHARS:s,/,,}

show_virtual_env() {
  if [ -n "$VIRTUAL_ENV" ]; then
    echo "(venv:${VIRTUAL_ENV##*/})"
  fi
}

PS1='$(show_virtual_env)'$PS1
