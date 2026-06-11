import shutil
from pathlib import Path

from deployers.base import AgentDeployer
from utils.config import Config
from utils.fs import Symlinks


# ---------------------------------------------------------------------------
# OpenCode-specific config translators
# ---------------------------------------------------------------------------

def _compile_opencode_mcp(mcp_servers: dict) -> dict:
    """Translate the unified mcp_servers schema into the OpenCode 'mcp' block."""
    result = {}
    for name, cfg in mcp_servers.items():
        if "serverUrl" in cfg:
            result[name] = {"type": "remote", "url": cfg["serverUrl"], "enabled": True}
        elif "command" in cfg:
            entry = {
                "type": "local",
                "command": [cfg["command"]] + cfg.get("args", []),
                "enabled": True,
            }
            if "env" in cfg:
                entry["environment"] = cfg["env"]
            result[name] = entry
    return result


def _compile_opencode_permission(permissions: dict) -> dict:
    """Translate the unified permissions schema into the OpenCode bash permission map."""
    result: dict = {"bash": {"*": "ask"}}
    for level, action in [("allow", "allow"), ("ask", "ask")]:
        for entry in permissions.get(level, []):
            if entry.startswith("command(") and entry.endswith(")"):
                cmd = entry[len("command("):-1].strip()
                result["bash"][cmd] = action
                result["bash"][f"{cmd} *"] = action
    return result


# ---------------------------------------------------------------------------
# Per-agent deployers
# ---------------------------------------------------------------------------

def deploy_antigravity(
    paths: dict[str, Path],
    color_scheme: str,
    permissions: dict,
    mcp_servers: dict,
    trusted_workspaces: list,
    custom_hooks: list,
    custom_subagents: list,
    agent_cfg: dict | None = None,
    backup_dir: Path | None = None,
):
    """Deploy Antigravity CLI MCP configuration, settings, and symlinks."""
    agent_cfg = agent_cfg or {}
    antigravity_dir = paths["home"] / ".gemini" / "antigravity-cli"
    antigravity_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            antigravity_dir / "settings.json",
            antigravity_dir / "mcp_config.json",
        ])

    AgentDeployer.setup_symlinks(antigravity_dir, paths["central_skills"], paths["central_hooks"])

    AgentDeployer.deploy_json(
        "Antigravity MCP config",
        antigravity_dir / "mcp_config.json",
        {"mcpServers": mcp_servers},
        "antigravity_mcp.json",
        ["mcpServers"],
    )
    AgentDeployer.deploy_json(
        "Antigravity settings",
        antigravity_dir / "settings.json",
        {
            "colorScheme":       color_scheme,
            "permissions":       permissions,
            "statusLine":        {"type": "", "command": "", "enabled": True},
            "trustedWorkspaces": trusted_workspaces,
            "hooks":             custom_hooks,
            "subagents":         custom_subagents,
        },
        "antigravity_settings.json",
        ["permissions", "hooks", "subagents"],
    )


def deploy_claude(
    paths: dict[str, Path],
    color_scheme: str,
    permissions: dict,
    mcp_servers: dict,
    custom_hooks: list,
    agent_cfg: dict | None = None,
    backup_dir: Path | None = None,
):
    """Deploy Claude Code settings, MCP configuration, and symlinks."""
    agent_cfg = agent_cfg or {}
    claude_dir = paths["home"] / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            claude_dir / "settings.json",
            paths["home"] / ".claude.json",
        ])

    AgentDeployer.setup_symlinks(claude_dir, paths["central_skills"], paths["central_hooks"])

    claude_theme = "dark" if "tokyo" in color_scheme.lower() else color_scheme

    AgentDeployer.deploy_json(
        "Claude settings",
        claude_dir / "settings.json",
        {
            "theme":       claude_theme,
            "permissions": permissions,
            "hooks":       custom_hooks,
            "env":         agent_cfg.get("env", {}),
        },
        "claude_settings.json",
        ["permissions", "hooks", "env"],
    )
    AgentDeployer.deploy_json(
        "Claude MCP config",
        paths["home"] / ".claude.json",
        {"mcpServers": mcp_servers},
        "claude_mcp.json",
        ["mcpServers"],
    )


def deploy_codex(
    paths: dict[str, Path],
    color_scheme: str,
    permissions: dict,
    mcp_servers: dict,
    custom_hooks: list,
    custom_subagents: list,
    agent_cfg: dict | None = None,
    backup_dir: Path | None = None,
):
    """Deploy Codex configuration (TOML) and symlinks."""
    agent_cfg = agent_cfg or {}
    codex_dir = paths["home"] / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [codex_dir / "config.toml"])

    AgentDeployer.setup_symlinks(codex_dir, paths["central_skills"], paths["central_hooks"])

    AgentDeployer.deploy_toml(
        "Codex config",
        codex_dir / "config.toml",
        {
            "color_scheme": color_scheme,
            "model":        agent_cfg.get("model", ""),
            "permissions":  permissions,
            "mcp_servers":  mcp_servers,
            "hooks":        custom_hooks,
            "subagents":    custom_subagents,
        },
        "codex_config.toml",
        ["permissions", "mcp_servers", "hooks", "subagents", "model"],
    )


def deploy_opencode(
    paths: dict[str, Path],
    color_scheme: str,
    permissions: dict,
    mcp_servers: dict,
    agent_cfg: dict | None = None,
    backup_dir: Path | None = None,
):
    """Deploy OpenCode configuration, TUI config, and symlinks."""
    agent_cfg = agent_cfg or {}
    opencode_dir = paths["home"] / ".config" / "opencode"
    opencode_dir.mkdir(parents=True, exist_ok=True)

    if backup_dir:
        Config.backup(backup_dir, [
            opencode_dir / "opencode.json",
            opencode_dir / "tui.json",
        ])

    # Remove any stale hooks symlink/dir before setting up the new layout
    hooks_path = opencode_dir / "hooks"
    if hooks_path.is_symlink() or hooks_path.is_file():
        hooks_path.unlink()
    elif hooks_path.is_dir():
        shutil.rmtree(hooks_path)

    Symlinks.ensure(paths["central_skills"], opencode_dir / "commands")
    Symlinks.ensure(paths["central_subagents"], opencode_dir / "agents")

    AgentDeployer.deploy_json(
        "OpenCode config",
        opencode_dir / "opencode.json",
        {
            "$schema":     "https://opencode.ai/config.json",
            "permission":  _compile_opencode_permission(permissions),
            "mcp":         _compile_opencode_mcp(mcp_servers),
            "provider":    agent_cfg.get("provider", {}),
            "model":       agent_cfg.get("model", ""),
            "small_model": agent_cfg.get("small_model", ""),
        },
        "opencode.json",
        ["permission", "mcp", "provider", "model", "small_model"],
    )
    AgentDeployer.deploy_json(
        "OpenCode TUI config",
        opencode_dir / "tui.json",
        {
            "$schema": "https://opencode.ai/tui.json",
            "theme":   color_scheme.replace(" ", ""),
        },
        "opencode_tui.json",
        ["theme"],
    )
