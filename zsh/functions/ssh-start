ssh-start() {
  AGENTENV="${HOME}/.ssh/agent-env"
  ssh-agent | grep -v echo > ${AGENTENV}
  . ${AGENTENV}
  ssh-add

  echo "please type:"
  echo ". ${AGENTENV}"
}
