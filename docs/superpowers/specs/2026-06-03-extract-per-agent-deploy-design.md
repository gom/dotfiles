# Design Spec: Extract Per-Agent Deploy Functions

## 1. Problem
In `agents/compile_configs.py`, the `main()` function is currently over 280 lines long. A large portion of it (~130 lines) is dedicated to compiling and writing configurations to system paths for four different agents:
1. **Antigravity CLI** (MCP config and settings)
2. **Claude Code** (settings and MCP configuration)
3. **Codex** (TOML configuration)
4. **OpenCode** (settings and TUI configuration)

Because this logic is inline, `main()` is hard to read and test. Changes to one agent's deployment process require editing the core of `main()`.

## 2. Solution
Extract the deployment logic for each agent into focused, decoupled module-level functions. These functions will be defined in a new section above `main()` called `# Per-agent deployment helpers`.

### Signature and Interface Guidelines
To keep functions decoupled and testable:
- Pass only specific configurations extracted from `master` (e.g. `color_scheme`, `permissions`, `mcp_servers`, `trusted_workspaces`, and `local_cfg`) instead of passing the entire `master` dictionary.
- Functions execute side-effects (writing/merging files) and print informative status messages.

### Function Definitions

#### 1. `deploy_antigravity`
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
```

#### 2. `deploy_claude`
```python
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
```

#### 3. `deploy_codex`
```python
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

#### 4. `deploy_opencode`
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

### Main Function Integration

The end of `main()` will extract parameters and make clean procedural calls:

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

## 3. File Structure
- **Modify:** `agents/compile_configs.py`
  - Add per-agent deploy helper functions above `main()`.
  - Replace inline agent deployment block in `main()` with the extracted function calls.

## 4. Verification
1. Run syntax verification: `python3 -m py_compile agents/compile_configs.py`
2. Run config compilation: `bash agents/deploy.sh`
3. Verify that the output files remain unchanged (e.g. `opencode.jsonc`, `settings.json` for Antigravity, Claude, Codex, etc.).
