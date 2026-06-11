# Dotfiles

Managed via [chezmoi](https://chezmoi.io/).

## Install

To set up these dotfiles on a new machine, run the following command (which automatically installs `chezmoi` to `~/.local/bin`, clones this repository, and applies the configurations):

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply [repos]
```

Or, if `chezmoi` is already installed:

```bash
chezmoi init --apply [repos]
```
