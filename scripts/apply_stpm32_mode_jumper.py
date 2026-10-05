#!/usr/bin/env python3
"""Add and route the rear-side STPM32 SPI/UART bias selector."""

from __future__ import annotations

from pathlib import Path

import pcbnew
from sexpdata import Symbol, loads


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM32_Breakout"
BOARD_PATH = PROJECT / "STPM32_Breakout.kicad_pcb"
NETLIST_PATH = PROJECT / "STPM32_Breakout.net"
KICAD_FOOTPRINTS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def atom(item: object) -> str:
    return item.value() if isinstance(item, Symbol) else str(item)


def schematic_uuid(reference: str) -> str:
    data = loads(NETLIST_PATH.read_text(encoding="utf-8"))
    for section in data[1:]:
        if not isinstance(section, list) or not section:
            continue
        if not isinstance(section[0], Symbol) or section[0].value() != "components":
            continue
        for component in section[1:]:
            if not isinstance(component, list) or not component:
                continue
            fields = {
                entry[0].value(): entry[1]
                for entry in component[1:]
                if isinstance(entry, list)
                and len(entry) > 1
                and isinstance(entry[0], Symbol)
            }
            if atom(fields.get("ref", "")) == reference:
                return atom(fields["tstamps"])
    raise RuntimeError(f"Missing {reference} in {NETLIST_PATH}")


def ensure_net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    net = board.FindNet(name)
    if net is not None:
        return net
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def same_point(vector: pcbnew.VECTOR2I, x: float, y: float) -> bool:
    return vector == point(x, y)


def remove_old_ground_tap(board: pcbnew.BOARD) -> None:
    endpoints = {
        (27.5400, 45.3000, 28.6769, 46.4369),
        (28.6769, 46.4369, 40.7210, 46.4369),
        (40.7210, 46.4369, 41.5100, 45.6479),
        (41.5100, 45.6479, 41.5100, 44.9089),
        (41.5100, 44.9089, 45.4189, 41.0),
        (45.4189, 41.0, 45.6250, 41.0),
        (45.6250, 41.0, 47.8353, 41.0),
        (47.8353, 41.0, 50.3000, 38.5353),
        (50.3000, 38.5353, 50.3000, 37.3608),
        (50.3000, 37.3608, 51.0757, 36.5851),
        (51.0757, 36.5851, 51.0757, 35.0757),
        (51.0757, 35.0757, 50.1000, 34.1000),
    }
    for track in list(board.GetTracks()):
        if isinstance(track, pcbnew.PCB_VIA) or track.GetNetname() != "DGND":
            continue
        for x1, y1, x2, y2 in endpoints:
            forward = same_point(track.GetStart(), x1, y1) and same_point(
                track.GetEnd(), x2, y2
            )
            reverse = same_point(track.GetStart(), x2, y2) and same_point(
                track.GetEnd(), x1, y1
            )
            if forward or reverse:
                board.Delete(track)
                break


def add_track(
    board: pcbnew.BOARD,
    net: pcbnew.NETINFO_ITEM,
    start: tuple[float, float],
    end: tuple[float, float],
    layer: int,
    width: float = 0.20,
) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(net)
    track.SetStart(point(*start))
    track.SetEnd(point(*end))
    track.SetLayer(layer)
    track.SetWidth(mm(width))
    board.Add(track)


def add_via(
    board: pcbnew.BOARD,
    net: pcbnew.NETINFO_ITEM,
    position: tuple[float, float],
) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetNet(net)
    via.SetPosition(point(*position))
    via.SetWidth(mm(0.60))
    via.SetDrill(mm(0.30))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(via)


def remove_previous_selector(board: pcbnew.BOARD) -> None:
    footprint = board.FindFootprintByReference("SJ1")
    if footprint is not None:
        board.Delete(footprint)
    selector_tracks = {
        ("DGND", 54.5000, 26.3000, 54.0000, 28.0000),
        ("DGND", 54.0000, 28.0000, 54.2000, 30.3000),
        ("+3V3", 54.5000, 23.7000, 52.5000, 23.7000),
        ("+3V3", 52.5000, 23.7000, 52.5000, 28.8000),
        ("+3V3", 52.5000, 28.8000, 48.8514, 29.9399),
    }
    for track in list(board.GetTracks()):
        if track.GetNetname() == "MODE_BIAS":
            board.Delete(track)
            continue
        if isinstance(track, pcbnew.PCB_VIA):
            if track.GetNetname() == "DGND" and same_point(
                track.GetPosition(), 54.00, 28.00
            ):
                board.Delete(track)
            continue
        for net, x1, y1, x2, y2 in selector_tracks:
            if track.GetNetname() != net:
                continue
            forward = same_point(track.GetStart(), x1, y1) and same_point(
                track.GetEnd(), x2, y2
            )
            reverse = same_point(track.GetStart(), x2, y2) and same_point(
                track.GetEnd(), x1, y1
            )
            if forward or reverse:
                board.Delete(track)
                break


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    board.GetTitleBlock().SetRevision("B")
    remove_previous_selector(board)
    remove_old_ground_tap(board)

    dgnd = board.FindNet("DGND")
    power = board.FindNet("+3V3")
    mode_bias = ensure_net(board, "MODE_BIAS")
    if dgnd is None or power is None:
        raise RuntimeError("Missing required DGND or +3V3 net")

    r12 = board.FindFootprintByReference("R12")
    if r12 is None:
        raise RuntimeError("Missing R12")
    r12.FindPadByNumber("2").SetNet(mode_bias)

    footprint = pcbnew.FootprintLoad(
        str(KICAD_FOOTPRINTS / "Jumper.pretty"),
        "SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm",
    )
    if footprint is None:
        raise RuntimeError("Unable to load the three-pad solder jumper")
    footprint.SetReference("SJ1")
    footprint.SetValue("SPI / UART")
    footprint.SetPath(pcbnew.KIID_PATH(f"/{schematic_uuid('SJ1')}"))
    footprint.SetPosition(point(54.50, 25.00))
    footprint.SetOrientationDegrees(90)
    footprint.SetExcludedFromBOM(True)
    footprint.SetExcludedFromPosFiles(True)
    footprint.Reference().SetVisible(False)
    footprint.Value().SetVisible(False)
    board.Add(footprint)
    footprint.Flip(point(54.50, 25.00), False)
    footprint.FindPadByNumber("1").SetNet(dgnd)
    footprint.FindPadByNumber("2").SetNet(mode_bias)
    footprint.FindPadByNumber("3").SetNet(power)

    # Pad 1 is tied to the reset-switch ground pad. The default pad 1-2 copper
    # bridge therefore pulls MODE_BIAS low for SPI.
    pad1 = footprint.FindPadByNumber("1").GetPosition()
    pad1_xy = (pcbnew.ToMM(pad1.x), pcbnew.ToMM(pad1.y))
    add_track(board, dgnd, pad1_xy, (54.00, 28.00), pcbnew.B_Cu)
    add_via(board, dgnd, (54.00, 28.00))
    add_track(board, dgnd, (54.00, 28.00), (54.20, 30.30), pcbnew.F_Cu)

    # Pad 2: isolated bias node to R12, leaving SCS free for SPI chip select.
    pad2 = footprint.FindPadByNumber("2").GetPosition()
    pad2_xy = (pcbnew.ToMM(pad2.x), pcbnew.ToMM(pad2.y))
    add_track(board, mode_bias, pad2_xy, (56.00, 25.00), pcbnew.B_Cu)
    add_track(board, mode_bias, (56.00, 25.00), (56.00, 41.80), pcbnew.B_Cu)
    add_track(board, mode_bias, (56.00, 41.80), (53.50, 42.60), pcbnew.B_Cu)
    add_via(board, mode_bias, (53.50, 42.60))
    add_track(board, mode_bias, (53.50, 42.60), (48.00, 42.60), pcbnew.F_Cu)
    add_track(board, mode_bias, (48.00, 42.60), (45.625, 41.00), pcbnew.F_Cu)

    # Pad 3: UART bias option to the nearby existing +3V3 via.
    pad3 = footprint.FindPadByNumber("3").GetPosition()
    pad3_xy = (pcbnew.ToMM(pad3.x), pcbnew.ToMM(pad3.y))
    add_track(board, power, pad3_xy, (52.50, 23.70), pcbnew.B_Cu)
    add_track(board, power, (52.50, 23.70), (52.50, 28.80), pcbnew.B_Cu)
    add_track(board, power, (52.50, 28.80), (48.8514, 29.9399), pcbnew.B_Cu)

    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Updated {BOARD_PATH}")


if __name__ == "__main__":
    main()
