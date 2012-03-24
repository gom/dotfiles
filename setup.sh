#!/bin/sh
PWD_DIR=$HOME/.dotfiles

# emacs
ln -s $PWD_DIR/init.el ~/.emacs.d/
ln -s $PWD_DIR/lisp ~/.emacs.d/elisp

# other config files
ln -s $PWD_DIR/.gitconfig ~
ln -s $PWD_DIR/.screenrc ~
ln -s $PWD_DIR/.vimrc ~
ln -s $PWD_DIR/.vim ~

# shell configs
echo 'source $HOME/.dotfiles/.zshrc' >> $HOME/.zshrc
echo 'source $HOME/.dotfiles/.zshenv' >> $HOME/.zshenv
echo 'source $HOME/.dotfiles/.bashrc' >> $HOME/.bashrc

# Git submodule Update
git submodule update --init --recursive

# Emacs lisp byte-compile
emacs -batch -f batch-byte-compile **/*.el
