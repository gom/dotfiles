# Design Spec: Dynamic Ollama Provider for OpenCode

## 1. Objective
Add support for using a local Ollama instance as the LLM provider in OpenCode.
The configuration must support dynamic switching between the local host (`http://localhost:11434/v1`) and a Docker container environment (`http://ollama:11434/v1`) without modifying the static config files.

---

## 2. Approach: Dynamic Base URL via Environment Variable (Approach A)
We will leverage OpenCode's native environment variable substitution syntax (`{env:OLLAMA_BASE_URL}`).

1. **Config level**: We define `"baseURL": "{env:OLLAMA_BASE_URL}"` in `master_config.json`.
2. **Shell level**: We export a default fallback value for `OLLAMA_BASE_URL` in the user's shell profile files (`.bashrc` and `zsh/env.zsh`):
   ```bash
   export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
   ```
   This ensures that:
   - On a standard host session, it defaults to `http://localhost:11434`.
   - In a Docker container or custom environment, the caller can override `OLLAMA_BASE_URL` to `http://ollama:11434`, and OpenCode will automatically resolve it.

---

## 3. Configuration & Modifying Plan

### 3.1 `agents/agent/master_config.json`
Add a `"local"` section containing the local model configuration:
- Main model: `ollama/qwen3.6:35b-a3b`
- Small model: `ollama/gemma4:e4b`
- Pre-configured models under the `ollama` provider:
  - `qwen3.6:27b`
  - `qwen3.6:35b-a3b`
  - `gemma4:26b`
  - `gemma4:e4b`

```json
  "local": {
    "model": "ollama/qwen3.6:35b-a3b",
    "small_model": "ollama/gemma4:e4b",
    "provider": {
      "ollama": {
        ...
      }
    }
  }
```

### 3.2 `agents/compile_configs.py`
Update the OpenCode compilation section to extract `provider`, `model`, and `small_model` from `master.get("local", {})` and merge them into `/home/dai/.config/opencode/opencode.jsonc`.

### 3.3 Shell Configuration Files
- Append the default `OLLAMA_BASE_URL` to `/home/dai/.dotfiles/.bashrc` and `/home/dai/.dotfiles/zsh/env.zsh`.

---

## 4. Verification & Testing
1. Run `./agents/deploy.sh` to compile and deploy configs.
2. Confirm the deployed `~/.config/opencode/opencode.jsonc` correctly contains:
   - `$schema`
   - Custom provider definitions
   - Target models
   - Natively resolved properties (permissions, MCP servers, hooks)
3. Confirm shell startup profiles export the correct environment variables.
