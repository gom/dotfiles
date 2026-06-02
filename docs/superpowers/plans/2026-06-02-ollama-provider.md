# Ollama Provider Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure OpenCode to support Ollama local models with a dynamic host/container base URL, integrated into the unified declarative dotfiles framework.

**Architecture:** Use OpenCode's native environment variable substitution (`{env:OLLAMA_BASE_URL}`) in `opencode.jsonc`. Define defaults in Zsh and Bash configurations, and add the provider/model settings to `master_config.json` which is compiled and deployed by `compile_configs.py`.

**Tech Stack:** Bash, Zsh, Python 3, JSON

---

### Task 1: Shell environment variables for Ollama

**Files:**
- Modify: `zsh/env.zsh`
- Modify: `.bashrc`

- [ ] **Step 1: Update `zsh/env.zsh`**
  Append the fallback definition of `OLLAMA_BASE_URL` to `zsh/env.zsh`.
  
  ```bash
  # Append to `/home/dai/.dotfiles/zsh/env.zsh`:
  
  ## Ollama
  export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
  ```

- [ ] **Step 2: Update `.bashrc`**
  Append the fallback definition of `OLLAMA_BASE_URL` to `.bashrc`.
  
  ```bash
  # Append to `/home/dai/.dotfiles/.bashrc`:
  
  # Ollama
  export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
  ```

- [ ] **Step 3: Verify syntax of edited shell files**
  Run: `zsh -n zsh/env.zsh && bash -n .bashrc`
  Expected: Command finishes successfully with no syntax errors.

- [ ] **Step 4: Commit shell environment configuration**
  ```bash
  git add zsh/env.zsh .bashrc
  git commit -m "feat: add OLLAMA_BASE_URL environment variable with fallback to shell config files"
  ```

---

### Task 2: Configure Ollama provider and models in master_config.json

**Files:**
- Modify: `agents/agent/master_config.json`

- [ ] **Step 1: Modify `master_config.json` to include the Ollama provider and custom models**
  Integrate the new properties directly in the master config nested inside the `"local"` section.
  
  Replace contents of `/home/dai/.dotfiles/agents/agent/master_config.json` with the following merged content:
  ```json
  {
    "colorScheme": "tokyo night",
    "trustedWorkspaces": [],
    "local": {
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

- [ ] **Step 2: Commit master config change**
  ```bash
  git add agents/agent/master_config.json
  git commit -m "config: define custom Ollama provider and models inside local section in master_config.json"
  ```

---

### Task 3: Support provider and models inside compile_configs.py

**Files:**
- Modify: `agents/compile_configs.py:699-708`

- [ ] **Step 1: Update OpenCode configuration block in `compile_configs.py`**
  Modify `/home/dai/.dotfiles/agents/compile_configs.py` to extract `provider`, `model`, and `small_model` fields from `master.get("local", {})` and merge them in `overwrite_keys`.
  
  Specifically, change this existing block:
  ```python
      merge_json_file(
          opencode_path,
          {
              "$schema": "https://opencode.ai/config.json",
              "permission": opencode_permission,
              "mcp": opencode_mcp,
              "hooks": custom_hooks,
          },
          overwrite_keys=["permission", "mcp", "hooks"],
      )
  ```
  to:
  ```python
      local_cfg = master.get("local", {})
      merge_json_file(
          opencode_path,
          {
              "$schema": "https://opencode.ai/config.json",
              "permission": opencode_permission,
              "mcp": opencode_mcp,
              "hooks": custom_hooks,
              "provider": local_cfg.get("provider", {}),
              "model": local_cfg.get("model", ""),
              "small_model": local_cfg.get("small_model", "")
          },
          overwrite_keys=["permission", "mcp", "hooks", "provider", "model", "small_model"],
      )
  ```

- [ ] **Step 2: Verify Python compilation script syntax**
  Run: `python3 -m py_compile agents/compile_configs.py`
  Expected: Command exits successfully with no output/errors.

- [ ] **Step 3: Commit compilation script updates**
  ```bash
  git add agents/compile_configs.py
  git commit -m "feat: compile and merge provider and model settings into opencode.jsonc"
  ```

---

### Task 4: Deploy and Validate

**Files:**
- Modify: none (Execution only)

- [ ] **Step 1: Execute deployment script**
  Run: `bash agents/deploy.sh`
  Expected: Complete compilation output with no errors.

- [ ] **Step 2: Verify generated `opencode.jsonc` file content**
  Read `/home/dai/.config/opencode/opencode.jsonc` and check that all parsed models, the custom provider, permissions, and the dynamic base URL are present.
  
  Run: `cat ~/.config/opencode/opencode.jsonc`
  Expected: Matches specification perfectly.
