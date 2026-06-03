# Extract OpenCode Translator Functions — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the two inline OpenCode translation blocks from `main()` into named, testable module-level functions.

**Architecture:** Pure function extraction within `agents/compile_configs.py`. No new files. No interface changes for callers outside the module.

**Tech Stack:** Python 3, Git

---

### Task 1: Add `compile_opencode_mcp()` function

**Files:**
- Modify: `agents/compile_configs.py` (insert above `main()`)

- [ ] **Step 1: Insert `compile_opencode_mcp` above `main()`**

  Insert the following block at line 410 (just before the `# ---------------------------------------------------------------------------\n# Main` comment block):

  ```python
  # ---------------------------------------------------------------------------
  # OpenCode config translators
  # ---------------------------------------------------------------------------

  def compile_opencode_mcp(mcp_servers):
      """
      Translates the unified mcp_servers schema into the OpenCode-specific
      'mcp' block format.
        - Entries with 'serverUrl' → type: remote
        - Entries with 'command'   → type: local (with optional 'env')
      """
      result = {}
      for name, cfg in mcp_servers.items():
          if "serverUrl" in cfg:
              result[name] = {"type": "remote", "url": cfg["serverUrl"], "enabled": True}
          elif "command" in cfg:
              cmd_list = [cfg["command"]] + cfg.get("args", [])
              result[name] = {"type": "local", "command": cmd_list, "enabled": True}
              if "env" in cfg:
                  result[name]["environment"] = cfg["env"]
      return result
  ```

- [ ] **Step 2: Replace the inline MCP block in `main()` with a call**

  In `main()`, find and remove the existing inline block (lines ~628–646):
  ```python
      # Compile OpenCode MCP config
      opencode_mcp = {}
      for name, cfg in master.get("mcp_servers", {}).items():
          if "serverUrl" in cfg:
              opencode_mcp[name] = {
                  "type": "remote",
                  "url": cfg["serverUrl"],
                  "enabled": True
              }
          elif "command" in cfg:
              cmd_list = [cfg["command"]]
              if "args" in cfg:
                  cmd_list.extend(cfg["args"])
              opencode_mcp[name] = {
                  "type": "local",
                  "command": cmd_list,
                  "enabled": True
              }
              if "env" in cfg:
                  opencode_mcp[name]["environment"] = cfg["env"]
  ```

  Replace it with:
  ```python
      opencode_mcp = compile_opencode_mcp(master.get("mcp_servers", {}))
  ```

- [ ] **Step 3: Verify syntax**

  Run: `python3 -m py_compile agents/compile_configs.py`
  Expected: exits with no output.

---

### Task 2: Add `compile_opencode_permission()` function

**Files:**
- Modify: `agents/compile_configs.py`

- [ ] **Step 1: Insert `compile_opencode_permission` below `compile_opencode_mcp`**

  Add immediately after `compile_opencode_mcp`:

  ```python
  def compile_opencode_permission(permissions):
      """
      Translates the unified permissions schema into OpenCode's bash
      permission map. The catch-all '*' key defaults to 'ask'.
      Each command(X) entry in 'allow'/'ask' produces two keys: X and 'X *'.
      """
      result = {"bash": {"*": "ask"}}
      for entry in permissions.get("allow", []):
          if entry.startswith("command(") and entry.endswith(")"):
              cmd = entry[len("command("):-1].strip()
              result["bash"][cmd] = "allow"
              result["bash"][cmd + " *"] = "allow"
      for entry in permissions.get("ask", []):
          if entry.startswith("command(") and entry.endswith(")"):
              cmd = entry[len("command("):-1].strip()
              result["bash"][cmd] = "ask"
              result["bash"][cmd + " *"] = "ask"
      return result
  ```

- [ ] **Step 2: Replace the inline permission block in `main()` with a call**

  In `main()`, find and remove the existing inline block (lines ~648–664):
  ```python
      # Compile OpenCode permissions block
      opencode_permission = {
          "bash": {
              "*": "ask"
          }
      }
      raw_permissions = master.get("permissions", {})
      for entry in raw_permissions.get("allow", []):
          if entry.startswith("command(") and entry.endswith(")"):
              cmd = entry[len("command("):-1].strip()
              opencode_permission["bash"][cmd] = "allow"
              opencode_permission["bash"][cmd + " *"] = "allow"
      for entry in raw_permissions.get("ask", []):
          if entry.startswith("command(") and entry.endswith(")"):
              cmd = entry[len("command("):-1].strip()
              opencode_permission["bash"][cmd] = "ask"
              opencode_permission["bash"][cmd + \" *\"] = "ask"
  ```

  Replace it with:
  ```python
      opencode_permission = compile_opencode_permission(master.get("permissions", {}))
  ```

- [ ] **Step 3: Verify syntax**

  Run: `python3 -m py_compile agents/compile_configs.py`
  Expected: exits with no output.

---

### Task 3: Commit, deploy, and validate

**Files:**
- none (execution only)

- [ ] **Step 1: Commit**

  ```bash
  git add agents/compile_configs.py
  git commit -m "refactor: extract compile_opencode_mcp and compile_opencode_permission from main()"
  ```

- [ ] **Step 2: Deploy**

  Run: `bash agents/deploy.sh`
  Expected: completes with `✨ Deploy successful!`

- [ ] **Step 3: Validate `opencode.jsonc` is unchanged**

  Run: `cat ~/.config/opencode/opencode.jsonc`
  Expected: `permission` and `mcp` blocks are identical to before the refactor — all four MCP servers present, all permission entries present.
