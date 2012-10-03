#!/bin/sh
PWD_DIR=`dirname $0`

# emacs
EMACS_DIR=$HOME/.emacs.d
[ ! -e $EMACS_DIR ] && $EMACS_DIR
ln -s $PWD_DIR/init.el $EMACS_DIR
ln -s $PWD_DIR/lisp $EMACS_DIR/elisp

# other config files
ln -s $PWD_DIR/.gitconfig ~
ln -s $PWD_DIR/.gitignore ~
ln -s $PWD_DIR/.screenrc ~
ln -s $PWD_DIR/.vimrc ~
ln -s $PWD_DIR/.vim ~
ln -s $PWD_DIR/.tmux.conf ~

# git complition files
cp $PWD_DIR/.git-completion.sh ~

# shell configs
PATH_DOTFILE=$HOME/.dotfiles
SOURCE_RC="source $PATH_DOTFILE"
for FILENAME_RC in .zshrc .zshenv .bashrc
do
    [[ `tail -n1 ~/$FILENAME_RC` != $SOURCE_RC/$FILENAME_RC ]] && echo $SOURCE_RC/$FILENAME_RC >> $HOME/$FILENAME_RC
done

# Git submodule Update
git submodule update --init --recursive

# Emacs lisp byte-compile
emacs -batch -f batch-byte-compile **/*.el
