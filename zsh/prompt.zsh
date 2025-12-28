## Prompt
autoload -Uz colors && colors
autoload -Uz promptinit && promptinit

setopt no_flow_control      # disabled C-s, C-q
setopt no_beep
setopt no_list_beep
setopt no_hist_beep
setopt interactive_comments # behind '#' is comment in cmd line
WORDCHARS=${WORDCHARS:s,/,,}

## Log
#watch="all"    # watching login and logout
case ${OSTYPE} in
  linux*)
    log # show watching log
    ;;
esac

## Job
setopt no_tify # when bg job finish, notify me.
setopt nomatch
setopt ignore_eof # ignore logout when touch ^D
setopt rm_star_wait # wait for confirmation when using rm *
setopt long_list_jobs
REPORTTIME=3

## Colors
export LSCOLORS=GxFxCxDxBxegedabagacad
export CLICOLOR=1
