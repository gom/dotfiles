#!/usr/bin/env python3
import os
import json
import shutil

def dict_to_toml(data):
    """
    A lightweight standard library TOML serializer that converts a Python dictionary 
    into a formatted TOML string, supporting nested tables and arrays.
    """
    output = []
    
    def serialize(d, prefix=""):
        # First, output all simple key-value pairs
        for k, v in sorted(d.items()):
            if not isinstance(v, dict):
                if isinstance(v, str):
                    # Escape backslashes and double quotes
                    escaped = v.replace('\\', '\\\\').replace('"', '\\"')
                    val_str = f'"{escaped}"'
                elif isinstance(v, bool):
                    val_str = str(v).lower()
                elif isinstance(v, list):
                    items = []
                    for x in v:
                        if isinstance(x, str):
                            items.append(f'"{x.replace("\\\\", "\\\\\\\\").replace("\"", "\\\"")}"')
                        elif isinstance(x, bool):
                            items.append(str(x).lower())
                        else:
                            items.append(str(x))
                    val_str = f"[{', '.join(items)}]"
                elif v is None:
                    val_str = '""'
                else:
                    val_str = str(v)
                output.append(f"{k} = {val_str}")
        
        # Next, recursively serialize nested dictionaries as tables
        for k, v in sorted(d.items()):
            if isinstance(v, dict):
                table_header = f"{prefix}.{k}" if prefix else k
                output.append(f"\n[{table_header}]")
                serialize(v, table_header)

    serialize(data)
    return "\n".join(output)

def safe_write_file(path, content, is_json=False):
    """
    Safely writes a file to target path, removing any pre-existing symlinks 
    or conflicting directory structures first.
    """
    if os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
        
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        if is_json:
            json.dump(content, f, indent=2)
            f.write("\n")
        else:
            f.write(content)

def safe_copy_file(src, dst):
    """
    Safely copies a file, removing any pre-existing symlinks or files first.
    """
    if os.path.islink(dst):
        os.remove(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    elif os.path.exists(dst):
        os.remove(dst)
        
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

def clean_target_dir(path):
    """
    Prepares a clean target directory in system paths, removing symlinks or stale files.
    """
    if os.path.islink(path):
        os.remove(path)
    
    if os.path.isdir(path):
        for f in os.listdir(path):
            p = os.path.join(path, f)
            if os.path.islink(p):
                os.remove(p)
            elif os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
    else:
        os.makedirs(path, exist_ok=True)

def deep_merge(existing, new_data):
    """
    Recursively merges new_data into existing dictionary.
    """
    for k, v in new_data.items():
        if k in existing and isinstance(existing[k], dict) and isinstance(v, dict):
            deep_merge(existing[k], v)
        else:
            existing[k] = v
    return existing

def parse_toml(content):
    """
    A very lightweight line-by-line TOML parser for basic Codex configurations.
    """
    data = {}
    current_table = data
    
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        if line.startswith("[") and line.endswith("]"):
            table_name = line[1:-1].strip()
            parts = table_name.split(".")
            current_table = data
            for part in parts:
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

def merge_json_file(path, new_data, overwrite_keys=None):
    """
    Reads an existing JSON file, deep-merges new_data into it (with priority to new_data),
    and completely overwrites specific top-level keys if specified.
    """
    if os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
        
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
    
    if overwrite_keys:
        for key in overwrite_keys:
            if key in new_data:
                merged[key] = new_data[key]
                
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")

def merge_toml_file(path, new_data, overwrite_keys=None):
    """
    Reads an existing TOML file, deep-merges new_data into it,
    and writes it back.
    """
    if os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
        
    existing = {}
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                content = f.read()
            existing = parse_toml(content)
        except Exception:
            existing = {}
            
    merged = deep_merge(existing, new_data)
    
    if overwrite_keys:
        for key in overwrite_keys:
            if key in new_data:
                merged[key] = new_data[key]
                
    toml_str = dict_to_toml(merged)
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(toml_str)
        f.write("\n")

def main():
    # Resolve system and master directories
    home = os.path.expanduser("~")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    master_path = os.path.join(script_dir, "agent", "master_config.json")
    
    if not os.path.exists(master_path):
        print(f"❌ Error: Master config not found at {master_path}")
        return 1
        
    print(f"🔄 Reading master configuration from {master_path}...")
    with open(master_path, "r") as f:
        master = json.load(f)
        
    # --- 1. Define Active System Configurations Directories ---
    antigravity_dir = os.path.join(home, ".gemini", "antigravity-cli")
    claude_dir = os.path.join(home, ".claude")
    codex_dir = os.path.join(home, ".codex")
    opencode_dir = os.path.join(home, ".config", "opencode")
    
    # Clean target directories of compiled components in system paths
    clean_target_dir(os.path.join(antigravity_dir, "skills"))
    clean_target_dir(os.path.join(antigravity_dir, "hooks"))
    clean_target_dir(os.path.join(claude_dir, "skills"))
    clean_target_dir(os.path.join(claude_dir, "hooks"))
    clean_target_dir(os.path.join(codex_dir, "skills"))
    clean_target_dir(os.path.join(codex_dir, "hooks"))
    clean_target_dir(os.path.join(opencode_dir, "commands"))
    clean_target_dir(os.path.join(opencode_dir, "hooks"))
    clean_target_dir(os.path.join(opencode_dir, "agents"))
    
    # Initialize basic files
    claude_md_path = os.path.join(claude_dir, "CLAUDE.md")
    safe_write_file(claude_md_path, (
        "# Claude Code Global Instructions\n\n"
        "This file is dynamically deployed from your unified plugins.\n\n"
        "## Core Guidelines\n"
        "* Prefer standard command line utilities managed via mise.\n"
        "* Follow clean development guidelines for editing code.\n\n"
    ))
        
    # --- 2. Scan and Process Plugins ---
    plugins_dir = os.path.join(script_dir, "plugins")
    plugins_data = []
    if os.path.exists(plugins_dir):
        # Walk directories recursively to scan both bespoke and external subfolders
        for root, dirs, files in os.walk(plugins_dir):
            if "plugin.json" in files:
                manifest_path = os.path.join(root, "plugin.json")
                print(f"🔌 Found plugin manifest: {manifest_path}")
                with open(manifest_path, "r") as f:
                    plugin = json.load(f)
                    plugin["_dir"] = root
                    plugins_data.append(plugin)

    # Accumulators for generated configurations
    custom_skills = []
    custom_hooks = []
    custom_subagents = []

    for plugin in sorted(plugins_data, key=lambda x: x.get("name", "")):
        p_dir = plugin["_dir"]
        
        # Process Skills
        for skill in plugin.get("skills", []):
            skill_name = skill["name"]
            rel_script = skill["script"]
            src_script = os.path.join(p_dir, rel_script)
            
            if os.path.exists(src_script):
                print(f"  ⚡ Deploying skill: {skill_name}")
                # Deploy directly to active system paths!
                safe_copy_file(src_script, os.path.join(antigravity_dir, "skills", skill_name))
                safe_copy_file(src_script, os.path.join(claude_dir, "skills", skill_name))
                safe_copy_file(src_script, os.path.join(codex_dir, "skills", skill_name))
                safe_copy_file(src_script, os.path.join(opencode_dir, "commands", skill_name))
                
                custom_skills.append({
                    "name": skill_name,
                    "description": skill.get("description", "")
                })

        # Process Hooks
        for hook in plugin.get("hooks", []):
            rel_script = hook["script"]
            src_script = os.path.join(p_dir, rel_script)
            
            if os.path.exists(src_script):
                hook_name = os.path.basename(rel_script)
                print(f"  🪝 Deploying hook: {hook_name} ({hook.get('event')})")
                # Deploy directly to active system paths!
                safe_copy_file(src_script, os.path.join(antigravity_dir, "hooks", hook_name))
                safe_copy_file(src_script, os.path.join(claude_dir, "hooks", hook_name))
                safe_copy_file(src_script, os.path.join(codex_dir, "hooks", hook_name))
                safe_copy_file(src_script, os.path.join(opencode_dir, "hooks", hook_name))
                
                custom_hooks.append({
                    "event": hook.get("event", "pre-command"),
                    "name": hook_name
                })

        # Process Subagents
        for agent in plugin.get("agents", []):
            agent_name = agent["name"]
            system_prompt = agent["system_prompt"]
            print(f"  🤖 Deploying subagent profile: {agent_name}")
            
            # Append directly to Claude active CLAUDE.md
            with open(claude_md_path, "a") as f:
                f.write(f"## Subagent Profile: {agent_name}\n")
                f.write(f"> {system_prompt}\n\n")
                
            # Write directly to OpenCode active agents/ directory
            opencode_agent_path = os.path.join(opencode_dir, "agents", f"{agent_name}.md")
            safe_write_file(opencode_agent_path, (
                f"# {agent_name} Subagent Profile\n\n"
                f"{system_prompt}\n"
            ))
                
            custom_subagents.append({
                "name": agent_name,
                "system_prompt": system_prompt
            })

    # --- 3. Compile & Deploy Active System Configurations ---
    mcp_config = {
        "mcpServers": master.get("mcp_servers", {})
    }
    
    # 3.1. Antigravity CLI MCP (JSON)
    antigravity_mcp_path = os.path.join(antigravity_dir, "mcp_config.json")
    print(f"💾 Deploying Antigravity CLI MCP configuration to {antigravity_mcp_path}...")
    merge_json_file(antigravity_mcp_path, mcp_config, overwrite_keys=["mcpServers"])
        
    # 3.2. Antigravity CLI Settings (JSON)
    antigravity_config = {
        "colorScheme": master.get("colorScheme", "tokyo night"),
        "permissions": master.get("permissions", {}),
        "statusLine": {
            "type": "",
            "command": "",
            "enabled": True
        },
        "trustedWorkspaces": master.get("trustedWorkspaces", []),
        "hooks": custom_hooks,
        "subagents": custom_subagents
    }
    antigravity_settings_path = os.path.join(antigravity_dir, "settings.json")
    print(f"💾 Deploying Antigravity CLI settings to {antigravity_settings_path}...")
    merge_json_file(antigravity_settings_path, antigravity_config, overwrite_keys=["permissions", "hooks", "subagents"])
        
    # 3.3. Claude Code Settings (JSON)
    claude_settings = {
        "theme": master.get("colorScheme", "dark"),
        "permissions": master.get("permissions", {}),
        "hooks": custom_hooks
    }
    claude_settings_path = os.path.join(claude_dir, "settings.json")
    print(f"💾 Deploying Claude Code settings to {claude_settings_path}...")
    merge_json_file(claude_settings_path, claude_settings, overwrite_keys=["permissions", "hooks"])
    
    # 3.4. Claude Code MCP (JSON)
    claude_mcp_path = os.path.join(home, ".claude.json")
    print(f"💾 Deploying Claude Code MCP configuration to {claude_mcp_path}...")
    merge_json_file(claude_mcp_path, mcp_config, overwrite_keys=["mcpServers"])
        
    # 3.5. Codex Configuration (TOML)
    codex_data = {
        "color_scheme": master.get("colorScheme", "tokyo night"),
        "permissions": master.get("permissions", {}),
        "mcp_servers": master.get("mcp_servers", {}),
        "hooks": custom_hooks,
        "subagents": custom_subagents
    }
    codex_path = os.path.join(codex_dir, "config.toml")
    print(f"💾 Deploying Codex config to {codex_path}...")
    merge_toml_file(codex_path, codex_data, overwrite_keys=["permissions", "mcp_servers", "hooks", "subagents"])
        
    # 3.6. OpenCode Configuration (JSON)
    opencode_config = {
        "theme": master.get("colorScheme", "tokyo night"),
        "permissions": master.get("permissions", {}),
        "mcpServers": master.get("mcp_servers", {}),
        "hooks": custom_hooks
    }
    opencode_path = os.path.join(opencode_dir, "opencode.json")
    print(f"💾 Deploying OpenCode settings to {opencode_path}...")
    merge_json_file(opencode_path, opencode_config, overwrite_keys=["permissions", "mcpServers", "hooks"])
        
    print("✨ Deploy-time compilation complete! All configs natively built and written to system folders.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
