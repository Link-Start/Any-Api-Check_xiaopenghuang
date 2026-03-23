from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "Any-API-Check"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"
WORK_DIR = PROJECT_ROOT / "build" / "pyinstaller"
SPEC_DIR = PROJECT_ROOT / "build" / "spec"
APP_DIST_DIR = DIST_DIR / APP_NAME
RUNTIME_ROOT = Path(os.environ.get("LOCALAPPDATA", str(DIST_DIR))) / APP_NAME

DATA_DIRS: list[tuple[Path, str]] = [
    (PROJECT_ROOT / "relay_console" / "web", "relay_console/web"),
    (PROJECT_ROOT / "config" / "templates", "config/templates"),
    (PROJECT_ROOT / "config" / "presets", "config/presets"),
]


def run_command(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def ensure_pyinstaller() -> None:
    if importlib.util.find_spec("PyInstaller") is not None:
        return
    run_command([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0"])


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def move_if_missing(source: Path, target: Path) -> None:
    if not source.exists() or target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))


def preserve_legacy_runtime_data() -> None:
    if not APP_DIST_DIR.exists():
        return

    legacy_config_dir = APP_DIST_DIR / "config"
    runtime_config_dir = RUNTIME_ROOT / "config"
    move_if_missing(legacy_config_dir / "app.db", runtime_config_dir / "app.db")
    move_if_missing(legacy_config_dir / "app.db-shm", runtime_config_dir / "app.db-shm")
    move_if_missing(legacy_config_dir / "app.db-wal", runtime_config_dir / "app.db-wal")
    move_if_missing(legacy_config_dir / "browser_profiles", runtime_config_dir / "browser_profiles")
    move_if_missing(
        legacy_config_dir / "presets" / "api_presets.json",
        runtime_config_dir / "presets" / "api_presets.json",
    )
    move_if_missing(APP_DIST_DIR / "debug", RUNTIME_ROOT / "debug")


def build() -> int:
    ensure_pyinstaller()

    from PyInstaller.__main__ import run as pyinstaller_run

    preserve_legacy_runtime_data()
    remove_path(APP_DIST_DIR)
    remove_path(WORK_DIR)
    remove_path(SPEC_DIR)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.parent.mkdir(parents=True, exist_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    pyinstaller_args: list[str] = [
        str(PROJECT_ROOT / "app.py"),
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--name",
        APP_NAME,
        "--contents-directory",
        ".",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(WORK_DIR),
        "--specpath",
        str(SPEC_DIR),
        "--paths",
        str(PROJECT_ROOT),
        "--collect-data",
        "webview",
        "--collect-submodules",
        "relay_console",
        "--hidden-import",
        "webview.platforms.winforms",
        "--hidden-import",
        "webview.platforms.edgechromium",
        "--exclude-module",
        "webview.platforms.qt",
        "--exclude-module",
        "qtpy",
        "--exclude-module",
        "PyQt5",
        "--noupx",
        "--icon",
        str(PROJECT_ROOT / "relay_console" / "web" / "icon.ico"),
    ]

    for source_dir, target_dir in DATA_DIRS:
        pyinstaller_args.extend(["--add-data", f"{source_dir}:{target_dir}"])

    print(f"Building {APP_NAME}...")
    pyinstaller_run(pyinstaller_args)

    print(f"Build completed: {APP_DIST_DIR}")
    print(f"Executable: {APP_DIST_DIR / (APP_NAME + '.exe')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
