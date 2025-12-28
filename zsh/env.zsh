
export GPG_TTY=$(tty)

if (( $+commands[nvim] )); then
    export EDITOR='nvim'
elif [ -e /usr/local/bin/vim ]; then
      EDITOR=/usr/local/bin/vim
elif (( $+commands[vim] )); then
    export EDITOR='vim'
else
    export EDITOR='vi'
fi
export VISUAL="$EDITOR"

## Pager
if (( $+commands[bat] )); then
    # bat を PAGER として使う (色付き、ヘルプ表示などが綺麗)
    export PAGER="bat --plain"
    export MANPAGER="bat --plain"
elif (( $+commands[lv] )); then
    export PAGER="lv"
else
    export PAGER="less"
fi
export LESS="-R -i -F"
export LV='-c -la -Ou8'

if [ "${PAGER}" != "lv" ]; then
  alias lv="${PAGER}"
fi
