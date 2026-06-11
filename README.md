# Dotfiles

Managed via [chezmoi](https://chezmoi.io/).

## Prerequisites

Before installing the dotfiles on a new machine, ensure the following core dependencies are installed on your system:

- **git**: Required to clone this repository.
- **curl**: Required to download `chezmoi` and `mise`.
- **zsh**: The primary shell configuration used.
- **Build Tools**: Required by `mise` to compile language runtimes (e.g., Python, Ruby).
  - macOS: `xcode-select --install`
  - Arch Linux: `sudo pacman -S base-devel`
  - Debian/Ubuntu: `sudo apt install build-essential`
- **bash (macOS only)**: macOS ships with an outdated Bash (v3.2). You must install a modern version (v4.0+) via Homebrew (`brew install bash`) to support the `mapfile` command used in the agent deployment scripts.

## Install

To set up these dotfiles on a new machine, run the following command (which automatically installs `chezmoi` to `~/.local/bin`, clones this repository, and applies the configurations):

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply [repos]
```

Or, if `chezmoi` is already installed:

```bash
chezmoi init --apply [repos]
```
