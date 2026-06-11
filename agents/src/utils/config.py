import copy
import json
import os
import shutil
from pathlib import Path
from utils.toml import Toml
from utils.fs import Files

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_CONFIGS_DIR = BASE_DIR / "agent" / ".local_configs"
CACHE_DIR = BASE_DIR / "agent" / ".cache" / "last_deployed"

class Config:
    @staticmethod
    def deep_merge(base, overlay):
        """
        Returns a new dict that is overlay recursively merged onto base.
        Neither input is mutated.
        """
        result = copy.deepcopy(base)
        for k, v in overlay.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = Config.deep_merge(result[k], v)
            else:
                result[k] = copy.deepcopy(v)
        return result

    @staticmethod
    def dict_diff(base, active):
        """Recursively compute the diff between base and active."""
        diff, _ = Config.dict_diff_with_deletions(base, active)
        return diff

    @staticmethod
    def dict_diff_with_deletions(base, active, prefix=""):
        """Recursively compute diff and deleted keys."""
        diff = {}
        deleted = []

        # Check for additions and modifications
        for k, v in active.items():
            current_path = f"{prefix}{k}"
            if k not in base:
                diff[k] = copy.deepcopy(v)
            elif isinstance(v, dict) and isinstance(base[k], dict):
                sub_diff, sub_del = Config.dict_diff_with_deletions(base[k], v, current_path + ".")
                if sub_diff: diff[k] = sub_diff
                deleted.extend(sub_del)
            elif isinstance(v, list) and isinstance(base[k], list):
                if v != base[k]:
                    diff[k] = copy.deepcopy(v)
            elif v != base[k]:
                diff[k] = copy.deepcopy(v)

        # Check for deletions
        for k in base:
            if k not in active:
                deleted.append(f"{prefix}{k}")

        return diff, deleted

    @staticmethod
    def merge_json_file(path: str | Path, new_data, overwrite_keys=None):
        """
        Reads an existing JSON file, deep-merges new_data into it (overlay wins),
        then hard-replaces top-level keys listed in overwrite_keys with pristine
        copies of the original new_data values.
        """
        p = Path(path)
        if p.is_symlink() or p.is_file():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p)

        overwrite_snapshot = {}
        if overwrite_keys:
            for key in overwrite_keys:
                if key in new_data:
                    overwrite_snapshot[key] = copy.deepcopy(new_data[key])

        existing = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    existing = json.load(f)
                    if not isinstance(existing, dict):
                        existing = {}
            except Exception:
                existing = {}

        merged = Config.deep_merge(existing, new_data)
        merged.update(overwrite_snapshot)

        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            json.dump(merged, f, indent=2)
            f.write("\n")

    @staticmethod
    def merge_toml_file(path: str | Path, new_data, overwrite_keys=None):
        """
        Reads an existing TOML file, deep-merges new_data into it,
        then hard-replaces overwrite_keys with pristine new_data values.
        """
        p = Path(path)
        if p.is_symlink() or p.is_file():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p)

        overwrite_snapshot = {}
        if overwrite_keys:
            for key in overwrite_keys:
                if key in new_data:
                    overwrite_snapshot[key] = copy.deepcopy(new_data[key])

        existing = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    existing = Toml.parse_toml(f.read())
            except Exception:
                existing = {}

        merged = Config.deep_merge(existing, new_data)
        merged.update(overwrite_snapshot)

        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            f.write(Toml.dict_to_toml(merged))
            f.write("\n")

    @staticmethod
    def backup(backup_dir: str | Path, file_paths: list[str | Path]):
        """
        Copies each existing file in file_paths into backup_dir with a flat filename.
        Silently skips files that do not exist.
        Returns the list of filenames that were backed up.
        """
        backed_up = []
        p_backup = Path(backup_dir)
        for src in file_paths:
            p_src = Path(src)
            if p_src.is_file():
                flat_name = p_src.name
                dst = p_backup / flat_name
                p_backup.mkdir(parents=True, exist_ok=True)
                Files.safe_copy_file(p_src, dst)
                backed_up.append(flat_name)
        return backed_up

class PullEngine:
    @staticmethod
    def handle_json(path: str | Path, generated_data, local_filename, allowed_keys=None):
        if allowed_keys is None:
            allowed_keys = [k for k in generated_data.keys() if not k.startswith('$')]
        p = Path(path)
        local_path = LOCAL_CONFIGS_DIR / local_filename
        cache_path = CACHE_DIR / local_filename

        active = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    import re
                    c = re.sub(r'(?<!:)\/\/.*', '', f.read())
                    active = json.loads(c)
            except Exception: pass

        last_deployed = {}
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    last_deployed = json.load(f)
            except Exception: pass

        if last_deployed:
            diff, deleted_keys = Config.dict_diff_with_deletions(last_deployed, active)
        else:
            diff = {}
            deleted_keys = []

        if allowed_keys:
            diff = {k: v for k, v in diff.items() if k in allowed_keys}
            deleted_keys = [k for k in deleted_keys if k.split('.')[0] in allowed_keys]

        if diff or deleted_keys:
            LOCAL_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
            existing = {}
            if local_path.exists():
                try:
                    with open(local_path) as f: existing = json.load(f)
                except: pass
            merged = Config.deep_merge(existing, diff)
            if deleted_keys:
                merged["_deleted_keys"] = list(set(merged.get("_deleted_keys", []) + deleted_keys))
            with open(local_path, "w") as f:
                json.dump(merged, f, indent=2)
                f.write("\n")
            print(f"📥 Sync: Updated local overrides in {local_path}")

        if local_path.exists():
            try:
                with open(local_path) as f:
                    override = json.load(f)
                deleted = override.pop("_deleted_keys", [])
                generated_data = Config.deep_merge(generated_data, override)
                for dk in deleted:
                    parts = dk.split('.')
                    curr = generated_data
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            if isinstance(curr, dict) and part in curr:
                                del curr[part]
                        else:
                            if isinstance(curr, dict) and part in curr:
                                curr = curr[part]
                            else:
                                break
            except: pass

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(generated_data, f, indent=2)
            f.write("\n")

        return generated_data

    @staticmethod
    def handle_toml(path: str | Path, generated_data, local_filename, allowed_keys=None):
        if allowed_keys is None:
            allowed_keys = [k for k in generated_data.keys() if not k.startswith('$')]
        p = Path(path)
        local_path = LOCAL_CONFIGS_DIR / local_filename
        cache_path = CACHE_DIR / local_filename

        active = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    active = Toml.parse_toml(f.read())
            except Exception: pass

        last_deployed = {}
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    last_deployed = Toml.parse_toml(f.read())
            except Exception: pass

        if last_deployed:
            diff, deleted_keys = Config.dict_diff_with_deletions(last_deployed, active)
        else:
            diff = {}
            deleted_keys = []

        if allowed_keys:
            diff = {k: v for k, v in diff.items() if k in allowed_keys}
            deleted_keys = [k for k in deleted_keys if k.split('.')[0] in allowed_keys]

        if diff or deleted_keys:
            LOCAL_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
            existing = {}
            if local_path.exists():
                try:
                    with open(local_path) as f: existing = Toml.parse_toml(f.read())
                except: pass
            merged = Config.deep_merge(existing, diff)
            if deleted_keys:
                merged["_deleted_keys"] = list(set(merged.get("_deleted_keys", []) + deleted_keys))
            with open(local_path, "w") as f:
                f.write(Toml.dict_to_toml(merged))
                f.write("\n")
            print(f"📥 Sync: Updated local overrides in {local_path}")

        if local_path.exists():
            try:
                with open(local_path) as f:
                    override = Toml.parse_toml(f.read())
                deleted = override.pop("_deleted_keys", [])
                generated_data = Config.deep_merge(generated_data, override)
                for dk in deleted:
                    parts = dk.split('.')
                    curr = generated_data
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            if isinstance(curr, dict) and part in curr:
                                del curr[part]
                        else:
                            if isinstance(curr, dict) and part in curr:
                                curr = curr[part]
                            else:
                                break
            except: pass

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            f.write(Toml.dict_to_toml(generated_data))
            f.write("\n")

        return generated_data
