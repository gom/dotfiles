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
        LOCAL_PATH=/usr/local/bin
	#PORT_PATH=/opt/local/bin:/opt/local/sbin
	#PYTHONPATH=$HOME/lib/python2.6/site-packages
        PATH=$LOCAL_PATH:$GAEJ_SDK:$PATH

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
# mysql
[ -e /usr/local/mysql/bin ] && PATH=/usr/local/mysql/bin:$PATH
# nvm
#[ -e $HOME/src/nvm ] && source $HOME/src/nvm/nvm.sh

# rbenv
[ -e $HOME/.rbenv/bin ] && PATH=$HOME/.rbenv/bin:$PATH
# nodebrew
[ -e $HOME/.nodebrew ] && PATH=$HOME/.nodebrew/current/bin:$PATH

# go
if [ -x "`which go`" ]; then
  export _GOROOT=`go env GOROOT`
  export GOPATH=$HOME/.goproj
  PATH=$PATH:$GOPATH/bin:$_GOROOT/bin
fi

HOME_BIN=$HOME/bin
PATH=$HOME_BIN:/usr/local/bin:$PATH

## Pager
export LESSCHARSET=utf-8
export LESS=-R
export LV='-la -Ou8'

## editor
[ -e /usr/local/bin/vim ] && EDITOR=/usr/local/bin/vim
export PATH EDITOR
