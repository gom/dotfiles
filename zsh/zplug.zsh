typeset -gx ZPLUG_HOME=$_ZDOTDIR/zplug
typeset -gx ZPLUG_USE_CACHE=true

if [ ! -d "$ZPLUG_HOME" ]; then
  git clone https://github.com/zplug/zplug.git $ZPLUG_HOME
fi

source $ZPLUG_HOME/init.zsh
source $_ZDOTDIR/zplug_plugins.zsh

zplug check || zplug install
zplug load
