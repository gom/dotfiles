typeset -gx ZPLUG_HOME=$ZDOTDIR/zplug
typeset -gx ZPLUG_USE_CACHE=true

if [ ! -d "$ZPLUG_HOME" ]; then
  git clone https://github.com/zplug/zplug.git $ZPLUG_HOME
fi

source $ZPLUG_HOME/init.zsh

zplug "zplug/zplug"

zplug "zsh-users/zsh-autosuggestions"
zplug "zsh-users/zsh-completions"
zplug "zsh-users/zsh-history-substring-search"
zplug "zsh-users/zsh-syntax-highlighting", nice:10
zplug "zsh-users/zaw", nice:10

zplug "mrowa44/emojify", as:command, use:emojify
zplug "willghatch/zsh-cdr"
zplug "Tarrasch/zsh-functional"
zplug "chrissicool/zsh-256color"
zplug "junegunn/fzf-bin", as:command, from:gh-r, rename-to:fzf
zplug "junegunn/fzf", as:command, use:bin/fzf-tmux
zplug "stedolan/jq", \
      from:gh-r, \
      as:command, \
      rename-to:jq
zplug "b4b4r07/emoji-cli", \
      on:"stedolan/jq"

zplug "mollifier/cd-gitroot"
zplug "mollifier/anyframe"

zplug "$ZDOTDIR/functions.zsh", from:local

zplug check --verbose || zplug install
zplug load --verbose
