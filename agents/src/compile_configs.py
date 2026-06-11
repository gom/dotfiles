#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

from utils.config import Config
from utils.fs import Files
from deployers.manifests import (
    deploy_antigravity,
    deploy_claude,
    deploy_codex,
    deploy_opencode,
)


def process_plugins(plugins_dir: Path, paths: dict[str, Path]) -> tuple[list, list, list]:
    """
    Scan the plugins directory, deploy hooks and subagent profiles to central folders,
    and write deployment manifests.
    Returns:
        tuple: (custom_skills, custom_hooks, custom_subagents)
    """
    plugins_data = []
    if plugins_dir.exists():
        for manifest_path in plugins_dir.rglob("plugin.json"):
            print(f"🔌 Found plugin manifest: {manifest_path}")
            with open(manifest_path, "r") as f:
                plugin = json.load(f)
                plugin["_dir"] = manifest_path.parent
                plugins_data.append(plugin)

    custom_skills:    list = []
    custom_hooks:     list = []
    custom_subagents: list = []

    central_skills    = paths["central_skills"]
    central_hooks     = paths["central_hooks"]
    central_subagents = paths["central_subagents"]

    deployed_tracking: dict[Path, set] = {
        central_skills: set(),
        central_hooks: set(),
        central_subagents: set(),
    }

    for plugin in sorted(plugins_data, key=lambda x: x.get("name", "")):
        p_dir: Path = plugin["_dir"]

        # Skills
        for skill in plugin.get("skills", []):
            skill_name = skill["name"]
            src_script = p_dir / skill["script"]
            if src_script.exists():
                print(f"  ⚡ Deploying skill: {skill_name}")
                Files.safe_copy_file(src_script, central_skills / skill_name)
                deployed_tracking[central_skills].add(skill_name)
                custom_skills.append({
                    "name":        skill_name,
                    "description": skill.get("description", ""),
                })

        # Hooks
        for hook in plugin.get("hooks", []):
            src_script = p_dir / hook["script"]
            if src_script.exists():
                hook_name = src_script.name
                print(f"  🪝 Deploying hook: {hook_name} ({hook.get('event')})")
                Files.safe_copy_file(src_script, central_hooks / hook_name)
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
                central_subagents / agent_filename,
                f"# {agent_name} Subagent Profile\n\n{system_prompt}\n",
            )
            deployed_tracking[central_subagents].add(agent_filename)
            custom_subagents.append({
                "name":          agent_name,
                "system_prompt": system_prompt,
            })

    for d, names in deployed_tracking.items():
        Files.save_deployed(d, names)

    return custom_skills, custom_hooks, custom_subagents


def main() -> int:
    home       = Path.home()
    script_dir = Path(__file__).resolve().parent.parent
    master_path = script_dir / "agent" / "master_config.json"

    if not master_path.exists():
        print(f"❌ Error: Master config not found at {master_path}")
        return 1

    print(f"🔄 Reading master configuration from {master_path}...")
    with open(master_path, "r") as f:
        master: dict = json.load(f)

    # Load machine-specific local overrides if present
    local_path = script_dir / "agent" / "master_config.local.json"
    if local_path.exists():
        print(f"🔄 Found local overrides at {local_path}, merging...")
        try:
            with open(local_path, "r") as f:
                local_master = json.load(f)
                if isinstance(local_master, dict):
                    master = Config.deep_merge(master, local_master)
        except Exception as exc:
            print(f"⚠️ Warning: Failed to read local overrides: {exc}")

    # --- 1. Define Common System Configuration Paths ---
    paths: dict[str, Path] = {
        "home":              home,
        "central_skills":    home / ".agents" / "skills",
        "central_hooks":     home / ".agents" / "hooks",
        "central_subagents": home / ".agents" / "subagents",
    }

    for key in ["central_skills", "central_hooks", "central_subagents"]:
        paths[key].mkdir(parents=True, exist_ok=True)
        Files.clean_compiler_owned(paths[key])

    # --- 2. Scan and Process Plugins ---
    _custom_skills, custom_hooks, custom_subagents = process_plugins(
        script_dir / "plugins", paths
    )

    # --- 3. Compile & Deploy Active System Configurations ---
    color_scheme       = master.get("colorScheme", "tokyo night")
    permissions        = master.get("permissions", {})
    mcp_servers        = master.get("mcp_servers", {})
    trusted_workspaces = master.get("trustedWorkspaces", [])
    agents_cfg         = master.get("agents", {})
    backup_dir         = home / ".agents" / "backups" / datetime.now().strftime("%Y%m%dT%H%M%S")

    deploy_antigravity(
        paths, color_scheme, permissions, mcp_servers,
        trusted_workspaces, custom_hooks, custom_subagents,
        agent_cfg=agents_cfg.get("antigravity"), backup_dir=backup_dir,
    )
    deploy_claude(
        paths, color_scheme, permissions, mcp_servers, custom_hooks,
        agent_cfg=agents_cfg.get("claude"), backup_dir=backup_dir,
    )
    deploy_codex(
        paths, color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents,
        agent_cfg=agents_cfg.get("codex"), backup_dir=backup_dir,
    )
    deploy_opencode(
        paths, color_scheme, permissions, mcp_servers,
        agent_cfg=agents_cfg.get("opencode"), backup_dir=backup_dir,
    )

    if backup_dir.is_dir():
        backed = [f for f in backup_dir.iterdir() if f.is_file()]
        print(f"💾 Backed up {len(backed)} config file(s) to: {backup_dir}")
    else:
        print("💾 No existing config files to back up (first-time deploy).")

    print("✨ Deploy-time compilation complete! All configs natively built and written to system folders.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
