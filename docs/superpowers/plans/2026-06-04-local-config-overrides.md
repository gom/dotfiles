# Local Configuration Overrides Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable users to override global configurations with local, work-specific configurations (MCP servers, models, permissions) that are never committed to Git.

**Architecture:**
1. Ignore `master_config.local.json` in Git.
2. Load and deep merge `master_config.local.json` on top of `master_config.json` in `compile_configs.py`.
3. Verify end-to-end correct deployment.

**Tech Stack:** Python 3, Git, Bash

---

### Task 1: Gitignore Local Overrides Configuration

**Files:**
- Modify: `/home/dai/.dotfiles/.gitignore`

- [ ] **Step 1: Ignore the local override file**
Add the path `agents/agent/master_config.local.json` to the bottom of `.gitignore`:
```
.antigravitycli
.serena
agents/plugins/external/
agents/agent/master_config.local.json
```

- [ ] **Step 2: Commit changes**
Run:
```bash
git add .gitignore
git commit -m "chore: ignore master_config.local.json in git"
```

---

### Task 2: Load and Merge Local Overrides in `compile_configs.py`

**Files:**
- Modify: `/home/dai/.dotfiles/agents/compile_configs.py`

- [ ] **Step 1: Update `main()` to load and merge overrides**
Locate the block in `main()` around lines 649-653:
```python
    print(f"🔄 Reading master configuration from {master_path}...")
    with open(master_path, "r") as f:
        master = json.load(f)
```
Replace it with:
```python
    print(f"🔄 Reading master configuration from {master_path}...")
    with open(master_path, "r") as f:
        master = json.load(f)

    # Load machine-specific local overrides if present
    local_path = os.path.join(script_dir, "agent", "master_config.local.json")
    if os.path.exists(local_path):
        print(f"🔄 Found local overrides at {local_path}, merging...")
        try:
            with open(local_path, "r") as f:
                local_master = json.load(f)
                if isinstance(local_master, dict):
                    master = Config.deep_merge(master, local_master)
        except Exception as exc:
            print(f"⚠️ Warning: Failed to read local overrides: {exc}")
```

- [ ] **Step 2: Verify syntax**
Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit changes**
Run:
```bash
git add agents/compile_configs.py
git commit -m "refactor: load and merge master_config.local.json overrides"
```

---

### Task 3: Dry-run and End-to-End Verification

**Files:**
- Test/Run: `bash agents/deploy.sh`

- [x] **Step 1: Create a mock local override file**
Create `agents/agent/master_config.local.json` with the following content:
```json
{
  "colorScheme": "monokai"
}
```

- [x] **Step 2: Run deployment**
Run: `bash agents/deploy.sh`
Expected: Passes successfully.

- [x] **Step 3: Verify color scheme was overridden**
Inspect the deployed OpenCode TUI settings:
Run: `cat ~/.config/opencode/tui.json`
Expected: The file contains `"theme": "monokai"` (overriding `"tokyonight"` or other defaults).

- [x] **Step 4: Verify git status ignores the local config**
Run: `git status`
Expected: Only showing untracked `__pycache__` if any, no mention of `master_config.local.json` (meaning it's successfully ignored).

- [x] **Step 5: Clean up mock file and restore default**
Delete the mock local override file and redeploy:
```bash
rm agents/agent/master_config.local.json
bash agents/deploy.sh
```
Expected: Redeploy finishes successfully and restores default settings.
