# Add the functions directory to fpath and autoload all functions
fpath=(${_ZDOTDIR}/functions ${fpath})
autoload -Uz ${_ZDOTDIR}/functions/*(N:t)

## ssh-agent
[ -e ${HOME}/.ssh/agent-env ] && source ${HOME}/.ssh/agent-env
