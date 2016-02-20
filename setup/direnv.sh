#!/usr/bin/zsh

git clone https://github.com/direnv/direnv .direnv
cd .direnv
make install
source $HOME/.zshrc

