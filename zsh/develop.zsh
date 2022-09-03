## direnv, rbenv, pyenv
if type direnv > /dev/null; then eval "$(direnv hook zsh)"; fi
if type rbenv > /dev/null; then eval "$(rbenv init - --no-rehash)"; fi
if type pyenv > /dev/null; then eval "$(pyenv init - --no-rehash)"; fi
[ -e "${XDG_CONFIG_HOME:-$HOME/.config}/asdf-direnv/zshrc" ] && source "${XDG_CONFIG_HOME:-$HOME/.config}/asdf-direnv/zshrc"

## ssh-agent
[ -e $HOME/.ssh/agent-env ] && source $HOME/.ssh/agent-env
