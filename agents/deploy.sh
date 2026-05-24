#!/usr/bin/env bash

set -e

# Resolve paths
DOTFILES_AGENTS_DIR=$(cd "$(dirname "$0")"; pwd)
HOME_DIR="${HOME}"

echo "🚀 Starting Declarative Build & Deployment sequence..."
echo ""

# Make compiler executable locally
chmod +x "${DOTFILES_AGENTS_DIR}/compile_configs.py" || true

# --- Step 1: External Plugin Git Sync ---
if command -v jq &>/dev/null; then
    EXTERNAL_PLUGINS=$(jq -r '.plugins[]' "${DOTFILES_AGENTS_DIR}/agent/manifest.json" 2>/dev/null || echo "")
    if [ -n "${EXTERNAL_PLUGINS}" ]; then
        echo "🔄 [1/3] Syncing remote external plugins..."
        mkdir -p "${DOTFILES_AGENTS_DIR}/plugins/external"
        for plugin_url in ${EXTERNAL_PLUGINS}; do
            repo_name=$(basename "${plugin_url}" .git)
            dest_path="${DOTFILES_AGENTS_DIR}/plugins/external/${repo_name}"
            
            if [ -d "${dest_path}/.git" ]; then
                echo "  🔄 Updating: ${repo_name}..."
                git -C "${dest_path}" pull || echo "  ⚠️ Warning: Failed to pull updates for ${repo_name}"
            else
                echo "  🚀 Cloning: ${repo_name}..."
                git clone "${plugin_url}" "${dest_path}" || echo "  ⚠️ Warning: Failed to clone ${repo_name}"
            fi
        done
    else
        echo "🔄 [1/3] No remote external plugins declared."
    fi
else
    echo "⚠️ Warning: jq not found. Skipping external plugin sync."
fi

echo ""

# --- Step 2: Run Compile & Deploy Engine ---
echo "⚙️ [2/3] Compiling and deploying configurations to active paths..."
python3 "${DOTFILES_AGENTS_DIR}/compile_configs.py"

# Clean up any lingering symlinks at target folders if they exist
for folder in ".gemini/antigravity-cli" ".claude" ".codex" ".config/opencode"; do
    path="${HOME_DIR}/${folder}"
    if [ -L "${path}" ]; then
        echo "  ... Removing obsolete config symlink: ${path}"
        rm -f "${path}"
        mkdir -p "${path}"
    fi
done

# Ensure all deployed shell script capabilities are executable in their system runtimes
echo "🔒 Securing execution permissions on deployed capabilities..."
find "${HOME_DIR}/.gemini/antigravity-cli/skills" "${HOME_DIR}/.gemini/antigravity-cli/hooks" \
     "${HOME_DIR}/.claude/skills" "${HOME_DIR}/.claude/hooks" \
     "${HOME_DIR}/.codex/skills" "${HOME_DIR}/.codex/hooks" \
     "${HOME_DIR}/.config/opencode/commands" "${HOME_DIR}/.config/opencode/hooks" \
     -name "*.sh" -exec chmod +x {} + 2>/dev/null || true

echo ""

# --- Step 3: Standalone External Skills Sync ---
echo "📦 [3/3] Synchronizing standalone outer-world skills..."
if command -v jq &>/dev/null; then
    for agent_key in "antigravity-cli" "claude" "codex" "opencode"; do
        # Map agent keys to the skills CLI agent names
        agent_name=""
        case "${agent_key}" in
            "antigravity-cli") agent_name="antigravity" ;;
            "claude")          agent_name="claude-code" ;;
            "codex")           agent_name="codex" ;;
            "opencode")        agent_name="opencode" ;;
            *)                 agent_name="${agent_key}" ;;
        esac
        
        EXTERNAL_SKILLS=$(jq -r ".skills.\"${agent_key}\".external[]" "${DOTFILES_AGENTS_DIR}/agent/manifest.json" 2>/dev/null || echo "")
        if [ -n "${EXTERNAL_SKILLS}" ]; then
            echo "  📥 Installing skills manifest for ${agent_key} (${agent_name}):"
            for skill in ${EXTERNAL_SKILLS}; do
                echo "    ⚙️ Running: npx skills add ${skill} --global --agent ${agent_name} --yes"
                npx -y skills add "${skill}" --global --agent "${agent_name}" --yes
            done
        fi
    done
else
    echo "  ⚠️ Warning: jq not found. Skipping external skills sync."
fi

echo ""
echo "✨ Deploy successful! Your agent environments are dynamically generated and ready for execution."
