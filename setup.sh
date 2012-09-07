#!/bin/sh
PWD_DIR=`dirname $0`

# emacs
EMACS_DIR=$HOME/.emacs.d
[ ! -e $EMACS_DIR ] && $EMACS_DIR
ln -s $PWD_DIR/init.el $EMACS_DIR
ln -s $PWD_DIR/lisp $EMACS_DIR/elisp

# other config files
ln -s $PWD_DIR/.gitconfig ~
ln -s $PWD_DIR/.screenrc ~
ln -s $PWD_DIR/.vimrc ~
ln -s $PWD_DIR/.vim ~
ln -s $PWD_DIR/.tmux.conf ~

# git complition files
cp $PWD_DIR/.git-completion.sh ~

# shell configs
echo 'source $HOME/.dotfiles/.zshrc' >> $HOME/.zshrc
echo 'source $HOME/.dotfiles/.zshenv' >> $HOME/.zshenv
echo 'source $HOME/.dotfiles/.bashrc' >> $HOME/.bashrc

# Git submodule Update
git submodule update --init --recursive

# Emacs lisp byte-compile
emacs -batch -f batch-byte-compile **/*.el
