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
    leaving any user-placed or npx-installed files untouched (fix #3).
    """
    if os.path.islink(directory):
        os.remove(directory)
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

    # Clean only previously compiler-owned files (fix #3)
    capability_dirs = [
        os.path.join(antigravity_dir, "skills"),
        os.path.join(antigravity_dir, "hooks"),
        os.path.join(claude_dir,      "skills"),
        os.path.join(claude_dir,      "hooks"),
        os.path.join(codex_dir,       "skills"),
        os.path.join(codex_dir,       "hooks"),
        os.path.join(opencode_dir,    "commands"),
        os.path.join(opencode_dir,    "hooks"),
        os.path.join(opencode_dir,    "agents"),
    ]
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

    # Track files deployed per directory so we can persist .deployed (fix #3)
    deployed_tracking = {d: set() for d in capability_dirs}

    for plugin in sorted(plugins_data, key=lambda x: x.get("name", "")):
        p_dir = plugin["_dir"]

        # Skills
        for skill in plugin.get("skills", []):
            skill_name = skill["name"]
            src_script = os.path.join(p_dir, skill["script"])
            if os.path.exists(src_script):
                print(f"  ⚡ Deploying skill: {skill_name}")
                for d in [
                    os.path.join(antigravity_dir, "skills"),
                    os.path.join(claude_dir,      "skills"),
                    os.path.join(codex_dir,       "skills"),
                    os.path.join(opencode_dir,    "commands"),
                ]:
                    safe_copy_file(src_script, os.path.join(d, skill_name))
                    deployed_tracking[d].add(skill_name)
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
                for d in [
                    os.path.join(antigravity_dir, "hooks"),
                    os.path.join(claude_dir,      "hooks"),
                    os.path.join(codex_dir,       "hooks"),
                    os.path.join(opencode_dir,    "hooks"),
                ]:
                    safe_copy_file(src_script, os.path.join(d, hook_name))
                    deployed_tracking[d].add(hook_name)
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
            agents_dir     = os.path.join(opencode_dir, "agents")
            write_text_file(
                os.path.join(agents_dir, agent_filename),
                f"# {agent_name} Subagent Profile\n\n{system_prompt}\n",
            )
            deployed_tracking[agents_dir].add(agent_filename)

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

    # Persist deployment manifests (fix #3)
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
    merge_json_file(
        os.path.join(opencode_dir, "opencode.json"),
        {
            "theme":       master.get("colorScheme", "tokyo night"),
            "permissions": master.get("permissions", {}),
            "mcpServers":  master.get("mcp_servers", {}),
            "hooks":       custom_hooks,
        },
        overwrite_keys=["permissions", "mcpServers", "hooks"],
    )

    print("✨ Deploy-time compilation complete! All configs natively built and written to system folders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
