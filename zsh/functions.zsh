# Add the functions directory to fpath and autoload all functions
fpath=(${_ZDOTDIR}/functions ${fpath})
autoload -U ${_ZDOTDIR}/functions/*(:t)

## ssh-agent
[ -e ${HOME}/.ssh/agent-env ] && source ${HOME}/.ssh/agent-env
