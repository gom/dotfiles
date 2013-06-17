#!/bin/sh
RBENV_DIR=$HOME/.rbenv
PLUGIN_DIR=$RBENV_DIR/plugins
git clone https://github.com/sstephenson/rbenv.git $RBENV_DIR
mkdir -p $PLUGIN_DIR
git clone https://github.com/sstephenson/ruby-build.git $PLUGIN_DIR/ruby-build
eval "$(rbenv init)"
echo 'Add setting to your .zshrc: eval "$(rbenv init -)"'
