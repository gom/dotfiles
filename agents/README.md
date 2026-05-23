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
├── setup.sh                            # Links generated outputs and bespoke configs to system paths
│
├── agent/                              # Master/Shared configurations
│   ├── master_config.json              # Single source of truth for MCP and permissions
│   └── skills_manifest.json            # Manifest of imported outer-world skills
│
├── antigravity-cli/                    # Antigravity CLI generated & bespoke assets
│   ├── settings.json                   # [Compiled] Permissions, theme, trusted directories
│   ├── mcp_config.json                 # [Compiled] Antigravity CLI MCP configurations
│   ├── skills/                         # Git-tracked custom skill scripts
│   └── hooks/                          # Git-tracked custom hooks
│
├── claude/                             # Claude Code generated & bespoke assets
│   ├── settings.json                   # [Compiled] Claude general settings
│   ├── claude.json                     # [Compiled] Master Claude MCP mappings (points to ~/.claude.json)
│   ├── CLAUDE.md                       # Global system prompt/instruction template
│   ├── skills/                         # Claude bespoke skills/tools
│   └── hooks/                          # Claude bespoke execution hooks
│
├── codex/                              # Codex generated & bespoke assets
│   ├── config.toml                     # [Compiled] Codex master config (TOML format)
│   ├── skills/                         # Codex bespoke skills
│   └── hooks/                          # Codex bespoke hooks
│
└── opencode/                           # OpenCode generated & bespoke assets
    ├── opencode.json                   # [Compiled] OpenCode settings (JSON)
    ├── agents/                         # Custom agent markdown profiles
    ├── commands/                       # OpenCode bespoke commands/skills
    └── hooks/                          # OpenCode bespoke hooks
```

---

## 🛠️ Usage

### 1. Update Configurations
Edit the single source of truth under `/home/dai/.dotfiles/agents/agent/master_config.json`.
You can update your allowed permissions list, trusted workspaces, and registered MCP servers there.

### 2. Add Bespoke Skills
Write custom scripts (Python, Node, Bash) inside the respective agent's `skills/` or `hooks/` directory. They will be symlinked to their active system paths.

### 3. Track Outer-World Skills
To import external agent packages, declare them under the `"external"` list inside `agent/skills_manifest.json`.

### 4. Compile & Link Configurations
Run the setup script:
```bash
cd ~/.dotfiles/agents
./setup.sh
```
This runs the compiler to generate target files and establishes symlinks to your system's active directories.
