#!/bin/sh
PWD_DIR=$(cd $(dirname $0);pwd)

# other config files
ln -s $PWD_DIR/vim ~/.vim
ln -s $PWD_DIR/gem $XDG_CONFIG_HOME/
ln -s $PWD_DIR/git $XDG_CONFIG_HOME/
ln -s $PWD_DIR/tmux $XDG_CONFIG_HOME/
ln -s $PWD_DIR/direnv $XDG_CONFIG_HOME/
ln -s $PWD_DIR/alacritty $XDG_CONFIG_HOME/

echo "source $PWD_DIR/zsh/zshenv" >> ~/.zshenv
echo "source $PWD_DIR/zsh/zshrc" >> ~/.zshrc
echo "source $PWD_DIR/vim/rc/vimrc" >> ~/.vimrc
