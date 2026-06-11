import copy
import json
import re
import shutil
from pathlib import Path

from utils.toml import Toml
from utils.fs import Files

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_CONFIGS_DIR = BASE_DIR / "agent" / ".local_configs"
CACHE_DIR = BASE_DIR / "agent" / ".cache" / "last_deployed"


class Config:
    @staticmethod
    def deep_merge(base: dict, overlay: dict) -> dict:
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
    def dict_diff_with_deletions(base: dict, active: dict, prefix: str = "") -> tuple[dict, list[str]]:
        """Recursively compute additions/modifications and deleted key paths."""
        diff: dict = {}
        deleted: list[str] = []

        for k, v in active.items():
            current_path = f"{prefix}{k}"
            if k not in base:
                diff[k] = copy.deepcopy(v)
            elif isinstance(v, dict) and isinstance(base[k], dict):
                sub_diff, sub_del = Config.dict_diff_with_deletions(base[k], v, current_path + ".")
                if sub_diff:
                    diff[k] = sub_diff
                deleted.extend(sub_del)
            elif v != base[k]:
                diff[k] = copy.deepcopy(v)

        for k in base:
            if k not in active:
                deleted.append(f"{prefix}{k}")

        return diff, deleted

    @staticmethod
    def merge_json_file(path: str | Path, new_data: dict, overwrite_keys: list[str] | None = None):
        """
        Reads an existing JSON file, deep-merges new_data into it (overlay wins),
        then hard-replaces top-level keys listed in overwrite_keys with pristine
        copies of the original new_data values.
        """
        p = Path(path)
        if p.is_symlink():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p)

        overwrite_snapshot = {
            key: copy.deepcopy(new_data[key])
            for key in (overwrite_keys or [])
            if key in new_data
        }

        existing: dict = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        existing = loaded
            except Exception:
                pass

        merged = Config.deep_merge(existing, new_data)
        merged.update(overwrite_snapshot)

        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            json.dump(merged, f, indent=2)
            f.write("\n")

    @staticmethod
    def merge_toml_file(path: str | Path, new_data: dict, overwrite_keys: list[str] | None = None):
        """
        Reads an existing TOML file, deep-merges new_data into it,
        then hard-replaces overwrite_keys with pristine new_data values.
        """
        p = Path(path)
        if p.is_symlink():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p)

        overwrite_snapshot = {
            key: copy.deepcopy(new_data[key])
            for key in (overwrite_keys or [])
            if key in new_data
        }

        existing: dict = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    existing = Toml.parse_toml(f.read())
            except Exception:
                pass

        merged = Config.deep_merge(existing, new_data)
        merged.update(overwrite_snapshot)

        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            f.write(Toml.dict_to_toml(merged))
            f.write("\n")

    @staticmethod
    def backup(backup_dir: str | Path, file_paths: list[str | Path]) -> list[str]:
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
                p_backup.mkdir(parents=True, exist_ok=True)
                Files.safe_copy_file(p_src, p_backup / p_src.name)
                backed_up.append(p_src.name)
        return backed_up


class PullEngine:
    @staticmethod
    def _apply_local_overrides(generated_data: dict, local_path: Path, load_fn) -> dict:
        """Apply local override file onto generated_data, respecting _deleted_keys."""
        if not local_path.exists():
            return generated_data
        try:
            with open(local_path) as f:
                override = load_fn(f)
            deleted = override.pop("_deleted_keys", [])
            generated_data = Config.deep_merge(generated_data, override)
            for dk in deleted:
                parts = dk.split(".")
                curr = generated_data
                for i, part in enumerate(parts):
                    if not isinstance(curr, dict) or part not in curr:
                        break
                    if i == len(parts) - 1:
                        del curr[part]
                    else:
                        curr = curr[part]
        except Exception:
            pass
        return generated_data

    @staticmethod
    def handle_json(
        path: str | Path,
        generated_data: dict,
        local_filename: str,
        allowed_keys: list[str] | None = None,
    ) -> dict:
        if allowed_keys is None:
            allowed_keys = [k for k in generated_data if not k.startswith("$")]
        p = Path(path)
        local_path = LOCAL_CONFIGS_DIR / local_filename
        cache_path = CACHE_DIR / local_filename

        active: dict = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    active = json.loads(re.sub(r"(?<!:)\/\/.*", "", f.read()))
            except Exception:
                pass

        last_deployed: dict = {}
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    last_deployed = json.load(f)
            except Exception:
                pass

        if last_deployed:
            diff, deleted_keys = Config.dict_diff_with_deletions(last_deployed, active)
            diff = {k: v for k, v in diff.items() if k in allowed_keys}
            deleted_keys = [k for k in deleted_keys if k.split(".")[0] in allowed_keys]
        else:
            diff, deleted_keys = {}, []

        if diff or deleted_keys:
            LOCAL_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
            existing: dict = {}
            if local_path.exists():
                try:
                    with open(local_path) as f:
                        existing = json.load(f)
                except Exception:
                    pass
            merged = Config.deep_merge(existing, diff)
            if deleted_keys:
                merged["_deleted_keys"] = list(set(merged.get("_deleted_keys", []) + deleted_keys))
            with open(local_path, "w") as f:
                json.dump(merged, f, indent=2)
                f.write("\n")
            print(f"📥 Sync: Updated local overrides in {local_path}")

        generated_data = PullEngine._apply_local_overrides(
            generated_data, local_path, lambda f: json.load(f)
        )

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(generated_data, f, indent=2)
            f.write("\n")

        return generated_data

    @staticmethod
    def handle_toml(
        path: str | Path,
        generated_data: dict,
        local_filename: str,
        allowed_keys: list[str] | None = None,
    ) -> dict:
        if allowed_keys is None:
            allowed_keys = [k for k in generated_data if not k.startswith("$")]
        p = Path(path)
        local_path = LOCAL_CONFIGS_DIR / local_filename
        cache_path = CACHE_DIR / local_filename

        active: dict = {}
        if p.exists():
            try:
                with open(p, "r") as f:
                    active = Toml.parse_toml(f.read())
            except Exception:
                pass

        last_deployed: dict = {}
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    last_deployed = Toml.parse_toml(f.read())
            except Exception:
                pass

        if last_deployed:
            diff, deleted_keys = Config.dict_diff_with_deletions(last_deployed, active)
            diff = {k: v for k, v in diff.items() if k in allowed_keys}
            deleted_keys = [k for k in deleted_keys if k.split(".")[0] in allowed_keys]
        else:
            diff, deleted_keys = {}, []

        if diff or deleted_keys:
            LOCAL_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
            existing: dict = {}
            if local_path.exists():
                try:
                    with open(local_path) as f:
                        existing = Toml.parse_toml(f.read())
                except Exception:
                    pass
            merged = Config.deep_merge(existing, diff)
            if deleted_keys:
                merged["_deleted_keys"] = list(set(merged.get("_deleted_keys", []) + deleted_keys))
            with open(local_path, "w") as f:
                f.write(Toml.dict_to_toml(merged))
                f.write("\n")
            print(f"📥 Sync: Updated local overrides in {local_path}")

        generated_data = PullEngine._apply_local_overrides(
            generated_data, local_path, lambda f: Toml.parse_toml(f.read())
        )

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            f.write(Toml.dict_to_toml(generated_data))
            f.write("\n")

        return generated_data
