"""Arma KovuRun.exe con PyInstaller (carpeta dist/KovuRun).

    py -m pip install pyinstaller
    py tools/build.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "KovuRun"
NAME = "KovuRun"


def main() -> int:
    assets = ROOT / "assets"
    if not assets.is_dir():
        print("Falta assets/", file=sys.stderr)
        return 1
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        NAME,
        "--distpath",
        str(ROOT / "dist"),
        "--workpath",
        str(ROOT / "build"),
        "--specpath",
        str(ROOT / "build"),
        "--add-data",
        f"{assets}{os.pathsep}assets",
        str(ROOT / "main.py"),
    ]
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode
    # onedir deja el exe en dist/KovuRun/; copiamos assets al lado por si el empaquetado falla
    target = DIST / "assets"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(assets, target)
    print(f"Listo: {DIST / (NAME + '.exe')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
