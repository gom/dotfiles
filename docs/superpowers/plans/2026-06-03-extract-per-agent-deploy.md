# Extract Per-Agent Deploy Functions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the long `main()` function in `agents/compile_configs.py` by extracting per-agent configuration deployment logic into decoupled module-level functions.

**Architecture:** Create four distinct helper functions (`deploy_antigravity`, `deploy_claude`, `deploy_codex`, and `deploy_opencode`) that accept only their required parameters from the master configuration. Integrate these helpers into `main()` to dramatically simplify readability and improve maintainability.

**Tech Stack:** Python 3, bash (for validation/deployment script)

---

### Task 1: Define Antigravity, Claude, and Codex Deploy Helpers

**Files:**
- Modify: `agents/compile_configs.py:452-456`

- [ ] **Step 1: Write helper functions above `main()`**

Insert the new functions `deploy_antigravity`, `deploy_claude`, and `deploy_codex` immediately after `compile_opencode_permission` and before `# Main` (around line 452).

```python
def deploy_antigravity(antigravity_dir, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents):
    """Deploy Antigravity CLI MCP configuration and settings."""
    print("💾 Deploying Antigravity CLI MCP configuration...")
    merge_json_file(
        os.path.join(antigravity_dir, "mcp_config.json"),
        {"mcpServers": mcp_servers},
        overwrite_keys=["mcpServers"],
    )

    print("💾 Deploying Antigravity CLI settings...")
    merge_json_file(
        os.path.join(antigravity_dir, "settings.json"),
        {
            "colorScheme":       color_scheme,
            "permissions":       permissions,
            "statusLine":        {"type": "", "command": "", "enabled": True},
            "trustedWorkspaces": trusted_workspaces,
            "hooks":             custom_hooks,
            "subagents":         custom_subagents,
        },
        overwrite_keys=["permissions", "hooks", "subagents"],
    )


def deploy_claude(home, claude_dir, color_scheme, permissions, mcp_servers, custom_hooks):
    """Deploy Claude Code Settings and MCP configuration."""
    print("💾 Deploying Claude Code settings...")
    merge_json_file(
        os.path.join(claude_dir, "settings.json"),
        {
            "theme":       color_scheme,
            "permissions": permissions,
            "hooks":       custom_hooks,
        },
        overwrite_keys=["permissions", "hooks"],
    )

    print("💾 Deploying Claude Code MCP configuration...")
    merge_json_file(
        os.path.join(home, ".claude.json"),
        {"mcpServers": mcp_servers},
        overwrite_keys=["mcpServers"],
    )


def deploy_codex(codex_dir, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents):
    """Deploy Codex Configuration (TOML)."""
    print("💾 Deploying Codex config...")
    merge_toml_file(
        os.path.join(codex_dir, "config.toml"),
        {
            "color_scheme": color_scheme,
            "permissions":  permissions,
            "mcp_servers":  mcp_servers,
            "hooks":        custom_hooks,
            "subagents":    custom_subagents,
        },
        overwrite_keys=["permissions", "mcp_servers", "hooks", "subagents"],
    )
```

- [ ] **Step 2: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: define deploy_antigravity, deploy_claude, and deploy_codex"
```

---

### Task 2: Define OpenCode Deploy Helper

**Files:**
- Modify: `agents/compile_configs.py` (insert above `# Main`)

- [ ] **Step 1: Write `deploy_opencode` function above `main()`**

Insert the new function `deploy_opencode` immediately after `deploy_codex` and before `# Main`.

```python
def deploy_opencode(opencode_dir, color_scheme, permissions, mcp_servers, local_cfg):
    """Deploy OpenCode Configuration and TUI Config."""
    print("💾 Deploying OpenCode settings...")
    opencode_mcp = compile_opencode_mcp(mcp_servers)
    opencode_permission = compile_opencode_permission(permissions)

    opencode_json_path = os.path.join(opencode_dir, "opencode.json")
    opencode_path = os.path.join(opencode_dir, "opencode.jsonc")

    existing_opencode = {}
    if os.path.exists(opencode_path):
        try:
            with open(opencode_path, "r") as f:
                existing_opencode = json.load(f)
        except Exception:
            pass

    if not existing_opencode and os.path.exists(opencode_json_path):
        try:
            with open(opencode_json_path, "r") as f:
                existing_opencode = json.load(f)
        except Exception:
            pass

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

- [ ] **Step 2: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: define deploy_opencode helper function"
```

---

### Task 3: Integrate Helpers in `main()`

**Files:**
- Modify: `agents/compile_configs.py`

- [ ] **Step 1: Replace inline blocks in `main()` with function calls**

Find the block starting with `# --- 3. Compile & Deploy Active System Configurations ---` (around line 607 pre-refactor) and ending just before `print("✨ Deploy-time compilation complete!...")` (around line 738).
Replace it with the parameter extraction and helper invocations:

```python
    # --- 3. Compile & Deploy Active System Configurations ---
    color_scheme       = master.get("colorScheme", "tokyo night")
    permissions        = master.get("permissions", {})
    mcp_servers        = master.get("mcp_servers", {})
    trusted_workspaces = master.get("trustedWorkspaces", [])
    local_cfg          = master.get("local", {})

    deploy_antigravity(antigravity_dir, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents)
    
    # Claude uses theme color_scheme mapping, but if master specifies "tokyo night", we fall back to "dark" theme format
    claude_theme = master.get("colorScheme", "dark")
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"
    deploy_claude(home, claude_dir, claude_theme, permissions, mcp_servers, custom_hooks)
    
    deploy_codex(codex_dir, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents)
    deploy_opencode(opencode_dir, color_scheme, permissions, mcp_servers, local_cfg)
```

- [ ] **Step 2: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: integrate helper functions in main()"
```

---

### Task 4: Deployment and Verification

**Files:**
- Test/Run: `bash agents/deploy.sh`

- [ ] **Step 1: Run deploy script**

Run: `bash agents/deploy.sh`
Expected: Completes successfully with exit code 0.

- [ ] **Step 2: Verify git status is clean except for compiled files if modified**

Ensure `git diff` shows no unintended modifications to Python files or other project code.
Check that the compiler successfully generated configuration files like `~/.config/opencode/opencode.jsonc`, `~/.config/opencode/tui.json`, etc.
