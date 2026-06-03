#!/usr/bin/env python3
import copy
import json
import os
import shutil
import sys


# ---------------------------------------------------------------------------
# TOML helpers
# ---------------------------------------------------------------------------

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
            output.append(f"{k} = {_toml_value(v)}")

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
                        output.append(f"{ik} = {_toml_value(iv)}")

    serialize(data)
    return "\n".join(output)


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

def deep_merge(base, overlay):
    """
    Returns a new dict that is overlay recursively merged onto base.
    Neither input is mutated.
    """
    result = copy.deepcopy(base)
    for k, v in overlay.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result


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

    merged = deep_merge(existing, new_data)
    merged.update(overwrite_snapshot)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")


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
                existing = parse_toml(f.read())
        except Exception:
            existing = {}

    merged = deep_merge(existing, new_data)
    merged.update(overwrite_snapshot)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(dict_to_toml(merged))
        f.write("\n")


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Deployment tracking (fix #3: only remove compiler-owned files on clean)
# ---------------------------------------------------------------------------

DEPLOYED_MANIFEST = ".deployed"


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


def save_deployed(directory, filenames):
    """Persists the set of compiler-owned filenames for a directory."""
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, DEPLOYED_MANIFEST), "w") as f:
        json.dump(sorted(filenames), f, indent=2)
        f.write("\n")


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

    for name in load_deployed(directory):
        p = os.path.join(directory, name)
        if os.path.islink(p) or os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            shutil.rmtree(p)


# ---------------------------------------------------------------------------
# CLAUDE.md section-marker helpers (fix #2)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Symlink helpers
# ---------------------------------------------------------------------------

def ensure_symlink(target, link_name):
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

    # --- 1. Define Active System Configuration Directories ---
    antigravity_dir = os.path.join(home, ".gemini", "antigravity-cli")
    claude_dir      = os.path.join(home, ".claude")
    codex_dir       = os.path.join(home, ".codex")
    opencode_dir    = os.path.join(home, ".config", "opencode")

    # Define centralized directories under ~/.agents
    agents_base_dir   = os.path.join(home, ".agents")
    central_skills    = os.path.join(agents_base_dir, "skills")
    central_hooks     = os.path.join(agents_base_dir, "hooks")
    central_subagents = os.path.join(agents_base_dir, "subagents")

    os.makedirs(central_skills, exist_ok=True)
    os.makedirs(central_hooks, exist_ok=True)
    os.makedirs(central_subagents, exist_ok=True)

    # Establish the symlinks map from active dirs to the centralized store.
    # Only OpenCode has a first-class "agents" directory concept — Antigravity,
    # Claude Code, and Codex read subagent definitions from settings.json
    # (injected by the compiler), so no subagents symlink is needed for them.
    symlinks_map = {
        os.path.join(antigravity_dir, "skills"):   central_skills,
        os.path.join(antigravity_dir, "hooks"):    central_hooks,
        os.path.join(claude_dir,      "skills"):   central_skills,
        os.path.join(claude_dir,      "hooks"):    central_hooks,
        os.path.join(codex_dir,       "skills"):   central_skills,
        os.path.join(codex_dir,       "hooks"):    central_hooks,
        os.path.join(opencode_dir,    "commands"): central_skills,
        os.path.join(opencode_dir,    "agents"):   central_subagents,
    }

    # Clean up obsolete hooks folder from OpenCode directory if it exists
    opencode_hooks_path = os.path.join(opencode_dir, "hooks")
    if os.path.islink(opencode_hooks_path):
        os.remove(opencode_hooks_path)
    elif os.path.isdir(opencode_hooks_path):
        shutil.rmtree(opencode_hooks_path)

    # Ensure all symlinks are created and point to the centralized store
    for link_name, target in symlinks_map.items():
        ensure_symlink(target, link_name)

    # Clean only previously compiler-owned files from the central directories
    capability_dirs = [central_skills, central_hooks, central_subagents]
    for d in capability_dirs:
        clean_compiler_owned(d)

    # --- 2. Scan and Process Plugins ---
    plugins_dir  = os.path.join(script_dir, "plugins")
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
    subagent_blocks  = []   # collected for CLAUDE.md

    # Track files deployed per directory so we can persist .deployed
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

            subagent_blocks.append(
                f"## Subagent Profile: {agent_name}\n"
                f"> {system_prompt}\n\n"
            )

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

    # Update CLAUDE.md via section markers (fix #2)
    update_claude_md(
        os.path.join(claude_dir, "CLAUDE.md"),
        (
            "# Claude Code Global Instructions\n\n"
            "This file is dynamically deployed from your unified plugins.\n\n"
            "## Core Guidelines\n"
            "* Prefer standard command line utilities managed via mise.\n"
            "* Follow clean development guidelines for editing code.\n\n"
        ),
        subagent_blocks,
    )

    # Persist deployment manifests
    for d, names in deployed_tracking.items():
        save_deployed(d, names)

    # --- 3. Compile & Deploy Active System Configurations ---
    mcp_config = {"mcpServers": master.get("mcp_servers", {})}

    # 3.1  Antigravity CLI MCP
    print("💾 Deploying Antigravity CLI MCP configuration...")
    merge_json_file(
        os.path.join(antigravity_dir, "mcp_config.json"),
        mcp_config,
        overwrite_keys=["mcpServers"],
    )

    # 3.2  Antigravity CLI Settings
    print("💾 Deploying Antigravity CLI settings...")
    merge_json_file(
        os.path.join(antigravity_dir, "settings.json"),
        {
            "colorScheme":       master.get("colorScheme", "tokyo night"),
            "permissions":       master.get("permissions", {}),
            "statusLine":        {"type": "", "command": "", "enabled": True},
            "trustedWorkspaces": master.get("trustedWorkspaces", []),
            "hooks":             custom_hooks,
            "subagents":         custom_subagents,
        },
        overwrite_keys=["permissions", "hooks", "subagents"],
    )

    # 3.3  Claude Code Settings
    print("💾 Deploying Claude Code settings...")
    merge_json_file(
        os.path.join(claude_dir, "settings.json"),
        {
            "theme":       master.get("colorScheme", "dark"),
            "permissions": master.get("permissions", {}),
            "hooks":       custom_hooks,
        },
        overwrite_keys=["permissions", "hooks"],
    )

    # 3.4  Claude Code MCP (~/.claude.json)
    print("💾 Deploying Claude Code MCP configuration...")
    merge_json_file(
        os.path.join(home, ".claude.json"),
        mcp_config,
        overwrite_keys=["mcpServers"],
    )

    # 3.5  Codex Configuration (TOML)
    print("💾 Deploying Codex config...")
    merge_toml_file(
        os.path.join(codex_dir, "config.toml"),
        {
            "color_scheme": master.get("colorScheme", "tokyo night"),
            "permissions":  master.get("permissions", {}),
            "mcp_servers":  master.get("mcp_servers", {}),
            "hooks":        custom_hooks,
            "subagents":    custom_subagents,
        },
        overwrite_keys=["permissions", "mcp_servers", "hooks", "subagents"],
    )

    # 3.6  OpenCode Configuration
    print("💾 Deploying OpenCode settings...")
    
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
            opencode_permission["bash"][cmd + " *"] = "ask"

    # Clean up legacy deprecated keys from opencode.jsonc if it exists.
    # Also migrate/delete the old opencode.json if present.
    opencode_json_path = os.path.join(opencode_dir, "opencode.json")
    opencode_path = os.path.join(opencode_dir, "opencode.jsonc")
    
    existing_opencode = {}
    if os.path.exists(opencode_path):
        try:
            with open(opencode_path, "r") as f:
                existing_opencode = json.load(f)
        except Exception:
            pass
            
    if not existing_opencode and os.path.exists(opencode_json_path):
        try:
            with open(opencode_json_path, "r") as f:
                existing_opencode = json.load(f)
        except Exception:
            pass

    if isinstance(existing_opencode, dict):
        for k in ["theme", "permissions", "mcpServers", "hooks"]:
            existing_opencode.pop(k, None)

    os.makedirs(os.path.dirname(opencode_path), exist_ok=True)
    try:
        with open(opencode_path, "w") as f:
            json.dump(existing_opencode, f, indent=2)
            f.write("\n")
    except Exception:
        pass

    if os.path.exists(opencode_json_path):
        try:
            os.remove(opencode_json_path)
            print("  ... Migrated and removed obsolete opencode.json")
        except Exception:
            pass

    local_cfg = master.get("local", {})
    merge_json_file(
        opencode_path,
        {
            "$schema": "https://opencode.ai/config.json",
            "permission": opencode_permission,
            "mcp": opencode_mcp,
            "provider": local_cfg.get("provider", {}),
            "model": local_cfg.get("model", ""),
            "small_model": local_cfg.get("small_model", "")
        },
        overwrite_keys=["permission", "mcp", "provider", "model", "small_model"],
    )


    # Deploy OpenCode TUI Config (tui.json)
    theme_name = master.get("colorScheme", "tokyonight").replace(" ", "")
    merge_json_file(
        os.path.join(opencode_dir, "tui.json"),
        {
            "$schema": "https://opencode.ai/tui.json",
            "theme": theme_name,
        },
        overwrite_keys=["theme"],
    )

    print("✨ Deploy-time compilation complete! All configs natively built and written to system folders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
