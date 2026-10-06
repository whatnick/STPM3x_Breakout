#!/usr/bin/env python3
"""Validate and generate the STPM33 KiCad 10 fabrication package."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM33_Breakout"
SCHEMATIC = PROJECT / "STPM33_Breakout.kicad_sch"
BOARD = PROJECT / "STPM33_Breakout.kicad_pcb"
OUTPUT = PROJECT / "gerber"
ARCHIVE = OUTPUT / "STPM33_Breakout_Gerbers.zip"

LAYERS = (
    "F.Cu",
    "B.Cu",
    "F.Paste",
    "F.Silkscreen",
    "B.Silkscreen",
    "F.Mask",
    "B.Mask",
    "Edge.Cuts",
)


def find_kicad_cli() -> str:
    executable = shutil.which("kicad-cli")
    if executable:
        return executable
    path = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
    if path.exists():
        return str(path)
    raise RuntimeError("KiCad 10 kicad-cli was not found")


def run(*arguments: str) -> None:
    subprocess.run(arguments, check=True)


def main() -> None:
    cli = find_kicad_cli()
    version = subprocess.run(
        (cli, "--version"), check=True, capture_output=True, text=True
    ).stdout.strip()
    if not version.startswith("10."):
        raise RuntimeError(f"KiCad 10 is required; found {version}")
    with tempfile.TemporaryDirectory(prefix="stpm33-fab-") as temporary:
        run(
            cli,
            "sch",
            "erc",
            "--exit-code-violations",
            "-o",
            str(Path(temporary) / "erc.rpt"),
            str(SCHEMATIC),
        )
        run(
            cli,
            "pcb",
            "drc",
            "--exit-code-violations",
            "-o",
            str(Path(temporary) / "drc.rpt"),
            str(BOARD),
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.iterdir():
        if path.is_file():
            path.unlink()
    run(
        cli,
        "pcb",
        "export",
        "gerbers",
        "--output",
        str(OUTPUT),
        "--layers",
        ",".join(LAYERS),
        "--subtract-soldermask",
        "--no-protel-ext",
        "--check-zones",
        str(BOARD),
    )
    run(
        cli,
        "pcb",
        "export",
        "drill",
        "--output",
        str(OUTPUT),
        "--format",
        "excellon",
        "--excellon-units",
        "mm",
        "--excellon-zeros-format",
        "decimal",
        "--excellon-separate-th",
        str(BOARD),
    )
    for side, name in (
        ("front", "STPM33_Breakout-Front_Pos.csv"),
        ("back", "STPM33_Breakout-Back_Pos.csv"),
    ):
        run(
            cli,
            "pcb",
            "export",
            "pos",
            "--output",
            str(OUTPUT / name),
            "--side",
            side,
            "--format",
            "csv",
            "--units",
            "mm",
            "--exclude-dnp",
            str(BOARD),
        )
    files = sorted(path for path in OUTPUT.iterdir() if path.is_file())
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.name)
    print(f"Wrote {len(files)} fabrication files and {ARCHIVE}")


if __name__ == "__main__":
    main()
