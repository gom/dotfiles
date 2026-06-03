# Design Spec: Remove Hooks from OpenCode Configuration

## 1. Objective
OpenCode does not support hooks. This specification outlines how to completely clean up and prevent hooks configuration/generation for OpenCode in the dotfiles compilation toolchain.

---

## 2. Proposed Changes

### 2.1 `agents/compile_configs.py`
1. **Remove hooks symlink mapping** for OpenCode from the `symlinks_map` dictionary:
   - Remove `os.path.join(opencode_dir, "hooks"): central_hooks,`.
2. **Explicitly clean up obsolete symlinks/folders**:
   - In `main()` of `compile_configs.py`, check if `os.path.join(opencode_dir, "hooks")` exists as a symlink or directory, and delete it.
3. **Pop `"hooks"` from existing `opencode.jsonc`**:
   - In the clean-up block where we pop deprecated keys (`"theme"`, `"permissions"`, `"mcpServers"`), add `"hooks"` to ensure any legacy hooks key is dropped.
4. **Exclude `"hooks"` from compilation dictionary**:
   - Remove `"hooks"` key from the data dictionary sent to `merge_json_file` for `opencode_path` (`opencode.jsonc`).
   - Remove `"hooks"` from the `overwrite_keys` array in that call.

---

## 3. Verification & Testing
1. Run `./agents/deploy.sh` to compile and deploy configs.
2. Confirm the file `~/.config/opencode/opencode.jsonc` does NOT contain the `"hooks"` block.
3. Confirm the symlink or directory at `~/.config/opencode/hooks` has been deleted from the filesystem.
4. Verify that other agents (Antigravity CLI, Claude Code) still have hooks correctly set up in their settings.
