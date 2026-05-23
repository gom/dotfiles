#!/usr/bin/env python3
import os
import json

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

def main():
    # Resolve paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    master_path = os.path.join(script_dir, "agent", "master_config.json")
    
    if not os.path.exists(master_path):
        print(f"❌ Error: Master config not found at {master_path}")
        return 1
        
    print(f"🔄 Reading master configuration from {master_path}...")
    with open(master_path, "r") as f:
        master = json.load(f)
        
    # --- 1. Prepare Target Directory Structures ---
    agents = ["antigravity-cli", "claude", "codex", "opencode", "agent"]
    for agent in agents:
        agent_dir = os.path.join(script_dir, agent)
        os.makedirs(agent_dir, exist_ok=True)
        
    # --- 2. Generate Antigravity CLI MCP Configuration (JSON) ---
    mcp_config = {
        "mcpServers": master.get("mcp_servers", {})
    }
    mcp_path = os.path.join(script_dir, "antigravity-cli", "mcp_config.json")
    print(f"💾 Compiling Antigravity CLI MCP configuration to {mcp_path}...")
    with open(mcp_path, "w") as f:
        json.dump(mcp_config, f, indent=2)
        f.write("\n")
        
    # --- 3. Compile Antigravity CLI Configuration ---
    antigravity_config = {
        "colorScheme": master.get("colorScheme", "tokyo night"),
        "permissions": master.get("permissions", {}),
        "statusLine": {
            "type": "",
            "command": "",
            "enabled": True
        },
        "trustedWorkspaces": master.get("trustedWorkspaces", [])
    }
    antigravity_path = os.path.join(script_dir, "antigravity-cli", "settings.json")
    print(f"💾 Compiling Antigravity CLI settings to {antigravity_path}...")
    with open(antigravity_path, "w") as f:
        json.dump(antigravity_config, f, indent=2)
        f.write("\n")
        
    # --- 4. Compile Claude Code Configurations ---
    claude_settings = {
        "theme": master.get("colorScheme", "dark"),
        "permissions": master.get("permissions", {})
    }
    claude_settings_path = os.path.join(script_dir, "claude", "settings.json")
    print(f"💾 Compiling Claude Code settings to {claude_settings_path}...")
    with open(claude_settings_path, "w") as f:
        json.dump(claude_settings, f, indent=2)
        f.write("\n")
        
    claude_mcp_path = os.path.join(script_dir, "claude", "claude.json")
    print(f"💾 Compiling Claude Code MCP configuration to {claude_mcp_path}...")
    with open(claude_mcp_path, "w") as f:
        json.dump(mcp_config, f, indent=2)
        f.write("\n")
        
    # --- 5. Compile Codex Configuration (TOML) ---
    codex_data = {
        "color_scheme": master.get("colorScheme", "tokyo night"),
        "permissions": master.get("permissions", {}),
        "mcp_servers": master.get("mcp_servers", {})
    }
    codex_toml = dict_to_toml(codex_data)
    codex_path = os.path.join(script_dir, "codex", "config.toml")
    print(f"💾 Compiling Codex config to {codex_path}...")
    with open(codex_path, "w") as f:
        f.write(codex_toml)
        f.write("\n")
        
    # --- 6. Compile OpenCode Configuration (JSON) ---
    opencode_config = {
        "theme": master.get("colorScheme", "tokyo night"),
        "permissions": master.get("permissions", {}),
        "mcpServers": master.get("mcp_servers", {})
    }
    opencode_path = os.path.join(script_dir, "opencode", "opencode.json")
    print(f"💾 Compiling OpenCode settings to {opencode_path}...")
    with open(opencode_path, "w") as f:
        json.dump(opencode_config, f, indent=2)
        f.write("\n")
        
    print("✨ Compilation complete! All configuration formats generated successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
