#!/bin/zsh
zstyle :compinstall filename '~/.zshrc'
#fpath=(~/.zsh.d/completion $fpath)
fpath+=~/.zsh.d

autoload -Uz bashcompinit && bashcompinit

zstyle ':completion:*' format '%B%d%b'
zstyle ':completion:*' group-name ''
zstyle ':completion:*:default' menu select=2        #use emacs keybind
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z} r:|[._-]=*' # ignore case
zstyle ':completion:*' completer \
      _oldlist _complete _match _history _ignored _approximate _prefix
zstyle ':completion:*' use-cache yes
zstyle ':completion:*' verbose yes
zstyle ':completion:sudo:*' environ PATH="${SUDO_PATH}:${PATH}"
zstyle ':completion:*:default' list-colors "${LSCOLORS}"
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([%0-9]#)*=0=01;31'

# cdr http://blog.n-z.jp/blog/2013-11-12-zsh-cdr.html
if [[ -n $(echo ${^fpath}/chpwd_recent_dirs(N)) && -n $(echo ${^fpath}/cdr(N)) ]]; then
  autoload -Uz chpwd_recent_dirs cdr add-zsh-hook
  add-zsh-hook chpwd chpwd_recent_dirs
  zstyle ':completion:*:*:cdr:*:*' menu selection
  zstyle ':completion:*' recent-dirs-insert both
  zstyle ':chpwd:*' recent-dirs-max 500
  zstyle ':chpwd:*' recent-dirs-default true
  zstyle ':chpwd:*' recent-dirs-file "${XDG_CACHE_HOME:-${HOME}/.cache}/shell/chpwd-recent-dirs"
  zstyle ':chpwd:*' recent-dirs-pushd true
fi

setopt complete_in_word
setopt glob_complete
setopt extended_glob
setopt numeric_glob_sort    # sort as numeric order
setopt mark_dirs            # add / when the path is directory
setopt hist_expand
setopt auto_list            # display autocomplete list by ^I
setopt list_types        # display file types in complete list
setopt auto_menu         # switch items by TAB
setopt magic_equal_subst # able to complete after '='
setopt print_eight_bit   # display Japanese

if [ -n "${FASTBOOT_ZSH}" ]; then
  autoload -Uz compinit
  if [[ -n ${_ZDOTDIR:-${HOME}}/.zcompdump(#qN.mh+24) ]]; then
    compinit -u
  else
    compinit -C
  fi
fi
