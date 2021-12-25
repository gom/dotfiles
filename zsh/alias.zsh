
setopt complete_aliases

case ${OSTYPE} in
  linux*)
    alias ls='ls --color=auto'
    ;;
esac

alias ls='exa'
alias grep='rg'
alias cat='bat'
alias find='fd'

alias ll='ls -lhF'
alias la='ls -la'
#alias grep='grep --color=auto'

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

alias -g L='| less'
alias -g H='| head'
alias -g T='| tail'
alias -g G='| grep'
alias -g W='| wc'
alias -g S='| sed'
alias -g A='| awk'

