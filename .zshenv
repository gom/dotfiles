###########
# environment variant
###########

## colors 
export LSCOLORS=GxFxCxDxBxegedabagacad

## Language
export LANGUAGE=ja_JP.UTF-8
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8

# complete list
# -1 : no asking when the list is too large
export LISTMAX=0

## Work Only Mac
if [ `uname` = "Darwin" ]
then
    ## add path (for Mac) 
	GAEJ_SDK=$HOME/lib/appengine-java-sdk/bin
	#PORT_PATH=/opt/local/bin:/opt/local/sbin
	#PYTHONPATH=$HOME/lib/python2.6/site-packages
        PATH=$GAEJ_SDK:$PATH

    ## add manual path
	#PORT_MAN=/opt/local/man
	#MANPATH=$PORT_MAN:$MANPATH
		
    ## user path
	export _JAVA_OPTIONS="-Dfile.encoding=UTF-8"
	export PYTHONSTARTUP=$HOME/.pyrc.py
	#export CLOJURE_EXT=~/.clojure
fi

# colors
export CLICOLOR=1

# Android
ANDROIDSDK_PATH=$HOME/lib/android-sdk/platform-tools
ANDROIDSDK_TOOLS_PATH=$HOME/lib/android-sdk/tools
ANDROIDNDK_PATH=$HOME/lib/android-ndk
PATH=$ANDROIDSDK_PATH:$ANDROIDNDK_PATH:$ANDROIDSDK_TOOLS_PATH:$PATH

# ccache
[ -e /usr/lib/ccache ] && PATH=/usr/lib/ccache:$PATH
# rbenv
[ -e $HOME/.rbenv/bin ] && PATH=$HOME/.rbenv/bin:$PATH
# mysql
[ -e /usr/local/mysql/bin ] && PATH=/usr/local/mysql/bin:$PATH
# nvm
[ -e $HOME/src/nvm ] && source $HOME/src/nvm/nvm.sh

HOME_BIN=~/bin
PATH=$HOME_BIN:$PATH

## Pager
export LESSCHARSET=utf-8
export LESS=-R
export LV='-la -Ou8'

## editor
EDITOR=/usr/local/bin/vim
export PATH EDITOR
