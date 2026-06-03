# Design Spec: Namespace Classes + Remove update_claude_md

## 1. Problem

`agents/compile_configs.py` has 21 module-level functions with no grouping
beyond comment banners. Reading the file requires scanning a long flat list
to understand which helpers belong together.

Additionally, `update_claude_md` dynamically rewrites `~/.claude/CLAUDE.md`
with plugin subagent blocks — a side-effect that adds complexity
(`subagent_blocks` flows through `process_plugins` → `main` → `deploy_claude`)
for limited benefit.

## 2. Solution

### Part A — Remove `update_claude_md` and its cascade

Delete:
- `update_claude_md()` function
- `update_claude_md(...)` call in `deploy_claude()`
- `subagent_blocks` parameter from `deploy_claude()` signature
- `subagent_blocks` from `process_plugins()` return value and internal accumulation
- `subagent_blocks` unpacking in `main()`

`process_plugins` returns `(custom_skills, custom_hooks, custom_subagents)`.

### Part B — Introduce namespace classes

Group the remaining helper functions into five `@staticmethod`-only classes.
No class state, no inheritance — pure namespace grouping.

```
class Toml
    .dict_to_toml(data) -> str
    ._toml_value(v) -> str            # internal helper, stays private
    .parse_toml(content) -> dict

class Config
    .deep_merge(base, overlay) -> dict
    .merge_json_file(path, new_data, overwrite_keys=None)
    .merge_toml_file(path, new_data, overwrite_keys=None)

class Files
    .write_text_file(path, content)
    .safe_copy_file(src, dst)
    .load_deployed(directory) -> set
    .save_deployed(directory, filenames)
    .clean_compiler_owned(directory)

class Symlinks
    .ensure(target, link_name)        # was: ensure_symlink()

class OpenCode
    .compile_mcp(mcp_servers) -> dict
    .compile_permission(permissions) -> dict
```

`process_plugins`, `deploy_antigravity`, `deploy_claude`, `deploy_codex`,
`deploy_opencode`, and `main` stay as module-level functions — they are
orchestration, not utilities.

### Call site changes (representative)

```python
# Before                              # After
merge_json_file(p, d, ...)        →   Config.merge_json_file(p, d, ...)
merge_toml_file(p, d, ...)        →   Config.merge_toml_file(p, d, ...)
deep_merge(a, b)                  →   Config.deep_merge(a, b)
write_text_file(p, c)             →   Files.write_text_file(p, c)
safe_copy_file(s, d)              →   Files.safe_copy_file(s, d)
load_deployed(d)                  →   Files.load_deployed(d)
save_deployed(d, n)               →   Files.save_deployed(d, n)
clean_compiler_owned(d)           →   Files.clean_compiler_owned(d)
ensure_symlink(t, l)              →   Symlinks.ensure(t, l)
compile_opencode_mcp(s)           →   OpenCode.compile_mcp(s)
compile_opencode_permission(p)    →   OpenCode.compile_permission(p)
dict_to_toml(d)                   →   Toml.dict_to_toml(d)
parse_toml(c)                     →   Toml.parse_toml(c)
```

## 3. File Structure

- **Modify only:** `agents/compile_configs.py`
  - Delete `update_claude_md` function.
  - Remove `subagent_blocks` from `process_plugins`, `deploy_claude`, and `main`.
  - Wrap helper functions in five namespace classes using `@staticmethod`.
  - Update all internal call sites to use the new `Class.method()` syntax.

## 4. Verification

1. `python3 -m py_compile agents/compile_configs.py` — no errors.
2. `bash agents/deploy.sh` — completes successfully.
3. Verify `~/.config/opencode/opencode.jsonc` is unchanged.
