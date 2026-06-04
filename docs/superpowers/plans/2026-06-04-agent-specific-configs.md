# Agent-Specific Configurations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Introduce per-agent configuration sections under `agents` in `master_config.json`, add a pre-deploy backup mechanism, and remove the legacy `local` key.

**Architecture:**
1. Add `backup_configs(home)` to `compile_configs.py` and call it in `main()` before any deploy.
2. Update `master_config.json` to move `local` → `agents.opencode` and delete `local`.
3. Update each `deploy_xxx()` function to accept an `agent_cfg` parameter and use it.
4. Update `main()` to extract `agents_cfg` and pass agent-specific slices to each function.
5. Verify end-to-end.

**Tech Stack:** Python 3, Git

---

### Task 1: Add `backup_configs()` and call it in `main()`

**Files:**
- Modify: `agents/compile_configs.py`

- [x] **Step 1: Add the `backup_configs` function**

Insert a new `backup_configs(home)` function into `compile_configs.py` just before the `# Main` section header (around line 634). The function:
- Collects all 8 known deployed config file paths.
- Copies each file that exists to `~/.agents/backups/YYYYMMDDTHHMMSS/` with an agent-prefixed flat name.
- Silently skips files that don't exist.
- Prints the backup path (or a note if no files were found to back up).

```python
def backup_configs(home):
    """
    Creates a timestamped backup of all known deployed agent config files at
    ~/.agents/backups/YYYYMMDDTHHMMSS/ before the deploy overwrites them.
    Files that do not exist yet are silently skipped.
    """
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_dir = os.path.join(home, ".agents", "backups", timestamp)

    known_files = [
        ("antigravity", os.path.join(home, ".gemini", "antigravity-cli", "settings.json")),
        ("antigravity", os.path.join(home, ".gemini", "antigravity-cli", "mcp_config.json")),
        ("claude",      os.path.join(home, ".claude", "settings.json")),
        ("claude",      os.path.join(home, ".claude.json")),
        ("codex",       os.path.join(home, ".codex", "config.toml")),
        ("opencode",    os.path.join(home, ".config", "opencode", "opencode.jsonc")),
        ("opencode",    os.path.join(home, ".config", "opencode", "tui.json")),
    ]

    backed_up = []
    for agent, src in known_files:
        if os.path.isfile(src):
            flat_name = f"{agent}__{os.path.basename(src)}"
            dst = os.path.join(backup_dir, flat_name)
            os.makedirs(backup_dir, exist_ok=True)
            Files.safe_copy_file(src, dst)
            backed_up.append(flat_name)

    if backed_up:
        print(f"💾 Backed up {len(backed_up)} config file(s) to: {backup_dir}")
    else:
        print("💾 No existing config files to back up (first-time deploy).")
```

- [x] **Step 2: Call `backup_configs` in `main()` before deployment**

In `main()`, insert `backup_configs(home)` immediately after the paths setup block, before the plugins scan (around line 675):
```python
    # --- 1. Define Common System Configuration Paths ---
    paths = { ... }

    for d in [...]:
        os.makedirs(paths[d], exist_ok=True)
        Files.clean_compiler_owned(paths[d])

    # --- 1b. Back up existing configs before overwriting ---
    backup_configs(home)

    # --- 2. Scan and Process Plugins ---
```

- [x] **Step 3: Verify syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: No errors.

- [x] **Step 4: Commit**

```bash
git add agents/compile_configs.py
git commit -m "feat: add backup_configs() to back up deployed configs before each deploy"
```

---

### Task 2: Migrate `master_config.json` from `local` to `agents.opencode`

**Files:**
- Modify: `agents/agent/master_config.json`

- [x] **Step 1: Replace `local` key with `agents.opencode`**

Replace the current `master_config.json` content with:
```json
{
  "colorScheme": "tokyo night",
  "trustedWorkspaces": [],
  "agents": {
    "claude": {
      "env": {}
    },
    "codex": {
      "model": ""
    },
    "opencode": {
      "model": "ollama/qwen3.6:35b-a3b",
      "small_model": "ollama/gemma4:e4b",
      "provider": {
        "ollama": {
          "npm": "@ai-sdk/openai-compatible",
          "name": "Ollama (local)",
          "options": {
            "baseURL": "{env:OLLAMA_BASE_URL}"
          },
          "models": {
            "qwen3.6:27b": {
              "name": "Qwen 3.6 27B"
            },
            "qwen3.6:35b-a3b": {
              "name": "Qwen 3.6 35B A3B"
            },
            "gemma4:26b": {
              "name": "Gemma 4 26B"
            },
            "gemma4:e4b": {
              "name": "Gemma 4 E4B"
            }
          }
        }
      }
    }
  },
  "permissions": {
    "allow": [
      "command(ls)",
      "command(cat)",
      "command(git status)",
      "command(git log)",
      "command(docker compose)",
      "command(mkdir)",
      "command(pwd)",
      "command(find)",
      "command(git rev-parse)",
      "command(git remote)",
      "command(diff)",
      "command(date)",
      "command(echo)",
      "command(git add)"
    ],
    "ask": [
      "command(git commit)",
      "command(git push)"
    ]
  },
  "mcp_servers": {
    "github": {
      "command": "/usr/local/bin/github-mcp-server",
      "args": ["stdio"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_TOKEN"
      }
    },
    "drawio": {
      "serverUrl": "https://mcp.draw.io/mcp"
    },
    "tavily": {
      "serverUrl": "https://mcp.tavily.com/mcp/?tavilyApiKey=$TAVILY_API_KEY"
    },
    "serena": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context", "claude-code",
        "--project-from-cwd"
      ]
    }
  }
}
```

- [x] **Step 2: Commit**

```bash
git add agents/agent/master_config.json
git commit -m "refactor: move local cfg to agents.opencode in master_config.json"
```

---

### Task 3: Update `deploy_xxx()` signatures and `main()`

**Files:**
- Modify: `agents/compile_configs.py`

- [x] **Step 1: Update `deploy_antigravity` signature**

Add `agent_cfg={}` parameter (unused for now, forward-compat):
```python
def deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents, agent_cfg={}):
    """Deploy Antigravity CLI MCP configuration, settings, and symlinks."""
    # ... existing body unchanged ...
```

- [x] **Step 2: Update `deploy_claude` signature and body**

Add `agent_cfg={}` parameter and write `env` into `settings.json`:
```python
def deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, agent_cfg={}):
    """Deploy Claude Code Settings, MCP configuration, and symlinks."""
    claude_dir = os.path.join(paths["home"], ".claude")
    os.makedirs(claude_dir, exist_ok=True)

    # Establish symlinks
    Symlinks.ensure(paths["central_skills"], os.path.join(claude_dir, "skills"))
    Symlinks.ensure(paths["central_hooks"], os.path.join(claude_dir, "hooks"))

    # Normalise color scheme for Claude (falls back to dark if Tokyo Night is used)
    claude_theme = color_scheme
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"

    print("💾 Deploying Claude Code settings...")
    Config.merge_json_file(
        os.path.join(claude_dir, "settings.json"),
        {
            "theme":       claude_theme,
            "permissions": permissions,
            "hooks":       custom_hooks,
            "env":         agent_cfg.get("env", {}),
        },
        overwrite_keys=["permissions", "hooks", "env"],
    )

    print("💾 Deploying Claude Code MCP configuration...")
    Config.merge_json_file(
        os.path.join(paths["home"], ".claude.json"),
        {"mcpServers": mcp_servers},
        overwrite_keys=["mcpServers"],
    )
```

- [x] **Step 3: Update `deploy_codex` signature and body**

Add `agent_cfg={}` parameter and write `model` into the TOML:
```python
def deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents, agent_cfg={}):
    """Deploy Codex Configuration (TOML) and symlinks."""
    codex_dir = os.path.join(paths["home"], ".codex")
    os.makedirs(codex_dir, exist_ok=True)

    # Establish symlinks
    Symlinks.ensure(paths["central_skills"], os.path.join(codex_dir, "skills"))
    Symlinks.ensure(paths["central_hooks"], os.path.join(codex_dir, "hooks"))

    print("💾 Deploying Codex config...")
    Config.merge_toml_file(
        os.path.join(codex_dir, "config.toml"),
        {
            "color_scheme": color_scheme,
            "model":        agent_cfg.get("model", ""),
            "permissions":  permissions,
            "mcp_servers":  mcp_servers,
            "hooks":        custom_hooks,
            "subagents":    custom_subagents,
        },
        overwrite_keys=["permissions", "mcp_servers", "hooks", "subagents", "model"],
    )
```

- [x] **Step 4: Update `deploy_opencode` to use `agent_cfg` instead of `local_cfg`**

Rename parameter from `local_cfg` to `agent_cfg` and update all `.get()` calls:
```python
def deploy_opencode(paths, color_scheme, permissions, mcp_servers, agent_cfg={}):
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
    Symlinks.ensure(paths["central_skills"], os.path.join(opencode_dir, "commands"))
    Symlinks.ensure(paths["central_subagents"], os.path.join(opencode_dir, "agents"))

    print("💾 Deploying OpenCode settings...")
    opencode_mcp = OpenCode.compile_mcp(mcp_servers)
    opencode_permission = OpenCode.compile_permission(permissions)

    opencode_path = os.path.join(opencode_dir, "opencode.jsonc")

    Config.merge_json_file(
        opencode_path,
        {
            "$schema":    "https://opencode.ai/config.json",
            "permission": opencode_permission,
            "mcp":        opencode_mcp,
            "provider":   agent_cfg.get("provider", {}),
            "model":      agent_cfg.get("model", ""),
            "small_model": agent_cfg.get("small_model", ""),
        },
        overwrite_keys=["permission", "mcp", "provider", "model", "small_model"],
    )

    theme_name = color_scheme.replace(" ", "")
    Config.merge_json_file(
        os.path.join(opencode_dir, "tui.json"),
        {
            "$schema": "https://opencode.ai/tui.json",
            "theme": theme_name,
        },
        overwrite_keys=["theme"],
    )
```

- [x] **Step 5: Update `main()` to use `agents_cfg`**

Replace:
```python
    local_cfg          = master.get("local", {})

    deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents)
    deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks)
    deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents)
    deploy_opencode(paths, color_scheme, permissions, mcp_servers, local_cfg)
```
With:
```python
    agents_cfg         = master.get("agents", {})

    deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents, agent_cfg=agents_cfg.get("antigravity", {}))
    deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, agent_cfg=agents_cfg.get("claude", {}))
    deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents, agent_cfg=agents_cfg.get("codex", {}))
    deploy_opencode(paths, color_scheme, permissions, mcp_servers, agent_cfg=agents_cfg.get("opencode", {}))
```

- [x] **Step 6: Verify syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: No errors.

- [x] **Step 7: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: add agent_cfg param to deploy functions, wire agents_cfg in main()"
```

---

### Task 4: End-to-End Deployment and Verification

- [x] **Step 1: Run deployment**

Run: `bash agents/deploy.sh`
Expected: Exits 0 and prints a backup path line like:
`💾 Backed up N config file(s) to: /home/dai/.agents/backups/YYYYMMDDTHHMMSS/`

- [x] **Step 2: Verify backup directory**

Run: `ls ~/.agents/backups/`
Expected: A timestamped directory containing prefixed backup files such as `claude__settings.json`, `opencode__opencode.jsonc`, etc.

- [x] **Step 3: Verify Claude settings contain `env` key**

Run: `cat ~/.claude/settings.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('env' in d)"`
Expected: `True`

- [x] **Step 4: Verify OpenCode model is correct**

Run: `cat ~/.config/opencode/opencode.jsonc | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('model'))"`
Expected: `ollama/qwen3.6:35b-a3b`

- [x] **Step 5: Verify git status is clean**

Run: `git status`
Expected: Only `agents/__pycache__/` untracked, nothing modified.
