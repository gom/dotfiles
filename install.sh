#!/bin/sh
PWD_DIR=$(cd $(dirname $0);pwd)

# other config files
ln -s $PWD_DIR/.gemrc ~
ln -s $PWD_DIR/git/config ~/.gitconfig
ln -s $PWD_DIR/git/ignore ~/.gitignore
ln -s $PWD_DIR/.screenrc ~/.screenrc
ln -s $PWD_DIR/vim ~/.vim
ln -s $PWD_DIR/tmux/tmux.conf ~/.tmux.conf
ln -s $PWD_DIR/direnv/direnvrc ~/.direnvrc

echo "source $PWD_DIR/zsh/zshenv" > ~/.zshenv
echo "source $PWD_DIR/zsh/zshrc" > ~/.zshrc
echo "source $PWD_DIR/vim/rc/vimrc" > ~/.vimrc
