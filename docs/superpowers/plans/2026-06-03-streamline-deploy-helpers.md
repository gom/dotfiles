# Streamline Deploy Helper Functions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up and streamline `agents/compile_configs.py` by encapsulating theme mapping inside `deploy_claude` and deleting deprecated compatibility logic in `deploy_opencode`.

**Architecture:** 
1. In `deploy_claude`, normalise `color_scheme` internally.
2. In `deploy_opencode`, remove the block that reads/writes `opencode.json` and deletes legacy keys from `opencode.jsonc`.
3. In `main()`, directly pass `color_scheme` to `deploy_claude`.

**Tech Stack:** Python 3, bash (for deployment script)

---

### Task 1: Update `deploy_claude` and `deploy_opencode` Helpers

**Files:**
- Modify: `agents/compile_configs.py` (helpers section)

- [ ] **Step 1: Normalise theme inside `deploy_claude()`**

Update `deploy_claude` to normalise `color_scheme` internally:

```python
def deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, subagent_blocks):
    """Deploy Claude Code Settings, MCP configuration, instructions (CLAUDE.md), and symlinks."""
    claude_dir = os.path.join(paths["home"], ".claude")
    os.makedirs(claude_dir, exist_ok=True)
    
    # Establish symlinks
    ensure_symlink(paths["central_skills"], os.path.join(claude_dir, "skills"))
    ensure_symlink(paths["central_hooks"], os.path.join(claude_dir, "hooks"))

    # Normalise color scheme for Claude (falls back to dark if Tokyo Night is used)
    claude_theme = color_scheme
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"

    print("💾 Deploying Claude Code settings...")
    merge_json_file(
        os.path.join(claude_dir, "settings.json"),
        {
            "theme":       claude_theme,
            "permissions": permissions,
            "hooks":       custom_hooks,
        },
        overwrite_keys=["permissions", "hooks"],
    )

    print("💾 Deploying Claude Code MCP configuration...")
    merge_json_file(
        os.path.join(paths["home"], ".claude.json"),
        {"mcpServers": mcp_servers},
        overwrite_keys=["mcpServers"],
    )

    # Update CLAUDE.md global instructions
    update_claude_md(
        os.path.join(claude_dir, "CLAUDE.md"),
        (
            "# Claude Code Global Instructions\n\n"
            "This file is dynamically deployed from your unified plugins.\n\n"
            "## Core Guidelines\n"
            "* Prefer standard command line utilities managed via mise.\n"
            "* Follow clean development guidelines for editing code.\n\n"
        ),
        subagent_blocks,
    )
```

- [ ] **Step 2: Streamline `deploy_opencode()`**

Remove the migration logic block from `deploy_opencode`:

```python
def deploy_opencode(paths, color_scheme, permissions, mcp_servers, local_cfg):
    """Deploy OpenCode Configuration, TUI Config, symlinks, and run obsolete hook cleanup."""
    opencode_dir = os.path.join(paths["home"], ".config", "opencode")
    os.makedirs(opencode_dir, exist_ok=True)
    
    # Clean up obsolete hooks folder from OpenCode directory if it exists
    opencode_hooks_path = os.path.join(opencode_dir, "hooks")
    if os.path.islink(opencode_hooks_path):
        os.remove(opencode_hooks_path)
    elif os.path.isdir(opencode_hooks_path):
        shutil.rmtree(opencode_hooks_path)

    # Establish symlinks
    ensure_symlink(paths["central_skills"], os.path.join(opencode_dir, "commands"))
    ensure_symlink(paths["central_subagents"], os.path.join(opencode_dir, "agents"))

    print("💾 Deploying OpenCode settings...")
    opencode_mcp = compile_opencode_mcp(mcp_servers)
    opencode_permission = compile_opencode_permission(permissions)

    opencode_path = os.path.join(opencode_dir, "opencode.jsonc")

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

    theme_name = color_scheme.replace(" ", "")
    merge_json_file(
        os.path.join(opencode_dir, "tui.json"),
        {
            "$schema": "https://opencode.ai/tui.json",
            "theme": theme_name,
        },
        overwrite_keys=["theme"],
    )
```

- [ ] **Step 3: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 4: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: streamline deploy_claude and deploy_opencode helper functions"
```

---

### Task 2: Simplify Call Site in `main()`

**Files:**
- Modify: `agents/compile_configs.py` (`main()` function)

- [ ] **Step 1: Simplify `deploy_claude` call**

Find the block in `main()`:
```python
    # Claude uses theme color_scheme mapping, but if master specifies "tokyo night", we fall back to "dark" theme format
    claude_theme = master.get("colorScheme", "dark")
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"
    deploy_claude(paths, claude_theme, permissions, mcp_servers, custom_hooks, subagent_blocks)
```
Replace it with a direct call to `deploy_claude`:
```python
    deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, subagent_blocks)
```

- [ ] **Step 2: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: simplify deploy_claude call in main()"
```

---

### Task 3: Deployment and Verification

**Files:**
- Test/Run: `bash agents/deploy.sh`

- [ ] **Step 1: Run deploy script**

Run: `bash agents/deploy.sh`
Expected: Completes successfully with exit code 0.

- [ ] **Step 2: Verify git status is clean**

Ensure that no unstaged changes remain.
Check that the compiler successfully compiled configurations and that CLAUDE.md has been updated correctly.
