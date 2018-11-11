## auto attach screen / tmux
if which screen 2>&1 > /dev/null; then
  screen -q -ls
  num=$?
  if [ $num -eq 9 ]; then
    # screen -xR
  elif [ $num -eq 11 ]; then ## 9: no session, 10: session cannot atattch, 11: session can attach
    screen -xr
  elif [ $num -eq 10 ]; then
    screen -ls
  fi
fi

if type tmux 2>&1 > /dev/null; then
  [ -z $TMUX ] && (tmux -u attach || tmux -u)
fi

## direnv, rbenv, pyenv
if type direnv > /dev/null; then eval "$(direnv hook zsh)"; fi
if type rbenv > /dev/null; then eval "$(rbenv init - --no-rehash)"; fi
if type pyenv > /dev/null; then eval "$(pyenv init - --no-rehash)"; fi

## ssh-agent
[ -e $HOME/.ssh/agent-env ] && source $HOME/.ssh/agent-env
