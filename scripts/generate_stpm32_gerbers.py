#!/usr/bin/env python3
"""Validate and generate the STPM32 KiCad 10 fabrication package."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM32_Breakout"
SCHEMATIC = PROJECT / "STPM32_Breakout.kicad_sch"
BOARD = PROJECT / "STPM32_Breakout.kicad_pcb"
OUTPUT = PROJECT / "gerber"
ARCHIVE = OUTPUT / "STPM32_Breakout_Gerbers.zip"

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

REQUIRED_SUFFIXES = (
    "-F_Cu.gbr",
    "-B_Cu.gbr",
    "-F_Paste.gbr",
    "-F_Silkscreen.gbr",
    "-B_Silkscreen.gbr",
    "-F_Mask.gbr",
    "-B_Mask.gbr",
    "-Edge_Cuts.gbr",
    "-PTH.drl",
    "-NPTH.drl",
    "-job.gbrjob",
)


def find_kicad_cli() -> str:
    executable = shutil.which("kicad-cli")
    if executable:
        return executable
    windows_path = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
    if windows_path.exists():
        return str(windows_path)
    raise RuntimeError("KiCad 10 kicad-cli was not found")


def run(*arguments: str) -> None:
    subprocess.run(arguments, check=True)


def validate(kicad_cli: str) -> None:
    version = subprocess.run(
        (kicad_cli, "--version"),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not version.startswith("10."):
        raise RuntimeError(f"KiCad 10 is required; found {version}")

    with tempfile.TemporaryDirectory(prefix="stpm32-fab-") as temporary:
        report_dir = Path(temporary)
        run(
            kicad_cli,
            "sch",
            "erc",
            "--exit-code-violations",
            "-o",
            str(report_dir / "erc.rpt"),
            str(SCHEMATIC),
        )
        run(
            kicad_cli,
            "pcb",
            "drc",
            "--exit-code-violations",
            "-o",
            str(report_dir / "drc.rpt"),
            str(BOARD),
        )


def clear_outputs() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT.iterdir():
        if path.is_file():
            path.unlink()


def export(kicad_cli: str) -> None:
    run(
        kicad_cli,
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
        kicad_cli,
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


def verify_outputs() -> list[Path]:
    files = sorted(path for path in OUTPUT.iterdir() if path.is_file())
    names = {path.name for path in files}
    missing = [
        suffix
        for suffix in REQUIRED_SUFFIXES
        if not any(name.endswith(suffix) for name in names)
    ]
    if missing:
        raise RuntimeError(f"Missing fabrication outputs: {', '.join(missing)}")
    return files


def create_archive(files: list[Path]) -> None:
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.name)


def main() -> None:
    kicad_cli = find_kicad_cli()
    validate(kicad_cli)
    clear_outputs()
    export(kicad_cli)
    files = verify_outputs()
    create_archive(files)
    print(f"Wrote {len(files)} fabrication files to {OUTPUT}")
    print(f"Wrote {ARCHIVE}")


if __name__ == "__main__":
    main()
