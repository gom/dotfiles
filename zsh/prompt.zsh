autoload -Uz colors && colors
autoload -Uz promptinit && promptinit

setopt no_flow_control      # disabled C-s, C-q
setopt no_beep
setopt interactive_comments # behind '#' is comment in cmd line
WORDCHARS=${WORDCHARS:s,/,,}

# log
#watch="all"    # watching login and logout

case ${OSTYPE} in
  linux*)
    # Darwin has /usr/bin/log.
    log # show watching log
    ;;
esac

setopt no_tify # when bg job finish, notify me.
setopt nomatch
setopt ignore_eof # ignore logout when touch ^D

# job
setopt long_list_jobs
REPORTTIME=3
