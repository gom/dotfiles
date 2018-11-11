zplug "zplug/zplug", hook-build:'zplug --self-manage'
zplug "zsh-users/zsh-autosuggestions"
zplug "zsh-users/zsh-completions", use:"src/*", lazy:true
zplug "zsh-users/zsh-history-substring-search"
zplug "zsh-users/zsh-syntax-highlighting", defer:2
zplug "zsh-users/zaw", defer:2

zplug "willghatch/zsh-cdr", lazy:true
zplug "chrissicool/zsh-256color"
zplug "junegunn/fzf-bin", as:command, from:gh-r, rename-to:fzf
zplug "junegunn/fzf", as:command, use:bin/fzf-tmux
zplug "stedolan/jq", \
    from:gh-r, \
    as:command, \
    rename-to:jq

zplug "mollifier/cd-gitroot", lazy:true
zplug 'mollifier/anyframe', \
    use:'anyframe-functions/{actions,selectors,sources,widgets}/*', lazy:true

zplug "mafredri/zsh-async", from:github
zplug "sindresorhus/pure", use:"pure.zsh", from:github, as:theme

zplug "$_ZDOTDIR/functions", from:local
