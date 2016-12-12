# !/bin/sh

if ! type brew > /dev/null 2>&1; then
  /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

declare -a brews=( \
  'mas' \
  'git' \
  'zsh' \
  'tmux' \
  'direnv' \
  'neovim/neovim/neovim' \
)

for b in ${brews[@]}; do
  brew install $b
done

declare -a casks=( \
  'alfred' \
  'iterm2' \
  'google-chrome' \
  '1password' \
  'sublime-text' \
  'atom' \
  'intellij-idea' \
)

for b in ${casks[@]}; do
  brew cask install $b
done

declare -a mases=( \
  '' \ #line
  '' \ #twitter
  '' \ #todoist
  '' \ #coteditor
  '' \ # theunarchiver
)

for b in ${mases[@]}; do
  mas install $b
done

brew list
brew cask list
mas list
