# Design Spec: Agent-Specific Configuration Sections

## 1. Problem

All per-agent configuration is currently either shared globally (e.g. `permissions`, `mcp_servers`) or folded into a single `local` key originally designed for OpenCode only. There is no structured way to express agent-specific settings such as:
- A model name for Codex (`gpt-5.5`), different from OpenCode's model.
- A model for Claude (`claude-opus`).
- Environment variables injected only into Claude Code's `settings.json`.

The `local` key is also a misleading name — it implies "this machine only" rather than "this agent only".

## 2. Solution

Introduce a top-level `agents` key in `master_config.json` (and `master_config.local.json`) to hold per-agent configuration. Replace the existing `local` key entirely.

### Schema

```json
{
  "colorScheme": "...",
  "permissions": { ... },
  "mcp_servers": { ... },
  "agents": {
    "antigravity": {},
    "claude": {
      "env": {
        "ANTHROPIC_MODEL": "claude-opus-4-5",
        "CLAUDE_MAX_TOKENS": "8192"
      }
    },
    "codex": {
      "model": "gpt-5.5"
    },
    "opencode": {
      "model": "ollama/qwen3.6:35b-a3b",
      "small_model": "ollama/gemma4:e4b",
      "provider": { ... }
    }
  }
}
```

Each agent key maps to a dict consumed exclusively by its own `deploy_xxx()` function. Keys not needed by an agent are simply absent.

## 3. Implementation Details

### Part A — Update `master_config.json`
Move the existing `local` block to `agents.opencode`:
```json
{
  "agents": {
    "opencode": {
      "model": "ollama/qwen3.6:35b-a3b",
      "small_model": "ollama/gemma4:e4b",
      "provider": { ... }
    }
  }
}
```
Delete the old `local` top-level key.

### Part B — Pre-deploy Backup

Before any config file is written, `main()` calls a new `backup_configs(home)` function that:
1. Collects all known deployed config file paths.
2. Copies each file that exists to a timestamped backup directory: `~/.agents/backups/YYYY-MM-DDTHHMMSS/`
3. Preserves a flat-name copy using an agent prefix (e.g. `claude__settings.json`, `opencode__opencode.jsonc`) to avoid collisions.
4. Prints the backup path so the user can restore from it if needed.
5. Silently skips files that do not yet exist (first-time deploy).

Backup covers the following files:
| Agent | Files |
|---|---|
| Antigravity | `~/.gemini/antigravity-cli/settings.json`, `mcp_config.json` |
| Claude | `~/.claude/settings.json`, `~/.claude.json` |
| Codex | `~/.codex/config.toml` |
| OpenCode | `~/.config/opencode/opencode.jsonc`, `tui.json` |

### Part C — Update `compile_configs.py`

In `main()`:
- Replace `local_cfg = master.get("local", {})` with:
  ```python
  agents_cfg = master.get("agents", {})
  ```
- Pass the per-agent slice to each `deploy_xxx()` function:
  ```python
  deploy_antigravity(..., agent_cfg=agents_cfg.get("antigravity", {}))
  deploy_claude(...,      agent_cfg=agents_cfg.get("claude", {}))
  deploy_codex(...,       agent_cfg=agents_cfg.get("codex", {}))
  deploy_opencode(...,    agent_cfg=agents_cfg.get("opencode", {}))
  ```

Each `deploy_xxx` function gains an `agent_cfg={}` parameter:

- **`deploy_antigravity`**: no current agent_cfg usage — parameter added for forward compatibility, not used.
- **`deploy_claude`**: writes `agent_cfg.get("env", {})` into `settings.json` under the `env` key, with `overwrite_keys=["permissions", "hooks", "env"]`.
- **`deploy_codex`**: writes `agent_cfg.get("model", "")` into `config.toml`.
- **`deploy_opencode`**: reads `provider`, `model`, `small_model` from `agent_cfg` (replacing `local_cfg`).

## 4. File Structure

- **Modify:** `agents/compile_configs.py` — add `backup_configs()`, update `deploy_xxx()` signatures, update `main()`.
- **Modify:** `agents/agent/master_config.json` — move `local` block to `agents.opencode`, delete `local` key.

## 5. Verification

1. `python3 -m py_compile agents/compile_configs.py` — no errors.
2. `bash agents/deploy.sh` — completes successfully and prints a backup path.
3. Verify `~/.agents/backups/<timestamp>/` exists and contains copies of the pre-deploy config files.
4. Verify `~/.claude/settings.json` contains an `env` key (empty dict `{}` if not configured).
5. Verify `~/.codex/config.toml` contains a `model` key.
6. Verify `~/.config/opencode/opencode.jsonc` contains the correct model and provider.
