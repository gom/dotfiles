#!/usr/bin/env bash

set -e

# Resolve paths
DOTFILES_AGENTS_DIR=$(cd "$(dirname "$0")"; pwd)

# Locate binaries (useful for first-time installs where mise shims aren't in PATH yet)
MISE_SHIMS_PATH="${HOME}/.local/share/mise/shims"

JQ_BIN="jq"
if ! command -v jq &>/dev/null && [ -x "${MISE_SHIMS_PATH}/jq" ]; then
    JQ_BIN="${MISE_SHIMS_PATH}/jq"
fi

NPX_BIN="npx"
if ! command -v npx &>/dev/null && [ -x "${MISE_SHIMS_PATH}/npx" ]; then
    NPX_BIN="${MISE_SHIMS_PATH}/npx"
fi

echo "🚀 Starting Declarative Build & Deployment sequence..."
echo ""




# Make compiler executable locally
chmod +x "${DOTFILES_AGENTS_DIR}/compile_configs.py" || true

# --- Step 1: External Plugin Git Sync ---
if command -v "${JQ_BIN}" &>/dev/null; then
    EXTERNAL_PLUGINS=$("${JQ_BIN}" -r '.plugins[]' "${DOTFILES_AGENTS_DIR}/agent/manifest.json" 2>/dev/null || echo "")
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
echo "⚙️ [2/3] Compiling and deploying configurations (auto-sync enabled)..."
python3 "${DOTFILES_AGENTS_DIR}/compile_configs.py"

# Clean up any lingering symlinks at target folders if they exist
for folder in ".gemini/antigravity-cli" ".claude" ".codex" ".config/opencode"; do
    path="${HOME}/${folder}"
    if [ -L "${path}" ]; then
        echo "  ... Removing obsolete config symlink: ${path}"
        rm -f "${path}"
        mkdir -p "${path}"
    fi
done

# Ensure all deployed shell script capabilities are executable in their system runtimes
echo "🔒 Securing execution permissions on deployed capabilities..."
find "${HOME}/.agents/skills" "${HOME}/.agents/hooks" \
     -name "*.sh" -exec chmod +x {} + 2>/dev/null || true

echo ""

# --- Step 3: Standalone External Skills Sync ---
echo "📦 [3/3] Synchronizing standalone outer-world skills..."
if command -v "${JQ_BIN}" &>/dev/null; then

    # ---------------------------------------------------------------------------
    # install_skill_entry <json-entry> <agent-name>
    #
    # Handles both manifest entry shapes:
    #   - Plain string  → "https://github.com/obra/superpowers"
    #     Installs all skills from the repo.
    #   - JSON object   → {"source":"...","skills":["grill-me","grill-with-docs"]}
    #     Installs only the listed skills via --skill flags.
    # ---------------------------------------------------------------------------
    install_skill_entry() {
        local entry="${1}"
        local agent_name="${2}"

        if [[ "${entry}" == {* ]]; then
            # JSON object: extract source and build --skill flags
            local source
            source=$(echo "${entry}" | "${JQ_BIN}" -r '.source')
            local skill_flags=""
            while IFS= read -r skill_name; do
                skill_flags="${skill_flags} --skill ${skill_name}"
            done < <(echo "${entry}" | "${JQ_BIN}" -r '.skills[]')
            echo "    ⚙️ Running: ${NPX_BIN} skills add ${source}${skill_flags} --global --agent ${agent_name} --yes"
            # shellcheck disable=SC2086
            "${NPX_BIN}" -y skills add "${source}" ${skill_flags} --global --agent "${agent_name}" --yes || \
                echo "  ⚠️ Warning: failed to install filtered skills from '${source}' for ${agent_name}, continuing..."
        else
            # Plain string: strip surrounding quotes produced by jq -c on a string
            local source
            source=$(echo "${entry}" | "${JQ_BIN}" -r '.')
            echo "    ⚙️ Running: ${NPX_BIN} skills add ${source} --global --agent ${agent_name} --yes"
            "${NPX_BIN}" -y skills add "${source}" --global --agent "${agent_name}" --yes || \
                echo "  ⚠️ Warning: failed to install global skill '${source}', continuing..."
        fi
    }

    # Install global skills once — all agent skill dirs symlink to ~/.agents/skills,
    # so installing once is sufficient and avoids quadruple network calls.
    mapfile -t GLOBAL_ENTRIES < <("${JQ_BIN}" -c '(.skills.global // []) | .[]' "${DOTFILES_AGENTS_DIR}/agent/manifest.json" 2>/dev/null || true)
    if [ ${#GLOBAL_ENTRIES[@]} -gt 0 ]; then
        echo "  🌐 Installing global skills (shared across all agents):"
        for entry in "${GLOBAL_ENTRIES[@]}"; do
            install_skill_entry "${entry}" "antigravity"
        done
    fi

    # Install agent-specific external skills for each agent
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

        mapfile -t AGENT_ENTRIES < <("${JQ_BIN}" -c "(.skills.\"${agent_key}\".external // []) | .[]" "${DOTFILES_AGENTS_DIR}/agent/manifest.json" 2>/dev/null || true)
        if [ ${#AGENT_ENTRIES[@]} -gt 0 ]; then
            echo "  📥 Installing agent-specific skills for ${agent_key} (${agent_name}):"
            for entry in "${AGENT_ENTRIES[@]}"; do
                install_skill_entry "${entry}" "${agent_name}"
            done
        fi
    done
else
    echo "  ⚠️ Warning: jq not found. Skipping external skills sync."
fi

echo ""
echo "✨ Deploy successful! Your agent environments are dynamically generated and ready for execution."
