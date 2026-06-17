# Design Spec: Standardize Chezmoi Config Layout

## 1. Objective
This repository currently manages several `~/.config` trees through an extra indirection layer: canonical files live under `config/`, while `dot_config/symlink_*.tmpl` entries point ChezMoi at those source directories. The goal of this change is to make `dot_config/` the single canonical source for managed `~/.config` content, remove the repo-to-home symlink model, and rely on ChezMoi's standard copy-based behavior for safer, easier-to-understand state management.

This migration is scoped to the configuration trees currently split between `config/` and `dot_config/`. It does not change already-native managed paths such as `dot_config/opencode/`, `dot_codex/`, `dot_claude/`, or the shell/bootstrap files at the repository root.

---

## 2. Proposed Changes

### 2.1 Canonical `~/.config` Source Layout
1. Treat `dot_config/` as the only canonical source for files deployed into `~/.config`.
2. Move the content of these source directories from `config/` into matching subdirectories under `dot_config/`:
   - `alacritty`
   - `atuin`
   - `git`
   - `herdr`
   - `mise`
   - `nvim`
   - `sheldon`
   - `starship`
   - `tmux`
   - `vim`
3. Remove the now-redundant `config/` tree after its contents have been migrated.

### 2.2 Remove Repo-to-Home Symlink Templates
1. Delete the top-level symlink templates that currently map `~/.config/<name>` back into the repository:
   - `dot_config/symlink_atuin.tmpl`
   - `dot_config/symlink_git.tmpl`
   - `dot_config/symlink_herdr.tmpl`
   - `dot_config/symlink_mise.tmpl`
   - `dot_config/symlink_nvim.tmpl`
   - `dot_config/symlink_sheldon.tmpl`
   - `dot_config/symlink_starship.tmpl`
   - `dot_config/symlink_tmux.tmpl`
   - `dot_config/symlink_vim.tmpl`
2. Convert the remaining Alacritty leaf-level symlink templates into normal managed files under `dot_config/alacritty/` so the whole subtree follows the same copy-based model:
   - `symlink_linux.toml.tmpl` -> `linux.toml`
   - `symlink_macos.toml.tmpl` -> `macos.toml`
   - `symlink_color_solarized_dark.toml.tmpl` -> `color_solarized_dark.toml`
3. Keep `dot_config/alacritty/alacritty.toml.tmpl` as the entrypoint template because its OS switch is still a valid ChezMoi use case.

### 2.3 Preserve Target Paths While Normalizing Source Names
1. Preserve the current target paths in the home directory. For example, the migration should still deploy to:
   - `~/.config/nvim/...`
   - `~/.config/tmux/tmux.conf`
   - `~/.config/git/config`
2. Rename hidden files inside migrated trees to valid ChezMoi source names where needed:
   - `config/nvim/.gitignore` -> `dot_config/nvim/dot_gitignore`
   - `config/nvim/.neoconf.json` -> `dot_config/nvim/dot_neoconf.json`
3. Preserve nested directory structure and file contents otherwise. The migration is about source layout and deployment semantics, not behavioral changes to the underlying tools.

### 2.4 Repository Metadata Cleanup
1. Remove the `config/` entry from `.chezmoiignore` once the migration is complete, since `config/` will no longer exist as an unmanaged source mirror.
2. Leave `.chezmoidata.toml` unchanged unless the implementation uncovers a real dependency on the old layout.
3. Audit the repository for remaining references to `{{ .chezmoi.sourceDir }}/config/` and remove or rewrite them where they are part of the active source state.

### 2.5 Safety Model
1. After this migration, the repository itself becomes the only editable source of truth for these config trees.
2. Local drift should be reconciled through ChezMoi workflows such as `chezmoi diff` and `chezmoi add`, rather than through live edits to repo-backed symlink targets in `~/.config`.
3. This intentionally favors clearer ownership and lower surprise over immediate bidirectional editing.

---

## 3. Verification & Testing
1. Run `chezmoi apply --dry-run` to inspect the migration result before touching the live home directory state.
2. Run `chezmoi diff` after the source-tree changes to confirm the deployed targets still map to the expected file contents.
3. Verify that representative paths under `~/.config` are managed as normal files/directories rather than symlinks into `{{ .chezmoi.sourceDir }}`.
4. Spot-check at least these tools after apply:
   - `nvim`
   - `tmux`
   - `git`
   - `mise`
   - `starship`
   - `atuin`
   - `alacritty`
5. Confirm that the active source state no longer contains runtime references to the old indirection model, especially:
   - `dot_config/symlink_*.tmpl`
   - `dot_config/alacritty/symlink_*.tmpl`
   - `{{ .chezmoi.sourceDir }}/config/`
