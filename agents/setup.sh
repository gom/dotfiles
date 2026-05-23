#!/usr/bin/env bash

set -e

# Resolve directories relative to script path
DOTFILES_AGENTS_DIR=$(cd "$(dirname "$0")"; pwd)

echo "🔄 Step 1: Compiling declarations and agent formats..."
python3 "${DOTFILES_AGENTS_DIR}/compile_configs.py"

echo ""
echo "🔗 Step 2: Creating symbolic links and backups..."

# A safe symlink creator
# Usage: safe_link <src> <dst>
safe_link() {
    local src="${1}"
    local dst="${2}"
    
    # Ensure target parent folder exists
    mkdir -p "$(dirname "${dst}")"
    
    if [ -e "${dst}" ] || [ -L "${dst}" ]; then
        if [ "$(readlink "${dst}")" = "${src}" ]; then
            echo "  ✔ Already linked: ${dst} -> ${src}"
            return
        fi
        echo "  📦 Backing up existing path: ${dst} -> ${dst}.bak"
        rm -rf "${dst}.bak"
        mv "${dst}" "${dst}.bak"
    fi
    
    echo "  🚀 Linking: ${dst} -> ${src}"
    ln -s "${src}" "${dst}"
}

# --- Cleanup Obsolete ~/.agents ---
if [ -L "${HOME}/.agents" ] || [ -d "${HOME}/.agents" ]; then
    echo "  🧹 Cleaning up obsolete ~/.agents folder..."
    rm -rf "${HOME}/.agents"
fi

# --- Antigravity CLI Configs ---
safe_link "${DOTFILES_AGENTS_DIR}/antigravity-cli/mcp_config.json" "${HOME}/.gemini/antigravity-cli/mcp_config.json"
safe_link "${DOTFILES_AGENTS_DIR}/antigravity-cli/settings.json" "${HOME}/.gemini/antigravity-cli/settings.json"
safe_link "${DOTFILES_AGENTS_DIR}/antigravity-cli/skills" "${HOME}/.gemini/antigravity-cli/skills"
safe_link "${DOTFILES_AGENTS_DIR}/antigravity-cli/hooks" "${HOME}/.gemini/antigravity-cli/hooks"

# --- Claude Code Configs ---
safe_link "${DOTFILES_AGENTS_DIR}/claude/claude.json" "${HOME}/.claude.json"
safe_link "${DOTFILES_AGENTS_DIR}/claude/settings.json" "${HOME}/.claude/settings.json"
safe_link "${DOTFILES_AGENTS_DIR}/claude/CLAUDE.md" "${HOME}/.claude/CLAUDE.md"
safe_link "${DOTFILES_AGENTS_DIR}/claude/skills" "${HOME}/.claude/skills"
safe_link "${DOTFILES_AGENTS_DIR}/claude/hooks" "${HOME}/.claude/hooks"

# --- Codex Configs ---
safe_link "${DOTFILES_AGENTS_DIR}/codex/config.toml" "${HOME}/.codex/config.toml"
safe_link "${DOTFILES_AGENTS_DIR}/codex/skills" "${HOME}/.codex/skills"
safe_link "${DOTFILES_AGENTS_DIR}/codex/hooks" "${HOME}/.codex/hooks"

# --- OpenCode Configs ---
safe_link "${DOTFILES_AGENTS_DIR}/opencode/opencode.json" "${HOME}/.config/opencode/opencode.json"
safe_link "${DOTFILES_AGENTS_DIR}/opencode/agents" "${HOME}/.config/opencode/agents"
safe_link "${DOTFILES_AGENTS_DIR}/opencode/commands" "${HOME}/.config/opencode/commands"
safe_link "${DOTFILES_AGENTS_DIR}/opencode/hooks" "${HOME}/.config/opencode/hooks"

echo ""
echo "📦 Step 3: Synchronizing external outer-world skills..."
# A simple check for imported outer-world skills list in skills_manifest.json
# We read the outer-world manifest. If they have URLs, we can log them or process them.
if command -v jq &>/dev/null; then
    EXTERNAL_ANTIGRAVITY_SKILLS=$(jq -r '."antigravity-cli".external[]' "${DOTFILES_AGENTS_DIR}/agent/skills_manifest.json" || echo "")
    if [ -n "${EXTERNAL_ANTIGRAVITY_SKILLS}" ]; then
        echo "Found external skills to install for Antigravity CLI:"
        for skill in ${EXTERNAL_ANTIGRAVITY_SKILLS}; do
            echo "  📥 Syncing external skill: ${skill}..."
            # Placeholder command: if user has a skill installer, run it here.
            # e.g., gemini skills install "$skill"
        done
    else
        echo "  ✔ No external skills declared."
    fi
else
    echo "  ⚠️ Warning: jq is not installed. Skipping skills manifest parsing."
fi

echo ""
echo "✨ Setup complete! Your agent configurations are successfully shared and symlinked."
