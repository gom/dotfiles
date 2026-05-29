# Declarative Filtered Skill Imports Design

## Overview
We want to allow importing specific, individual skills from multi-skill repositories (such as `https://github.com/mattpocock/skills`) declaratively. Currently, our system only supports adding a repository string under `skills.global`, which automatically installs *all* skills within that repository. This design extends the `manifest.json` schema to support JSON objects containing a `source` and a list of specific `skills` to import.

## Requirements
- **Declarative specification**: Users can specify specific skills in `agents/agent/manifest.json`.
- **Backward compatibility**: Plain string repository URLs continue to work exactly as they do today.
- **Idempotency and safety**: The deployment script parses the entries and invokes the skills installer cleanly.

## Design

### 1. manifest.json
We allow an entry in `skills.global` or `skills.<agent>.external` to be:
- A string representing the repository URL (e.g. `"https://github.com/obra/superpowers"`)
- A JSON object with the format:
  ```json
  {
    "source": "https://github.com/mattpocock/skills",
    "skills": ["grill-me", "grill-with-docs"]
  }
  ```

### 2. deploy.sh
We refactor the skill synchronization steps in `agents/deploy.sh` to:
- Iterate over each entry in JSON representation (`jq -c '...'`).
- Check if the entry starts with `{` to identify JSON objects.
- If it is a JSON object:
  - Extract `.source` using `jq -r '.source'`.
  - Extract `.skills[]` using `jq -r '.skills[]'`, and append each as a `--skill <name>` argument.
- If it is a string:
  - Extract the raw string.
- Run `npx -y skills add <source> <filters> --global --agent <agent> --yes`.

## Test Plan
- Run `./agents/deploy.sh` and verify that `obra/superpowers` is installed completely, while only `grill-me` and `grill-with-docs` are installed from `mattpocock/skills`.
