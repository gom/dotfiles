# Dotfiles

Managed via [chezmoi](https://chezmoi.io/).

## Prerequisites

Before installing the dotfiles on a new machine, ensure the following core dependencies are installed on your system:

- **git**: Required to clone this repository.
- **curl**: Required to download `chezmoi` and `mise`.

*Note: All other dependencies including Zsh, Bash (macOS), build tools, fonts, and language runtimes will be installed automatically during the setup process!*

## Install

To set up these dotfiles on a new machine, run the following command (which automatically installs `chezmoi` to `~/.local/bin`, clones this repository, and applies the configurations):

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply [repos]
```

Or, if `chezmoi` is already installed:

```bash
chezmoi init --apply [repos]
```
