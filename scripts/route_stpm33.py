#!/usr/bin/env python3
"""Route the placed STPM33 board with Freerouting and import the session."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM33_Breakout"
BOARD_PATH = PROJECT / "STPM33_Breakout.kicad_pcb"
DSN_PATH = PROJECT / "STPM33_Breakout.dsn"
SES_PATH = PROJECT / "STPM33_Breakout.ses"


def find_java() -> str:
    configured = os.environ.get("JAVA25")
    if configured and Path(configured).exists():
        return configured
    executable = shutil.which("java")
    if executable:
        version = subprocess.run(
            (executable, "-version"), capture_output=True, text=True
        ).stderr
        if version.startswith('openjdk version "25'):
            return executable
    for root in (Path(r"C:\Program Files\Eclipse Adoptium"),):
        matches = sorted(root.glob("jre-25*/bin/java.exe"))
        if matches:
            return str(matches[-1])
    raise RuntimeError("Java 25 was not found; set JAVA25 to java.exe")


def find_freerouting_jar() -> str:
    configured = os.environ.get("FREEROUTING_JAR")
    if configured and Path(configured).exists():
        return configured
    raise RuntimeError(
        "Set FREEROUTING_JAR to a Freerouting 2.4+ executable JAR"
    )


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    pcbnew.ExportSpecctraDSN(board, str(DSN_PATH))
    subprocess.run(
        (
            find_java(),
            "-jar",
            find_freerouting_jar(),
            "-de",
            str(DSN_PATH),
            "-do",
            str(SES_PATH),
            "-mp",
            "100",
            "-mt",
            "1",
            "-us",
            "Hybrid",
            "-hr",
            "1:2",
            "-is",
            "prioritized",
        ),
        check=True,
    )
    if not pcbnew.ImportSpecctraSES(board, str(SES_PATH)):
        raise RuntimeError(f"Unable to import {SES_PATH}")
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Routed {BOARD_PATH}")


if __name__ == "__main__":
    main()
