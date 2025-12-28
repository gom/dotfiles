bindkey -e

# anyframe
zle -N anyframe-widget-checkout-git-branch
zle -N anyframe-widget-kill
zle -N anyframe-widget-insert-git-branch
zle -N anyframe-widget-insert-filename

bindkey '^x^b' anyframe-widget-checkout-git-branch
bindkey '^x^k' anyframe-widget-kill
bindkey '^x^i' anyframe-widget-insert-git-branch
bindkey '^x^f' anyframe-widget-insert-filename

# fzf
bindkey -r "^T"
bindkey "^[t" fzf-file-widget
