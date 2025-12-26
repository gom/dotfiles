
setopt complete_aliases
has_alias() {
    if (( $+commands[$2[(w)1]] )); then
        alias "$1"="$2"
    fi
}

case ${OSTYPE} in
  linux*)
    alias ls='ls --color=auto'
    ;;
esac

has_alias ls 'eza --icons'
has_alias tree 'eza --tree --icons'

has_alias 'grep --color=auto' 'rg'
has_alias cat 'bat'
has_alias find 'fd'
has_alias diff 'delta'
has_alias ps 'procs'

has_alias ll 'eza -l --icons --git'
has_alias la 'eza -la --icons --git'

alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

alias pd='pushd'
alias po='popd'
alias gd='dirs -v; echo -n "select number: "; read newdir; cd +"${newdir}"'
alias lss='less -MN'

alias sc='screen'
alias sd='screen -D'
alias t='tmux'
alias ta='tmux attach'
alias td='tmux detach'

# zellij (zj to avoid conflict with zoxide)
alias zj='zellij'
alias za='zellij attach'
alias zd='zellij detach'

alias g='git'

alias -g L='| less'
alias -g H='| head'
alias -g T='| tail'
alias -g G='| grep'
alias -g W='| wc'
alias -g S='| sed'
alias -g A='| awk'
