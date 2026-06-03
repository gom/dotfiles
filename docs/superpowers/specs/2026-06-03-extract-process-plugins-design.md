# Design Spec: Extract Plugin Processor Function

## 1. Problem
In `agents/compile_configs.py`, the `main()` function is still about 160 lines long. A significant portion of it (~90 lines) is dedicated to scanning the plugins folder, deploying skills/hooks/subagents, generating `CLAUDE.md`, and saving deployment manifests.

This procedural code is tightly coupled with filesystem reads and writes, making `main()` hard to read, maintain, and test in isolation.

## 2. Solution
Extract the plugin scanning, copying, `CLAUDE.md` generation, and deployment manifest tracking logic from `main()` into a dedicated module-level function `process_plugins()`.

This function will be defined in a new helper section in `agents/compile_configs.py`.

### Function Definition

```python
def process_plugins(plugins_dir, claude_dir, central_skills, central_hooks, central_subagents):
    """
    Scan the plugins directory, deploy skills, hooks, and subagent profiles to central folders,
    update CLAUDE.md global instructions, and write deployment manifests.
    Returns:
        tuple: (custom_skills, custom_hooks, custom_subagents, subagent_blocks)
    """
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

    capability_dirs = [central_skills, central_hooks, central_subagents]
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

    # Update CLAUDE.md via section markers
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

    return custom_skills, custom_hooks, custom_subagents, subagent_blocks
```

### Call Site in `main()`
The inline block inside `main()` is replaced with:

```python
    # --- 2. Scan and Process Plugins ---
    plugins_dir = os.path.join(script_dir, "plugins")
    custom_skills, custom_hooks, custom_subagents, subagent_blocks = process_plugins(
        plugins_dir, claude_dir, central_skills, central_hooks, central_subagents
    )
```

## 3. File Structure
- **Modify:** `agents/compile_configs.py`
  - Add `process_plugins` above `# Per-agent deployment helpers`.
  - Replace inline scanning and processing block in `main()` with `process_plugins(...)` call.

## 4. Verification
1. Run syntax verification: `python3 -m py_compile agents/compile_configs.py`
2. Run config compilation: `bash agents/deploy.sh`
3. Verify that the output files remain unchanged (e.g. `~/.agents/skills/`, `~/.agents/hooks/`, `~/.agents/subagents/`, `~/.claude/CLAUDE.md`, etc.).
