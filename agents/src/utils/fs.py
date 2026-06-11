import json
import os
import shutil
from pathlib import Path

DEPLOYED_MANIFEST = ".deployed"

class Files:
    @staticmethod
    def write_text_file(path: str | Path, content: str):
        """
        Writes plain text to path, safely removing any pre-existing symlink or
        directory.
        """
        p = Path(path)
        if p.is_symlink():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    @staticmethod
    def safe_copy_file(src: str | Path, dst: str | Path):
        """Safely copies a file, removing any pre-existing symlink or file first."""
        p_dst = Path(dst)
        if p_dst.is_symlink() or p_dst.is_file():
            p_dst.unlink()
        elif p_dst.is_dir():
            shutil.rmtree(p_dst)

        p_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, p_dst)

    @staticmethod
    def load_deployed(directory: str | Path) -> set[str]:
        """Returns the set of filenames previously deployed into directory."""
        manifest_path = Path(directory) / DEPLOYED_MANIFEST
        if manifest_path.exists():
            try:
                with open(manifest_path, "r") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    @staticmethod
    def save_deployed(directory: str | Path, filenames: set[str]):
        """Persists the set of compiler-owned filenames for a directory."""
        p_dir = Path(directory)
        p_dir.mkdir(parents=True, exist_ok=True)
        with open(p_dir / DEPLOYED_MANIFEST, "w") as f:
            json.dump(sorted(filenames), f, indent=2)
            f.write("\n")

    @staticmethod
    def clean_compiler_owned(directory: str | Path):
        """
        Removes only files recorded in the .deployed manifest from a previous run,
        leaving any user-placed or npx-installed files untouched.
        """
        p_dir = Path(directory)
        if p_dir.is_symlink():
            raise RuntimeError(
                f"clean_compiler_owned called on a symlink: {p_dir}. "
                "Only call this on physical central directories (~/.agents/...)."
            )
        p_dir.mkdir(parents=True, exist_ok=True)

        for name in Files.load_deployed(p_dir):
            p = p_dir / name
            if p.is_symlink() or p.is_file():
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p)

class Symlinks:
    @staticmethod
    def ensure(target: str | Path, link_name: str | Path):
        """
        Ensures that a symlink at `link_name` points to `target`.
        """
        p_link = Path(link_name)
        p_target = Path(target)
        
        if p_link.is_symlink():
            existing_target = Path(os.readlink(p_link))
            if not existing_target.is_absolute():
                existing_target = p_link.parent.resolve() / existing_target
            if existing_target.resolve() == p_target.resolve():
                return
            p_link.unlink()
        elif p_link.exists():
            if p_link.is_dir():
                for item in p_link.iterdir():
                    dst_item = p_target / item.name
                    if not dst_item.exists():
                        if item.is_dir():
                            shutil.copytree(item, dst_item)
                        else:
                            shutil.copy2(item, dst_item)
                shutil.rmtree(p_link)
            else:
                print(f"⚠️  Warning: removing unexpected file at {p_link} to create symlink.")
                p_link.unlink()

        p_link.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(p_target, p_link)
        except OSError as exc:
            raise RuntimeError(
                f"Failed to create symlink {p_link} → {p_target}: {exc}"
            ) from exc
        print(f"🔗 Created symlink: {p_link} ➔ {p_target}")
