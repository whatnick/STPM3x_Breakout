#!/usr/bin/env python3
"""Add STPM33 copper pours and production silkscreen markings."""

from __future__ import annotations

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM33_Breakout"
BOARD_PATH = PROJECT / "STPM33_Breakout.kicad_pcb"
LOGO_LIBRARY = PROJECT / "logos.pretty"

TEXT_SIZE = 0.8
TEXT_STROKE = 0.2


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def add_text(
    board: pcbnew.BOARD,
    text: str,
    x: float,
    y: float,
    layer: int,
    *,
    angle: float = 0,
    size: float = TEXT_SIZE,
) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(point(x, y))
    item.SetLayer(layer)
    item.SetTextAngleDegrees(angle)
    item.SetTextSize(point(size, size))
    item.SetTextThickness(mm(TEXT_STROKE))
    if layer == pcbnew.B_SilkS:
        item.SetMirrored(True)
    board.Add(item)


def remove_generated_items(board: pcbnew.BOARD) -> None:
    for drawing in list(board.GetDrawings()):
        if isinstance(drawing, pcbnew.PCB_TEXT) and drawing.GetLayer() in (
            pcbnew.F_SilkS,
            pcbnew.B_SilkS,
        ):
            board.Delete(drawing)
    for footprint in list(board.GetFootprints()):
        if footprint.GetReference().startswith("LOGO"):
            board.Delete(footprint)
    for zone in list(board.Zones()):
        board.Delete(zone)


def add_zone(board: pcbnew.BOARD, net_name: str, layer: int) -> None:
    net = board.FindNet(net_name)
    if net is None:
        raise RuntimeError(f"Missing zone net {net_name}")
    zone = pcbnew.ZONE(board)
    zone.SetNet(net)
    zone.SetLayer(layer)
    zone.SetLocalClearance(mm(0.20))
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in ((21.0, 21.0), (74.0, 21.0), (74.0, 59.0), (21.0, 59.0)):
        outline.Append(point(x, y))
    board.Add(zone)


def place_references(board: pcbnew.BOARD) -> None:
    positions = {
        "U1": (49.0, 32.8, 0),
        "J1": (72.5, 56.4, 90),
        "SW1": (71.8, 36.5, 90),
        "Y1": (42.0, 27.5, 0),
        "NT1": (61.8, 44.5, 90),
        "C1": (37.0, 27.8, 0),
        "C2": (37.0, 31.2, 0),
        "C3": (37.0, 35.3, 0),
        "C4": (37.0, 38.7, 0),
        "C5": (44.5, 41.8, 0),
        "C6": (44.5, 51.2, 0),
        "C9": (58.5, 30.5, 0),
        "C10": (59.5, 34.5, 0),
        "C11": (59.5, 39.0, 0),
        "C12": (47.0, 42.0, 0),
        "C13": (49.0, 23.8, 0),
        "C14": (49.0, 27.0, 0),
        "C15": (52.5, 42.0, 0),
    }
    for footprint in board.GetFootprints():
        reference = footprint.GetReference()
        field = footprint.Reference()
        if reference.startswith(("H", "LOGO", "TP")) or reference == "SJ1":
            field.SetVisible(False)
            continue
        x = pcbnew.ToMM(footprint.GetPosition().x)
        y = pcbnew.ToMM(footprint.GetPosition().y)
        x, y, angle = positions.get(reference, (x, y - 1.5, 0))
        front = footprint.GetLayer() == pcbnew.F_Cu
        field.SetLayer(pcbnew.F_SilkS if front else pcbnew.B_SilkS)
        field.SetVisible(True)
        field.SetTextSize(point(TEXT_SIZE, TEXT_SIZE))
        field.SetTextThickness(mm(TEXT_STROKE))
        field.SetTextAngleDegrees(angle)
        field.SetPosition(point(x, y))
        field.SetMirrored(not front)
        footprint.Value().SetVisible(False)


def add_logos(board: pcbnew.BOARD) -> None:
    loader = pcbnew.PCB_IO_KICAD_SEXPR()
    whatnick = loader.FootprintLoad(str(LOGO_LIBRARY), "Whatnick_Logo")
    oshw = loader.FootprintLoad(str(LOGO_LIBRARY), "OSHW_Logo")
    if whatnick is None or oshw is None:
        raise RuntimeError("Unable to load Whatnick/OSHW logos")
    whatnick.SetReference("LOGO_W")
    whatnick.SetPosition(point(68.0, 48.0))
    whatnick.SetExcludedFromBOM(True)
    whatnick.SetExcludedFromPosFiles(True)
    whatnick.Reference().SetVisible(False)
    whatnick.Value().SetVisible(False)
    board.Add(whatnick)
    oshw.SetReference("LOGO_OSHW")
    oshw.SetPosition(point(66.0, 51.0))
    oshw.SetExcludedFromBOM(True)
    oshw.SetExcludedFromPosFiles(True)
    oshw.Reference().SetVisible(False)
    oshw.Value().SetVisible(False)
    board.Add(oshw)
    oshw.Flip(point(66.0, 51.0), False)


def add_markings(board: pcbnew.BOARD) -> None:
    add_text(board, "STPM33 DUAL CURRENT", 58.0, 21.5, pcbnew.F_SilkS, size=1.0)
    add_text(board, "whatnick.com", 62.5, 23.4, pcbnew.F_SilkS)
    add_text(board, "CT1", 28.5, 32.4, pcbnew.F_SilkS)
    add_text(board, "CT2", 28.5, 39.9, pcbnew.F_SilkS)
    add_text(board, "9VAC", 28.5, 51.5, pcbnew.F_SilkS)
    add_text(board, "UART", 67.5, 33.0, pcbnew.B_SilkS)
    add_text(board, "SPI", 68.2, 28.5, pcbnew.B_SilkS, angle=90)
    add_text(board, "NOT FOR DIRECT MAINS", 47.5, 32.0, pcbnew.B_SilkS)
    add_text(board, "ISOLATED 9VAC + CT INPUTS ONLY", 47.5, 33.7, pcbnew.B_SilkS)
    add_text(board, "TAPR OHL 1.0", 30.0, 49.5, pcbnew.B_SilkS)
    add_text(board, "v1.0 2026-10-06", 42.0, 49.5, pcbnew.B_SilkS)
    header_labels = (
        "3V3",
        "GND",
        "VAC+",
        "VAC-",
        "CT1+",
        "CT1-",
        "CT2+",
        "CT2-",
        "SCS",
        "SCL",
        "MOSI",
        "MISO",
        "SYN",
        "EN",
    )
    for index, label in enumerate(header_labels):
        add_text(
            board,
            label,
            30.50 + index * 2.54,
            52.9,
            pcbnew.B_SilkS,
            angle=90,
        )
    for x, label in (
        (29.5, "INT1"),
        (35.0, "INT2"),
        (54.0, "LED1"),
        (59.5, "LED2"),
        (61.5, "CLK/ZCR"),
    ):
        add_text(board, label, x, 29.5, pcbnew.B_SilkS, angle=90)


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    remove_generated_items(board)
    add_zone(board, "GNDA", pcbnew.F_Cu)
    add_zone(board, "DGND", pcbnew.B_Cu)
    place_references(board)
    add_logos(board)
    add_markings(board)
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Finalized {BOARD_PATH}")


if __name__ == "__main__":
    main()
