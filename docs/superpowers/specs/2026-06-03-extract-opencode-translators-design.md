# Design Spec: Extract OpenCode Translation Functions

## 1. Problem

In `agents/compile_configs.py`, the `main()` function contains two inline
transformation blocks (lines 628–664) that translate the unified `master_config.json`
schema into OpenCode-specific formats:

- **MCP translation** (~20 lines): converts `mcp_servers` entries to OpenCode's
  `type: remote | local` format.
- **Permission translation** (~17 lines): converts `permissions.allow` / `permissions.ask`
  lists of `command(...)` strings into OpenCode's bash permission map.

Both blocks are pure (no side effects, no I/O). Keeping them inline in `main()`
means they cannot be tested or reused without running the entire compiler.

---

## 2. Solution

Extract each block into a named module-level function placed in the existing
**helper functions** section of `compile_configs.py`, just above `main()`.

### `compile_opencode_mcp(mcp_servers: dict) -> dict`

```python
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

### `compile_opencode_permission(permissions: dict) -> dict`

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

### Call site in `main()`

The inline blocks are replaced with:

```python
opencode_mcp        = compile_opencode_mcp(master.get("mcp_servers", {}))
opencode_permission = compile_opencode_permission(master.get("permissions", {}))
```

---

## 3. File Structure

- **Modify only:** `agents/compile_configs.py`
  - Add two functions above `main()` in the helper section.
  - Remove the corresponding inline blocks from `main()`.
  - No new files; no interface changes visible to callers outside the module.

---

## 4. Verification

1. `python3 -m py_compile agents/compile_configs.py` — no errors.
2. `bash agents/deploy.sh` — completes successfully.
3. `cat ~/.config/opencode/opencode.jsonc` — `permission` and `mcp` blocks
   are identical to the pre-refactor output.
