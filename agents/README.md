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
/home/dai/.dotfiles/agents/
├── README.md                           # This documentation
├── compile_configs.py                  # Standard standard-library config compiler (JSON -> JSON/TOML)
├── deploy.sh                           # Entrypoint to compile and deploy configs and plugins directly to active paths
│
├── agent/                              # Master/Shared configurations
│   ├── master_config.json              # Single source of truth for MCP and permissions
│   └── manifest.json                   # Unified manifest for external skills and external plugins
│
└── plugins/                            # Local modular plugins directory
    └── my-custom-plugin/               # Custom capabilities (skills, hooks, subagents)
        ├── plugin.json                 # Plugin manifest declaring skills, hooks, and subagent rules
        └── scripts/                    # Shell scripts for skills and hooks
```

---

## 🛠️ Usage

### 1. Update Configurations
Edit the single source of truth under `/home/dai/.dotfiles/agents/agent/master_config.json`.
You can update your allowed permissions list, trusted workspaces, and registered MCP servers there.

### 2. Add Custom Skills, Hooks, & Subagents
You manage all your own custom capabilities modularly as **plugins** inside the `plugins/` directory:
* Write your custom script files and prompts inside a dedicated plugin directory (e.g. `plugins/my-custom-plugin/`).
* Declare them in the plugin's `plugin.json` manifest.
* The compiler automatically converts, builds, and deploys them directly into all of your agents' native active directories upon running `deploy.sh`!

### 3. Track Outer-World Skills & Plugins
To import external standalone skills or modular plugins, register them in `/home/dai/.dotfiles/agents/agent/manifest.json`:
* **External Skills**: Add skill package names (e.g. `"vercel-labs/agent-skills"`) under the agent's `"external"` list. They are synchronized via `npx skills` during deployment.
* **External Plugins**: Add the plugin's git repository URL (e.g. `"https://github.com/username/my-agent-plugin.git"`) inside the `"plugins"` list. They are cloned, pulled, and compiled recursively into your active environments automatically.

### 4. Build & Deploy Configurations
Run the deployment script:
```bash
cd ~/.dotfiles/agents
bash deploy.sh
```
This runs the compiler to dynamically build and deploy all configurations and plugin components natively to your system's active directories.
