update() {
  # Update all packages and plugins
  echo "\e[31mUpdating system packages...\e[m"
  # MacOS
  if [[ $(uname) == "Darwin" ]]; then
    brew update && brew upgrade
  # Arch Linux
  elif command -v paru &>/dev/null; then
    paru -Syu --skipreview
  elif command -v pacman &>/dev/null; then
    sudo pacman -Syu --noconfirm
  # Debian/Ubuntu
  elif command -v apt-get &>/dev/null; then
    sudo apt-get update && sudo apt-get upgrade -y
  elif command -v dnf &>/dev/null; then
    sudo dnf upgrade --refresh -y
  # Fedora
  elif command -v yum &>/dev/null; then
    sudo yum update -y
  else
    echo "No command is available. Please install one of them to manage packages."
    return 1
  fi

  # Update rust
  if command -v rustup >/dev/null; then
    echo "\e[31mUpdating Rust toolchain...\e[m"
    rustup update
  else
    echo "rustup is not installed. Skipping Rust updates."
  fi

  # update asdf plugins
  if command -v asdf &>/dev/null; then
    echo "\e[31mUpdating asdf plugins...\e[m"
    asdf plugin update --all
  else
    echo "asdf is not installed. Skipping asdf plugin updates." 
  fi

  # Update all git repositories in $HOME/src
  bulk_pull $HOME/src

  # Update zinit plugins
  echo "\e[31mUpdating zinit plugins...\e[m"
  zinit update --all
  zinit cclear
}
