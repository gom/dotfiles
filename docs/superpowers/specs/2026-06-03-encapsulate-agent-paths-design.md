# Design Spec: Encapsulate Agent Paths and Symlinks

## 1. Problem
Currently, the `main()` function in `agents/compile_configs.py` still contains agent-specific paths (`antigravity_dir`, `claude_dir`, etc.) and sets up symlink maps across all agents. This couples `main()` to the directory layout and linking mechanisms of each individual agent.

## 2. Solution
Encapsulate all agent-specific paths, symlinks, and obsolete file cleanups inside their respective `deploy_xxx` functions.
- `main()` will only define system-wide, common paths (`home` and the central store paths `central_skills`, `central_hooks`, `central_subagents`) in a single `paths` dictionary.
- Move agent-specific symlink generation and cleanups into each agent's deployment function.
- Move the `CLAUDE.md` instructions file compilation out of `process_plugins` and into `deploy_claude` where it belongs.

### Refactored Interfaces

#### The `paths` dictionary in `main()`
```python
    paths = {
        "home":              home,
        "central_skills":    os.path.join(home, ".agents", "skills"),
        "central_hooks":     os.path.join(home, ".agents", "hooks"),
        "central_subagents": os.path.join(home, ".agents", "subagents"),
    }
```

#### `process_plugins(plugins_dir, paths) -> (custom_skills, custom_hooks, custom_subagents, subagent_blocks)`
Processes plugins and returns metadata. It does not handle CLAUDE.md or Claude Code paths directly.

#### `deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents)`
Constructs `antigravity_dir`, creates its symlinks, and performs settings/MCP configuration merges.

#### `deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, subagent_blocks)`
Constructs `claude_dir`, creates its symlinks, performs settings/MCP configuration merges, and updates `CLAUDE.md`.

#### `deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents)`
Constructs `codex_dir`, creates its symlinks, and performs Codex TOML configuration merges.

#### `deploy_opencode(paths, color_scheme, permissions, mcp_servers, local_cfg)`
Constructs `opencode_dir`, cleans obsolete hooks folder, creates commands/agents symlinks, and performs OpenCode config merges.

---

## 3. File Structure
- **Modify:** `agents/compile_configs.py`
  - Update `process_plugins()` definition to accept `paths` and remove `CLAUDE.md` updating logic.
  - Update all `deploy_xxx` functions to accept `paths`, construct internal paths, establish symlinks, and execute cleanups.
  - Simplify `main()` to declare the `paths` dictionary, set up and clean the central store directories, and dispatch the function calls.

---

## 4. Verification
1. Run syntax verification: `python3 -m py_compile agents/compile_configs.py`
2. Run config compilation: `bash agents/deploy.sh`
3. Verify that the generated configs remain unchanged and correct.
