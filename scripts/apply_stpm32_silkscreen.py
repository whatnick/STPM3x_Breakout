#!/usr/bin/env python3
"""Apply production silkscreen markings to the compact STPM32 breakout."""

from __future__ import annotations

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM32_Breakout"
BOARD_PATH = PROJECT / "STPM32_Breakout.kicad_pcb"
LOGO_LIBRARY = PROJECT / "logos.pretty"

TEXT_SIZE = 0.8
TEXT_STROKE = 0.2


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


REFERENCE_POSITIONS: dict[str, tuple[float, float, float]] = {
    "C13": (40.50, 21.85, 0),
    "C11": (44.70, 24.30, 0),
    "Y1": (36.80, 21.85, 0),
    "C14": (39.10, 29.20, 0),
    "C9": (50.80, 27.20, 0),
    "U1": (44.00, 27.65, 0),
    "C10": (51.10, 32.80, 0),
    "R10": (35.20, 31.25, 0),
    "C4": (38.20, 30.85, 0),
    "R8": (29.90, 32.75, 0),
    "SW1": (56.70, 34.20, 90),
    "C12": (47.40, 36.05, 0),
    "NT1": (50.10, 36.90, 0),
    "C3": (36.30, 34.20, 0),
    "C1": (40.50, 38.00, 0),
    "C2": (43.70, 36.30, 0),
    "R5": (27.20, 35.10, 0),
    "R9": (34.90, 35.10, 0),
    "R11": (50.30, 39.55, 0),
    "R4": (28.45, 38.65, 90),
    "R7": (31.25, 38.65, 90),
    "R1": (34.95, 39.25, 90),
    "R2": (39.75, 39.25, 90),
    "R12": (44.80, 42.35, 0),
    "R3": (28.45, 41.65, 90),
    "R6": (31.25, 41.65, 90),
    "RB1": (39.10, 42.40, 0),
    "J1": (56.50, 46.70, 0),
    "TP1": (22.60, 25.10, 0),
    "TP2": (26.20, 25.10, 0),
    "TP3": (29.80, 25.10, 0),
    "TP4": (33.40, 25.10, 0),
}


HEADER_LABELS = (
    (25.00, "3V3"),
    (27.54, "GND"),
    (30.08, "VAC+"),
    (32.62, "VAC-"),
    (35.16, "CT+"),
    (37.70, "CT-"),
    (40.24, "SCS"),
    (42.78, "SCL"),
    (45.32, "MOSI"),
    (47.86, "MISO"),
    (50.40, "SYN"),
    (52.94, "EN"),
)


def add_text(
    board: pcbnew.BOARD,
    text: str,
    x: float,
    y: float,
    layer: int,
    *,
    angle: float = 0,
    size: float = TEXT_SIZE,
    stroke: float = TEXT_STROKE,
) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(point(x, y))
    item.SetLayer(layer)
    item.SetTextAngleDegrees(angle)
    item.SetTextSize(point(size, size))
    item.SetTextThickness(mm(stroke))
    if layer == pcbnew.B_SilkS:
        item.SetMirrored(True)
    board.Add(item)


def remove_old_markings(board: pcbnew.BOARD) -> None:
    for drawing in list(board.GetDrawings()):
        if isinstance(drawing, pcbnew.PCB_TEXT) and drawing.GetLayer() in (
            pcbnew.F_SilkS,
            pcbnew.B_SilkS,
        ):
            board.Delete(drawing)
    for footprint in list(board.GetFootprints()):
        if footprint.GetReference().startswith("LOGO"):
            board.Delete(footprint)


def place_references(board: pcbnew.BOARD) -> None:
    for footprint in board.GetFootprints():
        reference = footprint.GetReference()
        if reference.startswith("LOGO"):
            continue
        if reference not in REFERENCE_POSITIONS:
            raise RuntimeError(f"No silkscreen position defined for {reference}")
        x, y, angle = REFERENCE_POSITIONS[reference]
        field = footprint.Reference()
        front = footprint.GetLayer() == pcbnew.F_Cu
        field.SetLayer(pcbnew.F_SilkS if front else pcbnew.B_SilkS)
        field.SetVisible(True)
        field.SetTextSize(point(TEXT_SIZE, TEXT_SIZE))
        field.SetTextThickness(mm(TEXT_STROKE))
        field.SetTextAngleDegrees(angle)
        field.SetPosition(point(x, y))
        field.SetMirrored(not front)
        footprint.Value().SetLayer(pcbnew.F_Fab if front else pcbnew.B_Fab)
        footprint.Value().SetVisible(False)


def add_logos(board: pcbnew.BOARD) -> None:
    loader = pcbnew.PCB_IO_KICAD_SEXPR()
    whatnick = loader.FootprintLoad(str(LOGO_LIBRARY), "Whatnick_Logo")
    oshw = loader.FootprintLoad(str(LOGO_LIBRARY), "OSHW_Logo")
    if whatnick is None or oshw is None:
        raise RuntimeError("Unable to load project-local logo footprints")

    whatnick.SetReference("LOGO_W")
    whatnick.SetPosition(point(23.70, 25.00))
    whatnick.Reference().SetVisible(False)
    whatnick.Value().SetVisible(False)
    board.Add(whatnick)

    oshw.SetReference("LOGO_OSHW")
    oshw.SetPosition(point(54.40, 25.00))
    oshw.Reference().SetVisible(False)
    oshw.Value().SetVisible(False)
    board.Add(oshw)
    oshw.Flip(point(54.40, 25.00), False)


def add_board_markings(board: pcbnew.BOARD) -> None:
    add_text(board, "STPM32 ENERGY", 49.50, 21.55, pcbnew.F_SilkS, size=1.0)
    add_text(board, "whatnick.com", 53.00, 23.50, pcbnew.F_SilkS)

    add_text(board, "TAPR OHL 1.0", 25.20, 31.00, pcbnew.B_SilkS)
    add_text(board, "NOT FOR DIRECT MAINS", 42.00, 21.20, pcbnew.B_SilkS)
    add_text(board, "9VAC + CT ONLY", 28.20, 46.75, pcbnew.B_SilkS)
    add_text(board, "v1.0 2026-10-05", 48.20, 46.75, pcbnew.B_SilkS)

    for x, label in HEADER_LABELS:
        add_text(board, label, x, 41.75, pcbnew.B_SilkS, angle=90)

    for x, label in (
        (22.60, "INT1"),
        (26.20, "LED1"),
        (29.80, "LED2"),
        (33.40, "CLK/ZCR"),
    ):
        add_text(board, label, x, 29.00, pcbnew.B_SilkS, angle=90)


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    remove_old_markings(board)
    place_references(board)
    add_logos(board)
    add_board_markings(board)
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Updated {BOARD_PATH}")


if __name__ == "__main__":
    main()
