from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


APP_NAME = "Any-API-Check"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_APP_DIR = PROJECT_ROOT / "dist" / APP_NAME
INSTALLER_SCRIPT = PROJECT_ROOT / "build" / "installer" / f"{APP_NAME}.iss"
INSTALLER_OUTPUT_DIR = PROJECT_ROOT / "dist_installer"


def find_iscc() -> str | None:
    env_candidate = os.environ.get("ISCC_EXE")
    candidates = [
        env_candidate,
        shutil.which("ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def run_command(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def ensure_dist(source_dir: Path, skip_build: bool) -> Path:
    if skip_build:
        if not source_dir.exists():
            raise FileNotFoundError(f"打包目录不存在: {source_dir}")
        return source_dir

    run_command([sys.executable, str(PROJECT_ROOT / "scripts" / "build_windows.py")])
    if not source_dir.exists():
        raise FileNotFoundError(f"打包目录不存在: {source_dir}")
    return source_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Windows installer with Inno Setup")
    parser.add_argument(
        "--version",
        default=datetime.now().strftime("%Y.%m.%d"),
        help="Installer display version, defaults to current date",
    )
    parser.add_argument(
        "--source-dir",
        default=str(DIST_APP_DIR),
        help="Directory containing the built onedir app",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip PyInstaller build and package existing source-dir directly",
    )
    return parser.parse_args()


def build() -> int:
    args = parse_args()
    source_dir = ensure_dist(Path(args.source_dir).resolve(), args.skip_build)
    exe_path = source_dir / f"{APP_NAME}.exe"
    if not exe_path.exists():
        raise FileNotFoundError(f"缺少主程序: {exe_path}")

    iscc = find_iscc()
    if not iscc:
        raise FileNotFoundError(
            "未找到 Inno Setup 编译器 ISCC.exe，请先安装 Inno Setup 6"
        )

    INSTALLER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        iscc,
        f"/DAppVersion={args.version}",
        f"/DSourceDir={source_dir}",
        f"/DOutputDir={INSTALLER_OUTPUT_DIR}",
        str(INSTALLER_SCRIPT),
    ]
    run_command(command)

    print(f"Installer output: {INSTALLER_OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
