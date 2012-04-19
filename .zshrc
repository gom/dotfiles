# key bind
bindkey -e

# prompt
autoload -U colors && colors
PROMPT="${USER}@${HOST} %(!.#.$) "

autoload -Uz vcs_info
zstyle ':vcs_info:*' formats '(%s)-[%b]'
zstyle ':vcs_info:*' actionformats '(%s)-[%b|%a]'
precmd () {
    psvar=()
    LANG=en_US.UTF-8 vcs_info
    [[ -n "$vcs_info_msg_0_" ]] && psvar[1]="$vcs_info_msg_0_"
}
RPROMPT="%1(v|%F{green}%1v%f|)"
RPROMPT+="[%~]"

## auto complete
zstyle :compinstall filename '~/.zshrc'
autoload -Uz compinit
compinit
autoload bashcompinit
bashcompinit
if [ -f ~/.gitcompletion.sh ]; then source ~/.gitcompletion.sh; fi
zstyle ':completion:*:default' menu select=1        #use emacs keybind
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}' # ignore case

setopt auto_pushd        # cd to pushd
setopt pushd_ignore_dups
setopt pushd_to_home     # pushd with no argument, go home.
setopt auto_cd
setopt auto_menu
setopt list_types        # display file types in complete list
setopt magic_equal_subst # able to complete after '='
setopt print_eight_bit   # display Japanese

#eval `dircolors`
zstyle ':completion:*:default' list-colors ${LS_COLORS}
zstyle ':completion:*:default' list-colors ${LSCOLORS}
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([%0-9]#)*=0=01;31'

## history
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000
function history-all { history -E 1 } # output all histories

autoload history-search-end
zle -N history-beginning-search-backward-end history-search-end
zle -N history-beginning-search-forward-end history-search-end

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

## shell options
setopt no_flow_control      # disabled C-s, C-q
setopt no_beep
setopt auto_list            # display autocomplete list by ^I
setopt extended_glob
setopt interactive_comments # behind '#' is comment in cmd line
setopt numeric_glob_sort

watch="all"    # watching login and logout
log
setopt no_tify # when bg job finish, notify me.
setopt nomatch

# Work only Mac
case ${OSTYPE} in
    freebsd*|darwin*)
		    function e()
		    {
	          # Open file with Emacs.app
            emacsclient -n ${*:-.} 2>/dev/null && return 0
				    if [ -e $1 ] || touch $1; then
						    open -a /Applications/Emacs.app ${*:-.}
				    fi
		    }
        ;;
    linux*)
		    alias ls='ls --color=auto'
        ;;
esac

## set alias
setopt complete_aliases

alias ll='ls -l'
alias la='ls -la'
alias grep='grep --color=auto'
alias ec='emacsclient .'
alias em='emacs -nw -fs'

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

## others
umask 022
if [[ -s `which screen` ]]; then screen -r; fi
if [[ -s `which tmux` ]]; then tmux attach; fi

## rbenv settings
if [[ -s `which rbenv` ]] ; then eval "$(rbenv init -)" ; fi

## RVM settings
if [[ -s $HOME/.rvm/scripts/rvm ]] ; then source $HOME/.rvm/scripts/rvm ; fi

## for Emacs Shell
[[ $EMACS = t ]] && unsetopt zle
## for tramp
case "$TERM" in
  dumb | emacs)
    PROMPT="%m:%~> "
    unsetopt zle
    ;;
esac

grm() {
  git status | grep deleted: | awk '{ print $3 }' | xargs git rm
}
