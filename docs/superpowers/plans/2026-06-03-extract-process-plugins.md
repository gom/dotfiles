# Extract Plugin Processor Function Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the plugin scanning and processing logic from `main()` in `agents/compile_configs.py` into a focused helper function `process_plugins()`.

**Architecture:** Define `process_plugins()` above the per-agent deploy helper functions. It will encapsulate the filesystem scanning, file copies, updating `CLAUDE.md`, and saving the deployed manifest. Then, update `main()` to invoke this new function and receive the accumulated hooks, skills, and subagent data.

**Tech Stack:** Python 3, bash (for deployment script)

---

### Task 1: Define `process_plugins()` Function

**Files:**
- Modify: `agents/compile_configs.py` (above `# Per-agent deployment helpers`)

- [ ] **Step 1: Write helper function `process_plugins()`**

Insert the new function `process_plugins()` immediately after `compile_opencode_permission` and before `# Per-agent deployment helpers` (or just before `deploy_antigravity`, around line 452).

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

- [ ] **Step 2: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: define process_plugins helper function"
```

---

### Task 2: Integrate `process_plugins()` in `main()`

**Files:**
- Modify: `agents/compile_configs.py`

- [ ] **Step 1: Replace inline scanning block in `main()`**

Locate the block starting with `# --- 2. Scan and Process Plugins ---` (around line 646 pre-refactor) and ending just before `# --- 3. Compile & Deploy Active System Configurations ---` (around line 735).
Replace that block with:

```python
    # --- 2. Scan and Process Plugins ---
    plugins_dir = os.path.join(script_dir, "plugins")
    custom_skills, custom_hooks, custom_subagents, subagent_blocks = process_plugins(
        plugins_dir, claude_dir, central_skills, central_hooks, central_subagents
    )
```

- [ ] **Step 2: Check syntax**

Run: `python3 -m py_compile agents/compile_configs.py`
Expected: Passes with no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add agents/compile_configs.py
git commit -m "refactor: integrate process_plugins in main()"
```

---

### Task 3: Run Deployment and Verification

**Files:**
- Test/Run: `bash agents/deploy.sh`

- [ ] **Step 1: Run deploy script**

Run: `bash agents/deploy.sh`
Expected: Completes successfully with exit code 0.

- [ ] **Step 2: Verify git status is clean**

Ensure that no unstaged changes remain.
Check that the compiler successfully compiled configurations and that CLAUDE.md has been updated correctly.
