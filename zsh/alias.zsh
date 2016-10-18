
setopt complete_aliases

case ${OSTYPE} in
  linux*)
    alias ls='ls --color=auto'
    ;;
esac

alias ll='ls -lhF'
alias la='ls -la'
alias grep='grep --color=auto'
alias ec='emacsclient -c -t'
alias em='emacs -nw -fs'

alias rr="command rm -rf"
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

alias pd='pushd'
alias po='popd'
alias gd='dirs -v; echo -n "select number: "; read newdir; cd +"$newdir"'
alias lss='less -MN'

alias sc='screen'
alias sd='screen -D'
alias t='tmux'
alias ta='tmux attach'
alias td='tmux detach'
alias g='git'

alias re='ruby -e'
alias spec='spec -c -fs'

alias -g L='| less'
alias -g H='| head'
alias -g T='| tail'
alias -g G='| grep'
alias -g W='| wc'
alias -g S='| sed'
alias -g A='| awk'

alias utf='export LANG=ja_JP.UTF-8; export LANGUAGE=ja_JP.UTF-8; export LC_ALL=ja_JP.UTF-8'
alias en='export LANG=en; export LANGUAGE=en; export LC_ALL=en'
alias eucjp='export LANG=ja_JP.eucJP; export LANGUAGE=ja_JP.eucJP; export LC_ALL=ja_JP.eucJP'
alias sjis='export LANG=ja_JP.SJIS; export LANGUAGE=ja_JP.SJIS; export LC_ALL=ja_JP.SJIS'

