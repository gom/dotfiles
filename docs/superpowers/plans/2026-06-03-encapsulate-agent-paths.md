# Encapsulate Agent Paths and Symlinks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `agents/compile_configs.py` to encapsulate agent-specific paths, symlinks, and obsolete directory cleanups inside each agent's deployment function. This isolates `main()` from agent layout internals.

**Architecture:** Update the signatures and implementations of `process_plugins` and all four `deploy_xxx` functions. `main()` will build a unified `paths` dictionary with only common roots (`home`, `central_skills`, `central_hooks`, `central_subagents`), construct these directories, and run the pipeline.

**Tech Stack:** Python 3, bash (for deployment script)

---

### Task 1: Update Helper Functions in `compile_configs.py`

**Files:**
- Modify: `agents/compile_configs.py` (helpers section)

- [ ] **Step 1: Update `process_plugins` to receive `paths` and remove CLAUDE.md writing**

Update the definition of `process_plugins`:

```python
def process_plugins(plugins_dir, paths):
    """
    Scan the plugins directory, deploy skills, hooks, and subagent profiles to central folders,
    and write deployment manifests.
    Returns:
        tuple: (custom_skills, custom_hooks, custom_subagents, subagent_blocks)
    """
    plugins_data = []
    if os.path.exists(plugins_dir):
        for root, dirs, files in os.walk(plugins_dir):
            if "plugin.json" in files:
                manifest_path = os.path.join(root, "plugin.json")
                print(f"🔌 Found plugin manifest: {manifest_path}")
                with open(manifest_path, "r") as f:
                    plugin = json.load(f)
                    plugin["_dir"] = root
                    plugins_data.append(plugin)

    custom_skills    = []
    custom_hooks     = []
    custom_subagents = []
    subagent_blocks  = []   # collected for CLAUDE.md

    central_skills    = paths["central_skills"]
    central_hooks     = paths["central_hooks"]
    central_subagents = paths["central_subagents"]

    capability_dirs = [central_skills, central_hooks, central_subagents]
    deployed_tracking = {d: set() for d in capability_dirs}

    for plugin in sorted(plugins_data, key=lambda x: x.get("name", "")):
        p_dir = plugin["_dir"]

        # Skills
        for skill in plugin.get("skills", []):
            skill_name = skill["name"]
            src_script = os.path.join(p_dir, skill["script"])
            if os.path.exists(src_script):
                print(f"  ⚡ Deploying skill: {skill_name}")
                safe_copy_file(src_script, os.path.join(central_skills, skill_name))
                deployed_tracking[central_skills].add(skill_name)
                custom_skills.append({
                    "name":        skill_name,
                    "description": skill.get("description", ""),
                })

        # Hooks
        for hook in plugin.get("hooks", []):
            src_script = os.path.join(p_dir, hook["script"])
            if os.path.exists(src_script):
                hook_name = os.path.basename(hook["script"])
                print(f"  🪝 Deploying hook: {hook_name} ({hook.get('event')})")
                safe_copy_file(src_script, os.path.join(central_hooks, hook_name))
                deployed_tracking[central_hooks].add(hook_name)
                custom_hooks.append({
                    "event": hook.get("event", "pre-command"),
                    "name":  hook_name,
                })

        # Subagents
        for agent in plugin.get("agents", []):
            agent_name    = agent["name"]
            system_prompt = agent["system_prompt"]
            print(f"  🤖 Deploying subagent profile: {agent_name}")

            subagent_blocks.append(
                f"## Subagent Profile: {agent_name}\n"
                f"> {system_prompt}\n\n"
            )

            agent_filename = f"{agent_name}.md"
            write_text_file(
                os.path.join(central_subagents, agent_filename),
                f"# {agent_name} Subagent Profile\n\n{system_prompt}\n",
            )
            deployed_tracking[central_subagents].add(agent_filename)

            custom_subagents.append({
                "name":          agent_name,
                "system_prompt": system_prompt,
            })

    # Persist deployment manifests
    for d, names in deployed_tracking.items():
        save_deployed(d, names)

    return custom_skills, custom_hooks, custom_subagents, subagent_blocks
```

- [ ] **Step 2: Update `deploy_antigravity`, `deploy_claude`, `deploy_codex`, and `deploy_opencode`**

Update the helper functions to encapsulate internal directory layout and symlinks:

```python
def deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents):
    """Deploy Antigravity CLI MCP configuration, settings, and symlinks."""
    antigravity_dir = os.path.join(paths["home"], ".gemini", "antigravity-cli")
    os.makedirs(antigravity_dir, exist_ok=True)
    
    # Establish symlinks
    ensure_symlink(paths["central_skills"], os.path.join(antigravity_dir, "skills"))
    ensure_symlink(paths["central_hooks"], os.path.join(antigravity_dir, "hooks"))

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


def deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, subagent_blocks):
    """Deploy Claude Code Settings, MCP configuration, instructions (CLAUDE.md), and symlinks."""
    claude_dir = os.path.join(paths["home"], ".claude")
    os.makedirs(claude_dir, exist_ok=True)
    
    # Establish symlinks
    ensure_symlink(paths["central_skills"], os.path.join(claude_dir, "skills"))
    ensure_symlink(paths["central_hooks"], os.path.join(claude_dir, "hooks"))

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


def deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents):
    """Deploy Codex Configuration (TOML) and symlinks."""
    codex_dir = os.path.join(paths["home"], ".codex")
    os.makedirs(codex_dir, exist_ok=True)
    
    # Establish symlinks
    ensure_symlink(paths["central_skills"], os.path.join(codex_dir, "skills"))
    ensure_symlink(paths["central_hooks"], os.path.join(codex_dir, "hooks"))

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

- [ ] **Step 3: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 4: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: update process_plugins and deploy_xxx helper signatures and implementations"
```

---

### Task 2: Simplify `main()`

**Files:**
- Modify: `agents/compile_configs.py` (`main()` function)

- [ ] **Step 1: Simplify path setups, directory cleaning, and helper calls in `main()`**

Replace the directory definitions, symlinks block, and helper calls in `main()` with:

```python
def main():
    home       = os.path.expanduser("~")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    master_path = os.path.join(script_dir, "agent", "master_config.json")

    if not os.path.exists(master_path):
        print(f"❌ Error: Master config not found at {master_path}")
        return 1

    print(f"🔄 Reading master configuration from {master_path}...")
    with open(master_path, "r") as f:
        master = json.load(f)

    # --- 1. Define Common System Configuration Paths ---
    paths = {
        "home":              home,
        "central_skills":    os.path.join(home, ".agents", "skills"),
        "central_hooks":     os.path.join(home, ".agents", "hooks"),
        "central_subagents": os.path.join(home, ".agents", "subagents"),
    }

    for d in ["central_skills", "central_hooks", "central_subagents"]:
        os.makedirs(paths[d], exist_ok=True)
        clean_compiler_owned(paths[d])

    # --- 2. Scan and Process Plugins ---
    plugins_dir = os.path.join(script_dir, "plugins")
    custom_skills, custom_hooks, custom_subagents, subagent_blocks = process_plugins(
        plugins_dir, paths
    )

    # --- 3. Compile & Deploy Active System Configurations ---
    color_scheme       = master.get("colorScheme", "tokyo night")
    permissions        = master.get("permissions", {})
    mcp_servers        = master.get("mcp_servers", {})
    trusted_workspaces = master.get("trustedWorkspaces", [])
    local_cfg          = master.get("local", {})

    deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents)
    
    # Claude uses theme color_scheme mapping, but if master specifies "tokyo night", we fall back to "dark" theme format
    claude_theme = master.get("colorScheme", "dark")
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"
    deploy_claude(paths, claude_theme, permissions, mcp_servers, custom_hooks, subagent_blocks)
    
    deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents)
    deploy_opencode(paths, color_scheme, permissions, mcp_servers, local_cfg)

    print("✨ Deploy-time compilation complete! All configs natively built and written to system folders.")
    return 0
```

- [ ] **Step 2: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: simplify main() path declarations and helper calls"
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
