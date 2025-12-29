
setopt complete_aliases
has_alias() {
    local name="$1"
    local primary="$2"
    local fallback="$3"

    if (( ${+commands[${primary[(w)1]}]} )); then
        alias "${name}"="${primary}"
    elif [[ -n "${fallback}" ]]; then
        alias "${name}"="${fallback}"
    fi
}

has_alias ls 'eza --group-directories-first --git' 'ls -F'
has_alias tree 'eza --tree --icons'

has_alias grep 'rg' 'grep --color=auto'
has_alias cat 'bat --plain'
has_alias less 'bat --plain'
has_alias find 'fd'
has_alias diff 'delta'
has_alias du 'dust'
has_alias ps 'procs'
has_alias cd 'z'

has_alias ll 'eza -l --group-directories-first --git'
has_alias la 'eza -la --group-directories-first --git'

has_alias vi ${EDITOR}
has_alias vim ${EDITOR}

alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

alias pd='pushd'
alias po='popd'
alias gd='dirs -v; echo -n "select number: "; read newdir; cd +"${newdir}"'
alias lss='less -MN'

# zellij (zj to avoid conflict with zoxide)
alias zj='SHELL=$(which zsh) zellij attach -c main'

alias g='git'
alias lg='lazygit'

alias -g L='| less'
alias -g H='| head'
alias -g T='| tail'
alias -g G='| grep'
alias -g W='| wc'
alias -g S='| sed'
alias -g A='| awk'
