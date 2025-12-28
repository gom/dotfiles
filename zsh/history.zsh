## History
HISTFILE=~/.zsh_history
HISTSIZE=10000000
SAVEHIST=${HISTSIZE}
function history-all { history -E 1 } # output all histories

## History search
autoload history-search-end
zle -N history-beginning-search-backward-end history-search-end
zle -N history-beginning-search-forward-end history-search-end

## History options
setopt extended_history     # write datetime to history
setopt append_history       # add .zsh_history
setopt inc_append_history   # add history with incremental
setopt hist_ignore_all_dups # when dups command on history, delete old one
setopt hist_ignore_dups     # ignore same cmd
setopt hist_ignore_space    # when cmd starting space, ignore history
setopt share_history
setopt hist_no_store        # no store in history, `history` cmd.
setopt hist_reduce_blanks
setopt hist_verify
