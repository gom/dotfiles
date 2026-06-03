# Remove Hooks from OpenCode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely remove and clean up hooks configuration from the OpenCode config pipeline.

**Architecture:** Modify `agents/compile_configs.py` to remove the OpenCode hooks symlink map, add explicit cleanup for any existing symlinks, pop `"hooks"` from the existing `opencode.jsonc` before merge, and remove `"hooks"` from the merged dictionary and `overwrite_keys`.

**Tech Stack:** Python 3, Git, Bash

---

### Task 1: Update Symlinks Map and Add File Cleanup in `compile_configs.py`

**Files:**
- Modify: `agents/compile_configs.py:447-462`

- [ ] **Step 1: Modify `symlinks_map` and add physical symlink cleanup**
  Remove the `opencode_dir` hooks mapping, and add a check to delete any existing `hooks` symlink/directory inside the OpenCode config folder.

  Modify `agents/compile_configs.py` around line 447 to be:
  ```python
      # Establish the symlinks map from active dirs to the centralized store.
      # Only OpenCode has a first-class "agents" directory concept — Antigravity,
      # Claude Code, and Codex read subagent definitions from settings.json
      # (injected by the compiler), so no subagents symlink is needed for them.
      symlinks_map = {
          os.path.join(antigravity_dir, "skills"):   central_skills,
          os.path.join(antigravity_dir, "hooks"):    central_hooks,
          os.path.join(claude_dir,      "skills"):   central_skills,
          os.path.join(claude_dir,      "hooks"):    central_hooks,
          os.path.join(codex_dir,       "skills"):   central_skills,
          os.path.join(codex_dir,       "hooks"):    central_hooks,
          os.path.join(opencode_dir,    "commands"): central_skills,
          os.path.join(opencode_dir,    "agents"):   central_subagents,
      }

      # Clean up obsolete hooks folder from OpenCode directory if it exists
      opencode_hooks_path = os.path.join(opencode_dir, "hooks")
      if os.path.islink(opencode_hooks_path):
          os.remove(opencode_hooks_path)
      elif os.path.isdir(opencode_hooks_path):
          shutil.rmtree(opencode_hooks_path)

      # Ensure all symlinks are created and point to the centralized store
      for link_name, target in symlinks_map.items():
          ensure_symlink(target, link_name)
  ```

- [ ] **Step 2: Verify Python compilation script syntax**
  Run: `python3 -m py_compile agents/compile_configs.py`
  Expected: Command exits successfully with no output/errors.

---

### Task 2: Exclude Hooks from `opencode.jsonc` Generation and Legacy Pop List

**Files:**
- Modify: `agents/compile_configs.py:680-715`

- [ ] **Step 1: Modify legacy key stripping and merge calls**
  Add `"hooks"` to the pop list for `existing_opencode`, and remove `"hooks": custom_hooks` and `"hooks"` from `overwrite_keys`.

  Modify `agents/compile_configs.py` around line 680 to be:
  ```python
      if isinstance(existing_opencode, dict):
          for k in ["theme", "permissions", "mcpServers", "hooks"]:
              existing_opencode.pop(k, None)

      os.makedirs(os.path.dirname(opencode_path), exist_ok=True)
      try:
          with open(opencode_path, "w") as f:
              json.dump(existing_opencode, f, indent=2)
              f.write("\n")
      except Exception:
          pass

      if os.path.exists(opencode_json_path):
          try:
              os.remove(opencode_json_path)
              print("  ... Migrated and removed obsolete opencode.json")
          except Exception:
              pass

      local_cfg = master.get("local", {})
      merge_json_file(
          opencode_path,
          {
              "$schema": "https://opencode.ai/config.json",
              "permission": opencode_permission,
              "mcp": opencode_mcp,
              "provider": local_cfg.get("provider", {}),
              "model": local_cfg.get("model", ""),
              "small_model": local_cfg.get("small_model", "")
          },
          overwrite_keys=["permission", "mcp", "provider", "model", "small_model"],
      )
  ```

- [ ] **Step 2: Verify script syntax**
  Run: `python3 -m py_compile agents/compile_configs.py`
  Expected: Command exits successfully with no output/errors.

- [ ] **Step 3: Commit Task 1 and Task 2 changes**
  ```bash
  git add agents/compile_configs.py
  git commit -m "feat: remove hooks generation and symlinking from OpenCode config"
  ```

---

### Task 3: Deploy and Validate

**Files:**
- Modify: none (Execution only)

- [ ] **Step 1: Execute deployment script**
  Run: `bash agents/deploy.sh`
  Expected: Complete compilation output with no errors.

- [ ] **Step 2: Verify `opencode.jsonc` does not contain hooks**
  Run: `cat ~/.config/opencode/opencode.jsonc`
  Expected: Confirm the `"hooks"` array is not present in the output.

- [ ] **Step 3: Verify the hooks symlink is gone**
  Run: `ls -la ~/.config/opencode/`
  Expected: The output does not contain `hooks -> /home/dai/.agents/hooks`.
