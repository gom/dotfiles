bindkey -e

zle -N anyframe-widget-cdr
zle -N anyframe-widget-checkout-git-branch
zle -N anyframe-widget-execute-history
zle -N anyframe-widget-put-history
zle -N anyframe-widget-cd-ghq-repository
zle -N anyframe-widget-kill
zle -N anyframe-widget-insert-git-branch
zle -N anyframe-widget-insert-filename

bindkey '^xb' anyframe-widget-cdr
bindkey '^x^b' anyframe-widget-checkout-git-branch

bindkey '^xr' anyframe-widget-execute-history
bindkey '^x^r' anyframe-widget-execute-history

bindkey '^xp' anyframe-widget-put-history
bindkey '^x^p' anyframe-widget-put-history

bindkey '^xg' anyframe-widget-cd-ghq-repository
bindkey '^x^g' anyframe-widget-cd-ghq-repository

bindkey '^xk' anyframe-widget-kill
bindkey '^x^k' anyframe-widget-kill

bindkey '^xi' anyframe-widget-insert-git-branch
bindkey '^x^i' anyframe-widget-insert-git-branch

bindkey '^xf' anyframe-widget-insert-filename
bindkey '^x^f' anyframe-widget-insert-filename
