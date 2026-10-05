#!/usr/bin/env python3
"""Render reproducible top and bottom STPM32 board images."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM32_Breakout"
BOARD = PROJECT / "STPM32_Breakout.kicad_pcb"
RENDERS = PROJECT / "renders"


def find_kicad_cli() -> str:
    executable = shutil.which("kicad-cli")
    if executable:
        return executable
    windows_path = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
    if windows_path.exists():
        return str(windows_path)
    raise RuntimeError("kicad-cli was not found")


def render(side: str, rotation: str) -> None:
    output = RENDERS / f"STPM32_Breakout_{side}.png"
    subprocess.run(
        (
            find_kicad_cli(),
            "pcb",
            "render",
            "--output",
            str(output),
            "--width",
            "1600",
            "--height",
            "1000",
            "--side",
            side,
            "--background",
            "opaque",
            "--quality",
            "high",
            "--floor",
            "--perspective",
            "--zoom",
            "1.05",
            "--rotate",
            rotation,
            str(BOARD),
        ),
        check=True,
    )


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    render("top", "25,0,-20")
    render("bottom", "25,0,20")


if __name__ == "__main__":
    main()
