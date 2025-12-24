bulk_pull() {
  PWD="${1}"
  echo "\e[31mPull all the repositories under the ${PWD}...\e[m"
#PWD="$(cd $(dirname $0) && pwd)"

  for d in $(env find ${PWD} -maxdepth 2 -name '.git' -type d | env sed -e 's/\/\.git//'); do
    pushd "${d}"
    echo -e "\e[31mChecking ${d} ...\e[m"
    git remote update
    if [ -n "$(git branch | env grep -E '\* (main|master)')" ]; then
      git pull --rebase
      git gc
    else
      git status
      echo -e "\e[31m${d} is not on main branch.\e[m Check it later"
    fi
    popd
  done
}
