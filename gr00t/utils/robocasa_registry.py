from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path


def _load_module(module_name: str, file_path: Path):
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _find_workspace_root(start_file: Path) -> Path:
    for parent in [start_file.parent, *start_file.parents]:
        candidate = parent / "third_party" / "robocasa" / "robocasa" / "utils" / "dataset_registry.py"
        if candidate.exists():
            return parent
    raise FileNotFoundError("Could not find robofab_robocasa workspace root")


def _ensure_lightweight_robocasa_package(workspace_root: Path) -> None:
    robocasa_pkg_path = workspace_root / "third_party" / "robocasa" / "robocasa"
    utils_pkg_path = robocasa_pkg_path / "utils"

    if "robocasa" not in sys.modules:
        robocasa_pkg = types.ModuleType("robocasa")
        robocasa_pkg.__path__ = [str(robocasa_pkg_path)]
        sys.modules["robocasa"] = robocasa_pkg

    if "robocasa.utils" not in sys.modules:
        utils_pkg = types.ModuleType("robocasa.utils")
        utils_pkg.__path__ = [str(utils_pkg_path)]
        sys.modules["robocasa.utils"] = utils_pkg

    if "robocasa.macros" not in sys.modules:
        macros_mod = types.ModuleType("robocasa.macros")
        macros_mod.DATASET_BASE_PATH = os.environ.get("ROBOCASA_DATASET_BASE_PATH")
        sys.modules["robocasa.macros"] = macros_mod


def load_dataset_registry_module():
    try:
        from robocasa.utils import dataset_registry as dataset_registry  # type: ignore

        return dataset_registry
    except Exception:
        workspace_root = _find_workspace_root(Path(__file__).resolve())
        _ensure_lightweight_robocasa_package(workspace_root)

        utils_dir = workspace_root / "third_party" / "robocasa" / "robocasa" / "utils"
        _load_module("robocasa.utils.dataset_registry_utils", utils_dir / "dataset_registry_utils.py")
        dataset_registry = _load_module("robocasa.utils.dataset_registry", utils_dir / "dataset_registry.py")
        return dataset_registry

