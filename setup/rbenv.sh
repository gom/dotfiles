#!/bin/sh
RBENV_DIR=$HOME/.rbenv
PLUGIN_DIR=$RBENV_DIR/plugins

[ ! -e $RBENV_DIR ] && git clone https://github.com/sstephenson/rbenv.git $RBENV_DIR
eval "$(rbenv init)"
echo 'Add setting to your .zshrc: eval "$(rbenv init -)"'

[ -e $PLUGIN_DIR ] && exit 0

mkdir -p $PLUGIN_DIR
git clone https://github.com/znz/rbenv-plug.git $PLUGIN_DIR/rbenv-plug

config="$(cd $(dirname $0) && pwd)/rbenv_plugins.txt"
echo $config
for p in `cat ${config}`
do
  rbenv plug $p
done
