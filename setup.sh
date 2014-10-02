#!/bin/sh
PWD_DIR=$(cd $(dirname $0);pwd)

# other config files
ln -s $PWD_DIR/.gemrc ~
ln -s $PWD_DIR/.gitconfig ~
ln -s $PWD_DIR/.gitignore ~
ln -s $PWD_DIR/.screenrc ~
ln -s $PWD_DIR/.vim ~
ln -s $PWD_DIR/.tmux.conf ~

ln -s $PWD_DIR/.zsh.d ~

# shell configs
SOURCE_RC='source $HOME/.dotfiles'
for FILENAME_RC in .zsh.d/zshrc .zsh.d/zshenv .bashrc .vimrc .gvimrc
do
    [ ! -e ~/$FILENAME_RC ] && touch ~/$FILENAME_RC
    [[ `tail -n1 ~/$FILENAME_RC` != $SOURCE_RC/$FILENAME_RC ]] && echo $SOURCE_RC/$FILENAME_RC >> $HOME/$FILENAME_RC
done

# Git submodule Update
git submodule update --init --recursive

# emacs
EMACS_DIR=$HOME/.emacs.d
EMACS_SRC=$PWD_DIR/emacs
[ ! -e $EMACS_DIR ] && mkdir $EMACS_DIR
[ ! -e $EMACS_DIR/init.el ] && ln -s $EMACS_SRC/init.el $EMACS_DIR
[ ! -e $EMACS_DIR/elisp ] && ln -s $EMACS_SRC/el $EMACS_DIR/elisp
# Emacs lisp byte-compile
[ -s "`which emacs`" ] && emacs -batch -f batch-byte-compile **/*.el #> /dev/null 2>&1
