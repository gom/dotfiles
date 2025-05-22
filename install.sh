#!/bin/sh
PWD_DIR=$(cd $(dirname $0);pwd)
CONFIG_DIR=${XDG_CONFIG_HOME:-"$HOME/.config"}
mkdir -p $CONFIG_DIR

# other config files
ln -s $PWD_DIR/vim ~/.vim
ln -s $PWD_DIR/gem $CONFIG_DIR/
ln -s $PWD_DIR/git $CONFIG_DIR/
ln -s $PWD_DIR/tmux $CONFIG_DIR/
ln -s $PWD_DIR/direnv $CONFIG_DIR/
ln -s $PWD_DIR/alacritty $CONFIG_DIR/

echo "source $PWD_DIR/zsh/zshenv" >> ~/.zshenv
echo "source $PWD_DIR/zsh/zshrc" >> ~/.zshrc
echo "source $PWD_DIR/vim/rc/vimrc" >> ~/.vimrc
