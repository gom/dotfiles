# Namespace Classes and update_claude_md Removal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up `agents/compile_configs.py` by grouping flat helper functions into five namespace classes (`Toml`, `Config`, `Files`, `Symlinks`, `OpenCode`) and deleting the unused dynamic `CLAUDE.md` updates.

**Architecture:**
1. Remove `update_claude_md` function and remove the `subagent_blocks` accumulation cascade.
2. Group TOML helpers into `class Toml`.
3. Group Merge helpers into `class Config`.
4. Group File helpers into `class Files`.
5. Group symlink / translator helpers into `class Symlinks` and `class OpenCode` (renaming them slightly as specified in the design spec).
6. Update all internal and external call sites to use `Class.method()`.

**Tech Stack:** Python 3, Git

---

### Task 1: Remove `update_claude_md` and Cascade

**Files:**
- Modify: `/home/dai/.dotfiles/agents/compile_configs.py`

- [ ] **Step 1: Delete `update_claude_md` function and markers**
Remove the following lines:
```python
CLAUDE_MANAGED_START = "<!-- antigravity:managed:start -->"
CLAUDE_MANAGED_END   = "<!-- antigravity:managed:end -->"


def update_claude_md(path, base_content, subagent_blocks):
    """
    Replaces only the managed block (delimited by HTML comment markers) in
    CLAUDE.md, leaving any content the user wrote outside it untouched.
    On first deploy the managed block is prepended to any existing content.
    """
    managed = (
        f"{CLAUDE_MANAGED_START}\n"
        + base_content
        + "".join(subagent_blocks)
        + f"{CLAUDE_MANAGED_END}\n"
    )

    if not os.path.exists(path):
        write_text_file(path, managed)
        return

    with open(path, "r") as f:
        existing = f.read()

    start = existing.find(CLAUDE_MANAGED_START)
    end   = existing.find(CLAUDE_MANAGED_END)

    if start != -1 and end != -1:
        after  = existing[end + len(CLAUDE_MANAGED_END):].lstrip("\n")
        before = existing[:start]
        updated = before + managed + ("\n" + after if after.strip() else "")
    else:
        # First deploy: prepend managed block, keep existing user content
        updated = managed + ("\n" + existing if existing.strip() else "")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(updated)
```

- [ ] **Step 2: Clean up `process_plugins` return value and internal accumulation**
Update `process_plugins` to remove `subagent_blocks` accumulation:
```python
def process_plugins(plugins_dir, paths):
    """
    Scan the plugins directory, deploy skills, hooks, and subagent profiles to central folders,
    and write deployment manifests.
    Returns:
        tuple: (custom_skills, custom_hooks, custom_subagents)
    """
    plugins_data = []
    if os.path.exists(plugins_dir):
        for root, dirs, files in os.walk(plugins_dir):
            if "plugin.json" in files:
                manifest_path = os.path.join(root, "plugin.json")
                print(f"🔌 Found plugin manifest: {manifest_path}")
                with open(manifest_path, "r") as f:
                    plugin = json.load(f)
                    plugin["_dir"] = root
                    plugins_data.append(plugin)

    custom_skills    = []
    custom_hooks     = []
    custom_subagents = []

    central_skills    = paths["central_skills"]
    central_hooks     = paths["central_hooks"]
    central_subagents = paths["central_subagents"]

    capability_dirs = [central_skills, central_hooks, central_subagents]
    deployed_tracking = {d: set() for d in capability_dirs}

    for plugin in sorted(plugins_data, key=lambda x: x.get("name", "")):
        p_dir = plugin["_dir"]

        # Skills
        for skill in plugin.get("skills", []):
            skill_name = skill["name"]
            src_script = os.path.join(p_dir, skill["script"])
            if os.path.exists(src_script):
                print(f"  ⚡ Deploying skill: {skill_name}")
                safe_copy_file(src_script, os.path.join(central_skills, skill_name))
                deployed_tracking[central_skills].add(skill_name)
                custom_skills.append({
                    "name":        skill_name,
                    "description": skill.get("description", ""),
                })

        # Hooks
        for hook in plugin.get("hooks", []):
            src_script = os.path.join(p_dir, hook["script"])
            if os.path.exists(src_script):
                hook_name = os.path.basename(hook["script"])
                print(f"  🪝 Deploying hook: {hook_name} ({hook.get('event')})")
                safe_copy_file(src_script, os.path.join(central_hooks, hook_name))
                deployed_tracking[central_hooks].add(hook_name)
                custom_hooks.append({
                    "event": hook.get("event", "pre-command"),
                    "name":  hook_name,
                })

        # Subagents
        for agent in plugin.get("agents", []):
            agent_name    = agent["name"]
            system_prompt = agent["system_prompt"]
            print(f"  🤖 Deploying subagent profile: {agent_name}")

            agent_filename = f"{agent_name}.md"
            write_text_file(
                os.path.join(central_subagents, agent_filename),
                f"# {agent_name} Subagent Profile\n\n{system_prompt}\n",
            )
            deployed_tracking[central_subagents].add(agent_filename)

            custom_subagents.append({
                "name":          agent_name,
                "system_prompt": system_prompt,
            })

    # Persist deployment manifests
    for d, names in deployed_tracking.items():
        save_deployed(d, names)

    return custom_skills, custom_hooks, custom_subagents
```

- [ ] **Step 3: Remove `subagent_blocks` from `deploy_claude` signature and implementation**
Update `deploy_claude`:
```python
def deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks):
    """Deploy Claude Code Settings, MCP configuration, and symlinks."""
    claude_dir = os.path.join(paths["home"], ".claude")
    os.makedirs(claude_dir, exist_ok=True)
    
    # Establish symlinks
    ensure_symlink(paths["central_skills"], os.path.join(claude_dir, "skills"))
    ensure_symlink(paths["central_hooks"], os.path.join(claude_dir, "hooks"))

    # Normalise color scheme for Claude (falls back to dark if Tokyo Night is used)
    claude_theme = color_scheme
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"

    print("💾 Deploying Claude Code settings...")
    merge_json_file(
        os.path.join(claude_dir, "settings.json"),
        {
            "theme":       claude_theme,
            "permissions": permissions,
            "hooks":       custom_hooks,
        },
        overwrite_keys=["permissions", "hooks"],
    )

    print("💾 Deploying Claude Code MCP configuration...")
    merge_json_file(
        os.path.join(paths["home"], ".claude.json"),
        {"mcpServers": mcp_servers},
        overwrite_keys=["mcpServers"],
    )
```

- [ ] **Step 4: Update unpacking and function calls inside `main()`**
Update `main()` lines calling `process_plugins` and `deploy_claude`:
```python
    # --- 2. Scan and Process Plugins ---
    plugins_dir = os.path.join(script_dir, "plugins")
    custom_skills, custom_hooks, custom_subagents = process_plugins(
        plugins_dir, paths
    )

    # --- 3. Compile & Deploy Active System Configurations ---
    color_scheme       = master.get("colorScheme", "tokyo night")
    permissions        = master.get("permissions", {})
    mcp_servers        = master.get("mcp_servers", {})
    trusted_workspaces = master.get("trustedWorkspaces", [])
    local_cfg          = master.get("local", {})

    deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents)
    
    deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks)
    
    deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents)
    deploy_opencode(paths, color_scheme, permissions, mcp_servers, local_cfg)
```

- [ ] **Step 5: Verify syntax**
Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 6: Commit**
```bash
git add agents/compile_configs.py
git commit -m "refactor: remove update_claude_md and subagent_blocks cascade"
```

---

### Task 2: Implement Class `Toml` Namespace

**Files:**
- Modify: `/home/dai/.dotfiles/agents/compile_configs.py`

- [ ] **Step 1: Wrap TOML helpers in `class Toml`**
Wrap the functions `dict_to_toml`, `_toml_value`, and `parse_toml` in a class definition with `@staticmethod`:
```python
class Toml:
    @staticmethod
    def dict_to_toml(data):
        """
        Lightweight standard-library TOML serializer supporting nested tables
        and arrays of tables (fix #4: lists of dicts now render as [[section]]).
        """
        output = []

        def serialize(d, prefix=""):
            # First pass: scalar key-value pairs
            for k, v in sorted(d.items()):
                if isinstance(v, dict):
                    continue
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    continue  # handled below as [[array-of-tables]]
                output.append(f"{k} = {Toml._toml_value(v)}")

            # Second pass: nested dicts as [table], lists-of-dicts as [[table]]
            for k, v in sorted(d.items()):
                table_header = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    output.append(f"\n[{table_header}]")
                    serialize(v, table_header)
                elif isinstance(v, list) and v and isinstance(v[0], dict):
                    for item in v:
                        output.append(f"\n[[{table_header}]]")
                        for ik, iv in sorted(item.items()):
                            output.append(f"{ik} = {Toml._toml_value(iv)}")

        serialize(data)
        return "\n".join(output)

    @staticmethod
    def _toml_value(v):
        """Serialize a scalar Python value to a TOML value string."""
        if isinstance(v, str):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(v, bool):
            return str(v).lower()
        if isinstance(v, list):
            items = []
            for x in v:
                if isinstance(x, str):
                    esc = x.replace("\\", "\\\\").replace('"', '\\"')
                    items.append(f'"{esc}"')
                elif isinstance(x, bool):
                    items.append(str(x).lower())
                else:
                    items.append(str(x))
            return f"[{', '.join(items)}]"
        if v is None:
            return '""'
        return str(v)

    @staticmethod
    def parse_toml(content):
        """
        Lightweight line-by-line TOML parser for basic flat/nested configs.
        Limitations (fix #5 documented): no inline tables, no multi-line strings,
        no array-of-tables (lines starting with [[) — sufficient for Codex
        config.toml round-trips on keys produced by dict_to_toml.
        """
        data = {}
        current_table = data

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Standard table header (skip [[...]] array-of-tables lines)
            if line.startswith("[") and line.endswith("]") and not line.startswith("[["):
                table_name = line[1:-1].strip()
                current_table = data
                for part in table_name.split("."):
                    part = part.strip()
                    if part not in current_table or not isinstance(current_table[part], dict):
                        current_table[part] = {}
                    current_table = current_table[part]
            elif "=" in line:
                key, val_str = line.split("=", 1)
                key = key.strip()
                val_str = val_str.strip()

                if val_str.startswith("[") and val_str.endswith("]"):
                    items = []
                    inner = val_str[1:-1].strip()
                    if inner:
                        for x in inner.split(","):
                            x = x.strip()
                            if x.startswith('"') and x.endswith('"'):
                                items.append(x[1:-1].replace('\\"', '"'))
                            elif x == "true":
                                items.append(True)
                            elif x == "false":
                                items.append(False)
                            else:
                                try:
                                    items.append(int(x))
                                except ValueError:
                                    items.append(x)
                    current_table[key] = items
                elif val_str.startswith('"') and val_str.endswith('"'):
                    current_table[key] = val_str[1:-1].replace('\\"', '"')
                elif val_str == "true":
                    current_table[key] = True
                elif val_str == "false":
                    current_table[key] = False
                else:
                    try:
                        current_table[key] = int(val_str)
                    except ValueError:
                        current_table[key] = val_str

        return data
```

- [ ] **Step 2: Update internal references in other functions**
We need to update `merge_toml_file` to call `Toml.parse_toml` and `Toml.dict_to_toml`. Let's wait on this until Task 3 when we wrap `Config` helpers.

- [ ] **Step 3: Verify syntax**
Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 4: Commit**
```bash
git add agents/compile_configs.py
git commit -m "refactor: wrap TOML helpers inside class Toml"
```

---

### Task 3: Implement Class `Config` Namespace

**Files:**
- Modify: `/home/dai/.dotfiles/agents/compile_configs.py`

- [ ] **Step 1: Wrap Merge helpers in `class Config`**
Wrap `deep_merge`, `merge_json_file`, and `merge_toml_file` inside `class Config` with `@staticmethod`. Also update call sites of internal helper `deep_merge` to `Config.deep_merge`, and calls to `parse_toml` & `dict_to_toml` to `Toml.parse_toml` and `Toml.dict_to_toml`:
```python
class Config:
    @staticmethod
    def deep_merge(base, overlay):
        """
        Returns a new dict that is overlay recursively merged onto base.
        Neither input is mutated.
        """
        result = copy.deepcopy(base)
        for k, v in overlay.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = Config.deep_merge(result[k], v)
            else:
                result[k] = copy.deepcopy(v)
        return result

    @staticmethod
    def merge_json_file(path, new_data, overwrite_keys=None):
        """
        Reads an existing JSON file, deep-merges new_data into it (overlay wins),
        then hard-replaces top-level keys listed in overwrite_keys with pristine
        copies of the original new_data values (not the post-merge versions).
        """
        if os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

        # Snapshot BEFORE merging (fix #1)
        overwrite_snapshot = {}
        if overwrite_keys:
            for key in overwrite_keys:
                if key in new_data:
                    overwrite_snapshot[key] = copy.deepcopy(new_data[key])

        existing = {}
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    existing = json.load(f)
                    if not isinstance(existing, dict):
                        existing = {}
            except Exception:
                existing = {}

        merged = Config.deep_merge(existing, new_data)
        merged.update(overwrite_snapshot)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(merged, f, indent=2)
            f.write("\n")

    @staticmethod
    def merge_toml_file(path, new_data, overwrite_keys=None):
        """
        Reads an existing TOML file, deep-merges new_data into it,
        then hard-replaces overwrite_keys with pristine new_data values (fix #1).
        """
        if os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

        overwrite_snapshot = {}
        if overwrite_keys:
            for key in overwrite_keys:
                if key in new_data:
                    overwrite_snapshot[key] = copy.deepcopy(new_data[key])

        existing = {}
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    existing = Toml.parse_toml(f.read())
            except Exception:
                existing = {}

        merged = Config.deep_merge(existing, new_data)
        merged.update(overwrite_snapshot)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(Toml.dict_to_toml(merged))
            f.write("\n")
```

- [ ] **Step 2: Verify syntax**
Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**
```bash
git add agents/compile_configs.py
git commit -m "refactor: wrap merge helpers inside class Config and link to Toml"
```

---

### Task 4: Implement Class `Files` Namespace

**Files:**
- Modify: `/home/dai/.dotfiles/agents/compile_configs.py`

- [ ] **Step 1: Wrap File helpers in `class Files`**
Wrap `write_text_file`, `safe_copy_file`, `load_deployed`, `save_deployed`, and `clean_compiler_owned` inside `class Files` with `@staticmethod`. Also update call to `load_deployed` in `clean_compiler_owned` to `Files.load_deployed`:
```python
DEPLOYED_MANIFEST = ".deployed"


class Files:
    @staticmethod
    def write_text_file(path, content):
        """
        Writes plain text to path, safely removing any pre-existing symlink or
        directory (fix #6: renamed from safe_write_file to clarify it always
        overwrites — use merge_* functions for structured config files).
        """
        if os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)

    @staticmethod
    def safe_copy_file(src, dst):
        """Safely copies a file, removing any pre-existing symlink or file first."""
        if os.path.islink(dst):
            os.remove(dst)
        elif os.path.isdir(dst):
            shutil.rmtree(dst)
        elif os.path.exists(dst):
            os.remove(dst)

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    @staticmethod
    def load_deployed(directory):
        """Returns the set of filenames previously deployed into directory."""
        manifest_path = os.path.join(directory, DEPLOYED_MANIFEST)
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    @staticmethod
    def save_deployed(directory, filenames):
        """Persists the set of compiler-owned filenames for a directory."""
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, DEPLOYED_MANIFEST), "w") as f:
            json.dump(sorted(filenames), f, indent=2)
            f.write("\n")

    @staticmethod
    def clean_compiler_owned(directory):
        """
        Removes only files recorded in the .deployed manifest from a previous run,
        leaving any user-placed or npx-installed files untouched.

        IMPORTANT: must always be called with a physical (non-symlink) directory.
        Passing a symlink here would silently destroy it (C1 guard).
        """
        if os.path.islink(directory):
            # Safety guard: never operate on a symlink — it would remove the link
            # and re-create an empty physical directory, breaking the architecture.
            raise RuntimeError(
                f"clean_compiler_owned called on a symlink: {directory!r}. "
                "Only call this on physical central directories (~/.agents/...)."
            )
        os.makedirs(directory, exist_ok=True)

        for name in Files.load_deployed(directory):
            p = os.path.join(directory, name)
            if os.path.islink(p) or os.path.isfile(p):
                os.remove(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)
```

- [ ] **Step 2: Update call sites in `process_plugins`**
In `process_plugins`:
- `safe_copy_file` -> `Files.safe_copy_file` (lines 492, 505)
- `write_text_file` -> `Files.write_text_file` (line 524)
- `save_deployed` -> `Files.save_deployed` (line 537)

- [ ] **Step 3: Update call sites in `main()`**
In `main()`:
- `clean_compiler_owned` -> `Files.clean_compiler_owned` (line 716)

- [ ] **Step 4: Verify syntax**
Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 5: Commit**
```bash
git add agents/compile_configs.py
git commit -m "refactor: wrap file helpers inside class Files and update call sites"
```

---

### Task 5: Implement Class `Symlinks` and `OpenCode` Namespaces

**Files:**
- Modify: `/home/dai/.dotfiles/agents/compile_configs.py`

- [ ] **Step 1: Wrap `ensure_symlink` in `class Symlinks`**
Define `class Symlinks` with static method `ensure`:
```python
class Symlinks:
    @staticmethod
    def ensure(target, link_name):
        """
        Ensures that a symlink at `link_name` points to `target`.
        Argument order matches os.symlink(src, dst): target first, link second.
        """
        if os.path.islink(link_name):
            existing_target = os.readlink(link_name)
            if not os.path.isabs(existing_target):
                existing_target = os.path.join(
                    os.path.dirname(os.path.abspath(link_name)), existing_target
                )
            if os.path.normpath(existing_target) == os.path.normpath(os.path.abspath(target)):
                return  # Already correctly symlinked
            os.remove(link_name)
        elif os.path.exists(link_name):
            if os.path.isdir(link_name):
                # Migrate any existing files inside to target to prevent data loss
                for item in os.listdir(link_name):
                    src_item = os.path.join(link_name, item)
                    dst_item = os.path.join(target, item)
                    if not os.path.exists(dst_item):
                        if os.path.isdir(src_item):
                            shutil.copytree(src_item, dst_item)
                        else:
                            shutil.copy2(src_item, dst_item)
                shutil.rmtree(link_name)
            else:
                print(f"⚠️  Warning: removing unexpected file at {link_name!r} to create symlink.")
                os.remove(link_name)

        parent = os.path.dirname(os.path.abspath(link_name))
        os.makedirs(parent, exist_ok=True)
        try:
            os.symlink(target, link_name)
        except OSError as exc:
            raise RuntimeError(
                f"Failed to create symlink {link_name!r} → {target!r}: {exc}"
            ) from exc
        print(f"🔗 Created symlink: {link_name} ➔ {target}")
```

- [ ] **Step 2: Wrap OpenCode translators in `class OpenCode`**
Rename functions and define them as static methods `compile_mcp` and `compile_permission` inside `class OpenCode`:
```python
class OpenCode:
    @staticmethod
    def compile_mcp(mcp_servers):
        """
        Translates the unified mcp_servers schema into the OpenCode-specific
        'mcp' block format.
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

    @staticmethod
    def compile_permission(permissions):
        """
        Translates the unified permissions schema into OpenCode's bash
        permission map. The catch-all '*' key defaults to 'ask'.
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

- [ ] **Step 3: Update call sites in Orchestration functions**
Update calls across:
- `deploy_antigravity`:
  - `ensure_symlink` -> `Symlinks.ensure`
  - `merge_json_file` -> `Config.merge_json_file`
- `deploy_claude`:
  - `ensure_symlink` -> `Symlinks.ensure`
  - `merge_json_file` -> `Config.merge_json_file`
- `deploy_codex`:
  - `ensure_symlink` -> `Symlinks.ensure`
  - `merge_toml_file` -> `Config.merge_toml_file`
- `deploy_opencode`:
  - `ensure_symlink` -> `Symlinks.ensure`
  - `compile_opencode_mcp` -> `OpenCode.compile_mcp`
  - `compile_opencode_permission` -> `OpenCode.compile_permission`
  - `merge_json_file` -> `Config.merge_json_file`

- [ ] **Step 4: Verify syntax**
Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 5: Commit**
```bash
git add agents/compile_configs.py
git commit -m "refactor: wrap symlink and opencode helpers, update all remaining call sites"
```

---

### Task 6: System Deployment and Verification

- [ ] **Step 1: Execute deployment script**
Run: `bash agents/deploy.sh`
Expected: The deploy completes with exit status 0 and shows all agents deployed correctly.

- [ ] **Step 2: Verify `~/.config/opencode/opencode.jsonc` validity**
Read `~/.config/opencode/opencode.jsonc` and check that it contains valid JSON/JSONC with the compiled permissions and MCP servers.

- [ ] **Step 3: Verify git status is clean**
Run: `git status`
Expected: Only untracked files are `__pycache__` if any, no other modified files.
