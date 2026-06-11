#!/usr/bin/env python3
import copy
import json
import os
import shutil
import sys


# ---------------------------------------------------------------------------
# TOML helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Merge helpers  (fix #1: deep-copy before merge so overwrite values are
#                 pristine originals, not already-merged objects)
# ---------------------------------------------------------------------------

LOCAL_CONFIGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent", ".local_configs")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent", ".cache", "last_deployed")

class PullEngine:
    @staticmethod
    def handle_json(path, generated_data, local_filename, allowed_keys=None):
        local_path = os.path.join(LOCAL_CONFIGS_DIR, local_filename)
        cache_path = os.path.join(CACHE_DIR, local_filename)

        active = {}
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    import re
                    c = re.sub(r'(?<!:)\/\/.*', '', f.read())
                    active = json.loads(c)
            except Exception: pass

        last_deployed = {}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    last_deployed = json.load(f)
            except Exception: pass

        if last_deployed:
            diff, deleted_keys = Config.dict_diff_with_deletions(last_deployed, active)
        else:
            diff = {}
            deleted_keys = []

        if allowed_keys:
            diff = {k: v for k, v in diff.items() if k in allowed_keys}
            deleted_keys = [k for k in deleted_keys if k.split('.')[0] in allowed_keys]

        if diff or deleted_keys:
            os.makedirs(LOCAL_CONFIGS_DIR, exist_ok=True)
            existing = {}
            if os.path.exists(local_path):
                try:
                    with open(local_path) as f: existing = json.load(f)
                except: pass
            merged = Config.deep_merge(existing, diff)
            if deleted_keys:
                merged["_deleted_keys"] = list(set(merged.get("_deleted_keys", []) + deleted_keys))
            with open(local_path, "w") as f:
                json.dump(merged, f, indent=2)
                f.write("\n")
            print(f"📥 Sync: Updated local overrides in {local_path}")

        if os.path.exists(local_path):
            try:
                with open(local_path) as f:
                    override = json.load(f)
                deleted = override.pop("_deleted_keys", [])
                generated_data = Config.deep_merge(generated_data, override)
                for dk in deleted:
                    parts = dk.split('.')
                    curr = generated_data
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            if isinstance(curr, dict) and part in curr:
                                del curr[part]
                        else:
                            if isinstance(curr, dict) and part in curr:
                                curr = curr[part]
                            else:
                                break
            except: pass

        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(generated_data, f, indent=2)
            f.write("\n")

        return generated_data

    @staticmethod
    def handle_toml(path, generated_data, local_filename, allowed_keys=None):
        local_path = os.path.join(LOCAL_CONFIGS_DIR, local_filename)
        cache_path = os.path.join(CACHE_DIR, local_filename)

        active = {}
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    active = Toml.parse_toml(f.read())
            except Exception: pass

        last_deployed = {}
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    last_deployed = Toml.parse_toml(f.read())
            except Exception: pass

        if last_deployed:
            diff, deleted_keys = Config.dict_diff_with_deletions(last_deployed, active)
        else:
            diff = {}
            deleted_keys = []

        if allowed_keys:
            diff = {k: v for k, v in diff.items() if k in allowed_keys}
            deleted_keys = [k for k in deleted_keys if k.split('.')[0] in allowed_keys]

        if diff or deleted_keys:
            os.makedirs(LOCAL_CONFIGS_DIR, exist_ok=True)
            existing = {}
            if os.path.exists(local_path):
                try:
                    with open(local_path) as f: existing = Toml.parse_toml(f.read())
                except: pass
            merged = Config.deep_merge(existing, diff)
            if deleted_keys:
                merged["_deleted_keys"] = list(set(merged.get("_deleted_keys", []) + deleted_keys))
            with open(local_path, "w") as f:
                f.write(Toml.dict_to_toml(merged))
                f.write("\n")
            print(f"📥 Sync: Updated local overrides in {local_path}")

        if os.path.exists(local_path):
            try:
                with open(local_path) as f:
                    override = Toml.parse_toml(f.read())
                deleted = override.pop("_deleted_keys", [])
                generated_data = Config.deep_merge(generated_data, override)
                for dk in deleted:
                    parts = dk.split('.')
                    curr = generated_data
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            if isinstance(curr, dict) and part in curr:
                                del curr[part]
                        else:
                            if isinstance(curr, dict) and part in curr:
                                curr = curr[part]
                            else:
                                break
            except: pass

        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_path, "w") as f:
            f.write(Toml.dict_to_toml(generated_data))
            f.write("\n")

        return generated_data

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
    def dict_diff(base, active):
        """Recursively compute the diff between base and active."""
        diff, _ = Config.dict_diff_with_deletions(base, active)
        return diff

    @staticmethod
    def dict_diff_with_deletions(base, active, prefix=""):
        """Recursively compute diff and deleted keys."""
        diff = {}
        deleted = []

        # Check for additions and modifications
        for k, v in active.items():
            current_path = f"{prefix}{k}"
            if k not in base:
                diff[k] = __import__("copy").deepcopy(v)
            elif isinstance(v, dict) and isinstance(base[k], dict):
                sub_diff, sub_del = Config.dict_diff_with_deletions(base[k], v, current_path + ".")
                if sub_diff: diff[k] = sub_diff
                deleted.extend(sub_del)
            elif isinstance(v, list) and isinstance(base[k], list):
                if v != base[k]:
                    diff[k] = __import__("copy").deepcopy(v)
            elif v != base[k]:
                diff[k] = __import__("copy").deepcopy(v)

        # Check for deletions
        for k in base:
            if k not in active:
                deleted.append(f"{prefix}{k}")

        return diff, deleted

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

    @staticmethod
    def backup(backup_dir, file_paths):
        """
        Copies each existing file in file_paths into backup_dir with a flat filename.
        Silently skips files that do not exist (safe for first-time deploys).
        Returns the list of filenames that were backed up.
        """
        backed_up = []
        for src in file_paths:
            if os.path.isfile(src):
                flat_name = os.path.basename(src)
                dst = os.path.join(backup_dir, flat_name)
                os.makedirs(backup_dir, exist_ok=True)
                Files.safe_copy_file(src, dst)
                backed_up.append(flat_name)
        return backed_up


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

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




# ---------------------------------------------------------------------------
# Symlink helpers
# ---------------------------------------------------------------------------

class Symlinks:
    @staticmethod
    def ensure(target, link_name):
        """
        Ensures that a symlink at `link_name` points to `target`.

        Argument order matches os.symlink(src, dst): target first, link second.

        Handles all pre-existing states at link_name:
          - Correct symlink → no-op (idempotent).
          - Wrong symlink   → remove and re-create.
          - Physical dir    → migrate contents to target (best-effort, skipping
                              files that already exist at the destination), then
                              remove the dir and create the symlink. This migration
                              is not atomic: if interrupted between copy and rmtree,
                              re-running will skip already-migrated items and safely
                              finish — no data loss, but modifications made to the
                              old dir during that window are silently discarded.
          - Physical file   → warn and remove (unusual; no migration needed).
        """
        # C2 fix: resolve relative readlink targets against the symlink's own dir,
        # not against os.getcwd(), to correctly compare paths from any tool.
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
                # I2 fix: warn before silently removing a plain file
                print(f"⚠️  Warning: removing unexpected file at {link_name!r} to create symlink.")
                os.remove(link_name)

        # I3 fix: use abspath so dirname is always non-empty even for bare names
        parent = os.path.dirname(os.path.abspath(link_name))
        os.makedirs(parent, exist_ok=True)
        try:
            os.symlink(target, link_name)
        except OSError as exc:
            raise RuntimeError(
                f"Failed to create symlink {link_name!r} → {target!r}: {exc}"
            ) from exc
        print(f"🔗 Created symlink: {link_name} ➔ {target}")


# ---------------------------------------------------------------------------
# OpenCode config translators
# ---------------------------------------------------------------------------

class OpenCode:
    @staticmethod
    def compile_mcp(mcp_servers):
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

    @staticmethod
    def compile_permission(permissions):
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
                Files.safe_copy_file(src_script, os.path.join(central_skills, skill_name))
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
                Files.safe_copy_file(src_script, os.path.join(central_hooks, hook_name))
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
            Files.write_text_file(
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
        Files.save_deployed(d, names)

    return custom_skills, custom_hooks, custom_subagents


def deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents, agent_cfg={}, backup_dir=None):
    """Deploy Antigravity CLI MCP configuration, settings, and symlinks."""
    antigravity_dir = os.path.join(paths["home"], ".gemini", "antigravity-cli")
    os.makedirs(antigravity_dir, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            os.path.join(antigravity_dir, "settings.json"),
            os.path.join(antigravity_dir, "mcp_config.json"),
        ])

    # Establish symlinks
    Symlinks.ensure(paths["central_skills"], os.path.join(antigravity_dir, "skills"))
    Symlinks.ensure(paths["central_hooks"], os.path.join(antigravity_dir, "hooks"))

    ag_mcp = {"mcpServers": mcp_servers}
    ag_mcp_path = os.path.join(antigravity_dir, "mcp_config.json")
    ag_mcp = PullEngine.handle_json(ag_mcp_path, ag_mcp, "antigravity_mcp.json", ["mcpServers"])
    print("💾 Deploying Antigravity CLI MCP configuration...")
    Config.merge_json_file(ag_mcp_path, ag_mcp, overwrite_keys=["mcpServers"])

    ag_settings = {
        "colorScheme":       color_scheme,
        "permissions":       permissions,
        "statusLine":        {"type": "", "command": "", "enabled": True},
        "trustedWorkspaces": trusted_workspaces,
        "hooks":             custom_hooks,
        "subagents":         custom_subagents,
    }
    ag_settings_path = os.path.join(antigravity_dir, "settings.json")
    ag_settings = PullEngine.handle_json(ag_settings_path, ag_settings, "antigravity_settings.json", ["permissions", "trustedWorkspaces", "hooks", "subagents", "colorScheme"])
    print("💾 Deploying Antigravity CLI settings...")
    Config.merge_json_file(ag_settings_path, ag_settings, overwrite_keys=["permissions", "hooks", "subagents"])


def deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, agent_cfg={}, backup_dir=None):
    """Deploy Claude Code Settings, MCP configuration, and symlinks."""
    claude_dir = os.path.join(paths["home"], ".claude")
    os.makedirs(claude_dir, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            os.path.join(claude_dir, "settings.json"),
            os.path.join(paths["home"], ".claude.json"),
        ])

    # Establish symlinks
    Symlinks.ensure(paths["central_skills"], os.path.join(claude_dir, "skills"))
    Symlinks.ensure(paths["central_hooks"], os.path.join(claude_dir, "hooks"))

    claude_theme = color_scheme
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"

    c_settings = {
        "theme":       claude_theme,
        "permissions": permissions,
        "hooks":       custom_hooks,
        "env":         agent_cfg.get("env", {}),
    }
    c_settings_path = os.path.join(claude_dir, "settings.json")
    c_settings = PullEngine.handle_json(c_settings_path, c_settings, "claude_settings.json", ["theme", "permissions", "hooks", "env"])
    print("💾 Deploying Claude Code settings...")
    Config.merge_json_file(c_settings_path, c_settings, overwrite_keys=["permissions", "hooks", "env"])

    c_mcp = {"mcpServers": mcp_servers}
    c_mcp_path = os.path.join(paths["home"], ".claude.json")
    c_mcp = PullEngine.handle_json(c_mcp_path, c_mcp, "claude_mcp.json", ["mcpServers"])
    print("💾 Deploying Claude Code MCP configuration...")
    Config.merge_json_file(c_mcp_path, c_mcp, overwrite_keys=["mcpServers"])


def deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents, agent_cfg={}, backup_dir=None):
    """Deploy Codex Configuration (TOML) and symlinks."""
    codex_dir = os.path.join(paths["home"], ".codex")
    os.makedirs(codex_dir, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            os.path.join(codex_dir, "config.toml"),
        ])

    # Establish symlinks
    Symlinks.ensure(paths["central_skills"], os.path.join(codex_dir, "skills"))
    Symlinks.ensure(paths["central_hooks"], os.path.join(codex_dir, "hooks"))

    codex_cfg = {
        "color_scheme": color_scheme,
        "model":        agent_cfg.get("model", ""),
        "permissions":  permissions,
        "mcp_servers":  mcp_servers,
        "hooks":        custom_hooks,
        "subagents":    custom_subagents,
    }
    codex_cfg_path = os.path.join(codex_dir, "config.toml")
    codex_cfg = PullEngine.handle_toml(codex_cfg_path, codex_cfg, "codex_config.toml", ["color_scheme", "model", "permissions", "mcp_servers", "hooks", "subagents"])
    print("💾 Deploying Codex config...")
    Config.merge_toml_file(codex_cfg_path, codex_cfg, overwrite_keys=["permissions", "mcp_servers", "hooks", "subagents", "model"])


def deploy_opencode(paths, color_scheme, permissions, mcp_servers, agent_cfg={}, backup_dir=None):
    """Deploy OpenCode Configuration, TUI Config, symlinks, and run obsolete hook cleanup."""
    opencode_dir = os.path.join(paths["home"], ".config", "opencode")
    os.makedirs(opencode_dir, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            os.path.join(opencode_dir, "opencode.jsonc"),
            os.path.join(opencode_dir, "tui.json"),
        ])

    opencode_hooks_path = os.path.join(opencode_dir, "hooks")
    if os.path.islink(opencode_hooks_path):
        os.remove(opencode_hooks_path)
    elif os.path.isdir(opencode_hooks_path):
        shutil.rmtree(opencode_hooks_path)
    Symlinks.ensure(paths["central_skills"], os.path.join(opencode_dir, "commands"))
    Symlinks.ensure(paths["central_subagents"], os.path.join(opencode_dir, "agents"))

    opencode_mcp = OpenCode.compile_mcp(mcp_servers)
    opencode_permission = OpenCode.compile_permission(permissions)

    oc_cfg = {
        "$schema":     "https://opencode.ai/config.json",
        "permission":  opencode_permission,
        "mcp":         opencode_mcp,
        "provider":    agent_cfg.get("provider", {}),
        "model":       agent_cfg.get("model", ""),
        "small_model": agent_cfg.get("small_model", ""),
    }
    oc_path = os.path.join(opencode_dir, "opencode.jsonc")
    oc_cfg = PullEngine.handle_json(oc_path, oc_cfg, "opencode.json", ["permission", "mcp", "provider", "model", "small_model"])
    print("💾 Deploying OpenCode settings...")
    Config.merge_json_file(oc_path, oc_cfg, overwrite_keys=["permission", "mcp", "provider", "model", "small_model"])

    theme_name = color_scheme.replace(" ", "")
    oc_tui = {
        "$schema": "https://opencode.ai/tui.json",
        "theme": theme_name,
    }
    oc_tui_path = os.path.join(opencode_dir, "tui.json")
    oc_tui = PullEngine.handle_json(oc_tui_path, oc_tui, "opencode_tui.json", ["theme"])
    Config.merge_json_file(oc_tui_path, oc_tui, overwrite_keys=["theme"])





# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    home       = os.path.expanduser("~")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    master_path = os.path.join(script_dir, "agent", "master_config.json")

    if not os.path.exists(master_path):
        print(f"❌ Error: Master config not found at {master_path}")
        return 1

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

    # --- 1. Define Common System Configuration Paths ---
    paths = {
        "home":              home,
        "central_skills":    os.path.join(home, ".agents", "skills"),
        "central_hooks":     os.path.join(home, ".agents", "hooks"),
        "central_subagents": os.path.join(home, ".agents", "subagents"),
    }

    for d in ["central_skills", "central_hooks", "central_subagents"]:
        os.makedirs(paths[d], exist_ok=True)
        Files.clean_compiler_owned(paths[d])

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
    import datetime
    agents_cfg  = master.get("agents", {})
    backup_dir  = os.path.join(home, ".agents", "backups",
                               datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))

    # Run the deployments (with auto-sync)
    deploy_antigravity(paths, color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents, agent_cfg=agents_cfg.get("antigravity", {}), backup_dir=backup_dir)
    deploy_claude(paths, color_scheme, permissions, mcp_servers, custom_hooks, agent_cfg=agents_cfg.get("claude", {}), backup_dir=backup_dir)
    deploy_codex(paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents, agent_cfg=agents_cfg.get("codex", {}), backup_dir=backup_dir)
    deploy_opencode(paths, color_scheme, permissions, mcp_servers, agent_cfg=agents_cfg.get("opencode", {}), backup_dir=backup_dir)

    if os.path.isdir(backup_dir):
        backed = os.listdir(backup_dir)
        print(f"💾 Backed up {len(backed)} config file(s) to: {backup_dir}")
    else:
        print("💾 No existing config files to back up (first-time deploy).")

    print("✨ Deploy-time compilation complete! All configs natively built and written to system folders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
