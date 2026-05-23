# Claude Code Global Instructions

This file defines the system-wide context and instructions for Claude Code when running inside this workspace or globally.

## Environment Context
* **OS**: Linux
* **Shell**: bash/zsh
* **Standard Utilities**: eza, bat, ripgrep (rg), fd, zoxide, fzf, jq, delta, lazygit, uv, mise

## Guidelines
* Prefer standard command line utilities managed via `mise` over raw bash scripts.
* Follow clean development guidelines for editing code.
* Refer to custom scripts inside your `skills` or `hooks` folders when automating complex flows.
