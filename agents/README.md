# Unified Agent Configuration Management

This project provides a **declarative, compiler-based system** to share agent configurations (MCP settings, permissions, keybindings, custom skills, hooks, and subagent rules) across multiple machines and agents.

The targeted agents are:
* **Antigravity CLI**
* **Claude Code**
* **Codex**
* **OpenCode**

---

## 📂 Layout

```
~/.dotfiles/agents/
├── README.md                           # This documentation
├── compile_configs.py                  # Standard-library config compiler (JSON → JSON/TOML)
├── deploy.sh                           # Entrypoint: compile + deploy configs and plugins
│
├── agent/                              # Master/Shared configurations
│   ├── master_config.json              # Single source of truth for MCP, permissions, and theme
│   └── manifest.json                   # External skills and external plugin Git repos
│
└── plugins/                            # Local modular plugins (git-tracked)
    └── my-custom-plugin/               # Custom capabilities: skills, hooks, subagents
        ├── plugin.json                 # Plugin manifest
        └── scripts/                    # Shell scripts for skills and hooks
```

> **Note**: `plugins/external/` (cloned remote plugins) is gitignored and managed automatically by `deploy.sh`.

---

## 🛠️ Usage

### 1. Update Configurations
Edit `~/.dotfiles/agents/agent/master_config.json`.
You can update your allowed permissions list, trusted workspaces, and registered MCP servers there.

### 2. Add Custom Skills, Hooks, & Subagents
Manage your own custom capabilities as **plugins** under `plugins/`:
* Write your script files inside a dedicated plugin directory (e.g. `plugins/my-plugin/`).
* Declare them in `plugin.json`.
* Run `./deploy.sh` — the compiler deploys them to all agents automatically.

### 3. Track Outer-World Skills & Plugins
Register external packages in `~/.dotfiles/agents/agent/manifest.json`:

```json
{
  "skills": {
    "global": [
      "username/common-tool"
    ],
    "claude": {
      "external": [
        "username/claude-specific-tool"
      ]
    }
  },
  "plugins": [
    "https://github.com/username/my-agent-plugin.git"
  ]
}
```

* **`skills.global`**: Installed to **all** agents on every deploy.
* **`skills.<agent>.external`**: Installed only to the specified agent.
* **`plugins`**: Git repos cloned/updated into `plugins/external/` and compiled recursively.

All external skills are installed via `npx skills add` during deployment. They are **not** committed to Git.

### 4. Build & Deploy
```bash
cd ~/.dotfiles/agents
./deploy.sh
```

This compiles configurations, deep-merges them into active system directories, and installs any declared external skills.

### 5. How Merging Works
On each deploy the compiler:
1. Reads the existing config file in the system directory.
2. Deep-merges the compiled settings on top (your local customizations survive).
3. Hard-replaces shared keys (`permissions`, `mcpServers`, `hooks`, `subagents`) with the master values.

`CLAUDE.md` is managed via `<!-- antigravity:managed:start/end -->` markers — content you write outside those markers is preserved.
