## auto attach tmux
if type tmux 2>&1 > /dev/null; then
  [ -z $TMUX ] && (tmux -u attach || tmux -u)
fi

## direnv, rbenv, pyenv
if type direnv > /dev/null; then eval "$(direnv hook zsh)"; fi
if type rbenv > /dev/null; then eval "$(rbenv init - --no-rehash)"; fi
if type pyenv > /dev/null; then eval "$(pyenv init - --no-rehash)"; fi

## ssh-agent
[ -e $HOME/.ssh/agent-env ] && source $HOME/.ssh/agent-env
