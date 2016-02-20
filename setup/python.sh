#!/usr/bin/zsh

# pythonz
curl -kL https://raw.github.com/saghul/pythonz/master/pythonz-install | bash

# pyenv
git clone https://github.com/yyuu/pyenv.git ~/.pyenv
source $HOME/.zshrc && rehash

# pip
[ ! -e "`which pip`" ] && curl -kL https://bootstrap.pypa.io/get-pip.py | python
sudo pip install virtualenv 
