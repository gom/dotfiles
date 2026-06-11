from pathlib import Path
from deployers.base import AgentDeployer
from utils.config import Config
from utils.fs import Symlinks

class OpenCode:
    @staticmethod
    def compile_mcp(mcp_servers):
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

def deploy_antigravity(paths: dict[str, Path], color_scheme, permissions, mcp_servers, trusted_workspaces, custom_hooks, custom_subagents, agent_cfg={}, backup_dir: Path = None):
    antigravity_dir = paths["home"] / ".gemini" / "antigravity-cli"
    antigravity_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            antigravity_dir / "settings.json",
            antigravity_dir / "mcp_config.json",
        ])

    AgentDeployer.setup_symlinks(antigravity_dir, paths["central_skills"], paths["central_hooks"])

    ag_mcp = {"mcpServers": mcp_servers}
    AgentDeployer.deploy_json("Antigravity MCP config", antigravity_dir / "mcp_config.json", ag_mcp, "antigravity_mcp.json", ["mcpServers"])

    ag_settings = {
        "colorScheme":       color_scheme,
        "permissions":       permissions,
        "statusLine":        {"type": "", "command": "", "enabled": True},
        "trustedWorkspaces": trusted_workspaces,
        "hooks":             custom_hooks,
        "subagents":         custom_subagents,
    }
    AgentDeployer.deploy_json("Antigravity settings", antigravity_dir / "settings.json", ag_settings, "antigravity_settings.json", ["permissions", "hooks", "subagents"])


def deploy_claude(paths: dict[str, Path], color_scheme, permissions, mcp_servers, custom_hooks, agent_cfg={}, backup_dir: Path = None):
    claude_dir = paths["home"] / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            claude_dir / "settings.json",
            paths["home"] / ".claude.json",
        ])

    AgentDeployer.setup_symlinks(claude_dir, paths["central_skills"], paths["central_hooks"])

    claude_theme = color_scheme
    if "tokyo" in claude_theme.lower():
        claude_theme = "dark"

    c_settings = {
        "theme":       claude_theme,
        "permissions": permissions,
        "hooks":       custom_hooks,
        "env":         agent_cfg.get("env", {}),
    }
    AgentDeployer.deploy_json("Claude settings", claude_dir / "settings.json", c_settings, "claude_settings.json", ["permissions", "hooks", "env"])

    c_mcp = {"mcpServers": mcp_servers}
    AgentDeployer.deploy_json("Claude MCP config", paths["home"] / ".claude.json", c_mcp, "claude_mcp.json", ["mcpServers"])


def deploy_codex(paths: dict[str, Path], color_scheme, permissions, mcp_servers, custom_hooks, custom_subagents, agent_cfg={}, backup_dir: Path = None):
    codex_dir = paths["home"] / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            codex_dir / "config.toml",
        ])

    AgentDeployer.setup_symlinks(codex_dir, paths["central_skills"], paths["central_hooks"])

    codex_cfg = {
        "color_scheme": color_scheme,
        "model":        agent_cfg.get("model", ""),
        "permissions":  permissions,
        "mcp_servers":  mcp_servers,
        "hooks":        custom_hooks,
        "subagents":    custom_subagents,
    }
    AgentDeployer.deploy_toml("Codex config", codex_dir / "config.toml", codex_cfg, "codex_config.toml", ["permissions", "mcp_servers", "hooks", "subagents", "model"])


def deploy_opencode(paths: dict[str, Path], color_scheme, permissions, mcp_servers, agent_cfg={}, backup_dir: Path = None):
    opencode_dir = paths["home"] / ".config" / "opencode"
    opencode_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            opencode_dir / "opencode.json",
            opencode_dir / "tui.json",
        ])

    opencode_hooks_path = opencode_dir / "hooks"
    if opencode_hooks_path.is_symlink() or opencode_hooks_path.is_file():
        opencode_hooks_path.unlink()
    elif opencode_hooks_path.is_dir():
        import shutil
        shutil.rmtree(opencode_hooks_path)
        
    Symlinks.ensure(paths["central_skills"], opencode_dir / "commands")
    Symlinks.ensure(paths["central_subagents"], opencode_dir / "agents")

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
    AgentDeployer.deploy_json("OpenCode config", opencode_dir / "opencode.json", oc_cfg, "opencode.json", ["permission", "mcp", "provider", "model", "small_model"])

    theme_name = color_scheme.replace(" ", "")
    oc_tui = {
        "$schema": "https://opencode.ai/tui.json",
        "theme": theme_name,
    }
    AgentDeployer.deploy_json("OpenCode TUI config", opencode_dir / "tui.json", oc_tui, "opencode_tui.json", ["theme"])
