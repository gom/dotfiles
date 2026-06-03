# Design Spec: Streamline Deploy Helper Functions

## 1. Problem
In `agents/compile_configs.py`:
- `main()` still contains Claude Code theme normalization logic (detecting `"tokyo"` and falling back to `"dark"`). This is Claude-specific theme handling and should be handled inside `deploy_claude`.
- `deploy_opencode()` contains obsolete migration code that handles stripping legacy keys from `opencode.jsonc` and deleting the deprecated `opencode.json` file. Since all active setups have migrated, this logic is dead code.

## 2. Solution
1. Move the theme fallback logic for Claude Code from `main()` into `deploy_claude()`. `main()` will pass the raw `color_scheme` directly.
2. Delete the legacy JSON migration, cleanup, and key popping block from `deploy_opencode()`, relying purely on `merge_json_file()` directly.

### Refactored Helper Implementations

#### `deploy_claude` (signature and theme mapping)
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

#### `deploy_opencode` (removing migration logic)
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

---

## 3. File Structure
- **Modify:** `agents/compile_configs.py`
  - Normalise theme internally in `deploy_claude()`.
  - Streamline `deploy_opencode()` to exclude legacy config check and file migration block.
  - Simplify `main()` to directly call `deploy_claude(paths, color_scheme, ...)` without preprocessing the theme.

---

## 4. Verification
1. Run syntax verification: `python3 -m py_compile agents/compile_configs.py`
2. Run config compilation: `bash agents/deploy.sh`
3. Verify that the output configurations remain unchanged.
