from pathlib import Path
from utils.config import Config, PullEngine
from utils.fs import Symlinks

class AgentDeployer:
    @staticmethod
    def setup_symlinks(target_dir: Path, central_skills: Path, central_hooks: Path, central_subagents: Path = None):
        target_dir.mkdir(parents=True, exist_ok=True)
        Symlinks.ensure(central_skills, target_dir / "skills")
        Symlinks.ensure(central_hooks, target_dir / "hooks")
        if central_subagents:
            # Different tools use different names for the subagents symlink, e.g. "agents" vs "subagents".
            # For simplicity, we just pass the correct target link name in the manifests.
            pass

    @staticmethod
    def deploy_json(path: Path, new_data: dict, local_filename: str, overwrite_keys: list[str]):
        generated = PullEngine.handle_json(path, new_data, local_filename)
        print(f"💾 Deploying JSON config to {path}...")
        Config.merge_json_file(path, generated, overwrite_keys=overwrite_keys)

    @staticmethod
    def deploy_toml(path: Path, new_data: dict, local_filename: str, overwrite_keys: list[str]):
        generated = PullEngine.handle_toml(path, new_data, local_filename)
        print(f"💾 Deploying TOML config to {path}...")
        Config.merge_toml_file(path, generated, overwrite_keys=overwrite_keys)
