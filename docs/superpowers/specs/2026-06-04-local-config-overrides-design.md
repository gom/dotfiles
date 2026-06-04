# Design Spec: Local Configuration Overrides

## 1. Problem
Users deploying this dotfiles configuration on different machines (e.g. personal vs. work laptops) have machine-specific configurations. For example, work environments often require dedicated MCP servers, local API keys, or custom AI models. These configurations should not be committed to the public/shared dotfiles repository.

Currently, running `deploy.sh` completely overwrites top-level keys like `mcpServers`, `permissions`, and `model`, making it impossible to run the setup without losing machine-specific configs.

## 2. Solution
Introduce support for a local-only master configuration override file at `agents/agent/master_config.local.json` that will be merged on top of `master_config.json` at deploy-time.

### Part A — Ignore Local Overrides in Git
Add `agents/agent/master_config.local.json` to the repository's `.gitignore` to prevent any machine-specific secrets, keys, or configurations from being accidentally committed.

### Part B — Load and Merge Local Override
Update the compiler engine (`compile_configs.py`) inside `main()` to:
1. Check if `agents/agent/master_config.local.json` exists.
2. If it does, parse it as JSON.
3. Use the existing `Config.deep_merge(master, local_master)` utility to merge the local configuration on top of the global master configuration. The local configuration takes precedence for conflicting keys.
4. If the local file does not exist, fall back to the default master configuration (no-op).

## 3. Implementation Details

### Changes to `.gitignore`
Add the following line:
```
agents/agent/master_config.local.json
```

### Changes to `agents/compile_configs.py`
In `main()`:
```python
    print(f"🔄 Reading master configuration from {master_path}...")
    with open(master_path, "r") as f:
        master = json.load(f)

    # Load machine-specific local overrides if present
    local_path = os.path.join(script_dir, "agent", "master_config.local.json")
    if os.path.exists(local_path):
        print(f"🔄 Found local overrides at {local_path}, merging...")
        try:
            with open(local_path, "r") as f:
                local_master = json.load(f)
                if isinstance(local_master, dict):
                    master = Config.deep_merge(master, local_master)
        except Exception as exc:
            print(f"⚠️ Warning: Failed to read local overrides: {exc}")
```

## 4. Verification
1. Verify python syntax: `python3 -m py_compile agents/compile_configs.py`.
2. Run a dry-run test by creating a mock local override:
   - Create `agents/agent/master_config.local.json` with a custom `colorScheme` (e.g. `"monokai"`).
   - Run `bash agents/deploy.sh`.
   - Verify that the deployed config file (e.g., `~/.config/opencode/tui.json`) has the overridden value (`"monokai"`).
   - Delete the mock file and run `deploy.sh` again to ensure it defaults back to `"tokyo night"`.
3. Check `git status` to ensure `master_config.local.json` is ignored.
