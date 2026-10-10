#!/usr/bin/env python3
"""Build the placed STPM34 breakout PCB from its exported netlist."""

from __future__ import annotations

import math
from pathlib import Path

import pcbnew
from sexpdata import Symbol, loads


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM34_Breakout"
NETLIST = PROJECT / "STPM34_Breakout.net"
OUTPUT = PROJECT / "STPM34_Breakout.kicad_pcb"
KICAD_FOOTPRINTS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
STPM34_MODEL = "${KIPRJMOD}/models/step/QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm.step"

LEFT, TOP, RIGHT, BOTTOM, RADIUS = 20.0, 20.0, 95.0, 70.0, 5.08


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def tag(item: object) -> str | None:
    if isinstance(item, list) and item and isinstance(item[0], Symbol):
        return item[0].value()
    return None


def atom(item: object) -> str:
    return item.value() if isinstance(item, Symbol) else str(item)


def read_netlist() -> tuple[dict[str, dict[str, str]], list[tuple[str, list[tuple[str, str]]]]]:
    data = loads(NETLIST.read_text(encoding="utf-8"))
    components: dict[str, dict[str, str]] = {}
    nets: list[tuple[str, list[tuple[str, str]]]] = []
    for section in data[1:]:
        if tag(section) == "components":
            for component in section[1:]:
                if tag(component) != "comp":
                    continue
                fields = {
                    tag(entry): entry[1]
                    for entry in component[1:]
                    if isinstance(entry, list) and len(entry) > 1
                }
                reference = atom(fields["ref"])
                components[reference] = {
                    "value": atom(fields["value"]),
                    "footprint": atom(fields["footprint"]),
                    "uuid": atom(fields["tstamps"]),
                }
        elif tag(section) == "nets":
            for net in section[1:]:
                if tag(net) != "net":
                    continue
                name = ""
                nodes: list[tuple[str, str]] = []
                for entry in net[1:]:
                    if tag(entry) == "name":
                        name = atom(entry[1]).removeprefix("/")
                    elif tag(entry) == "node":
                        node = {
                            tag(field): field[1]
                            for field in entry[1:]
                            if isinstance(field, list) and len(field) > 1
                        }
                        nodes.append((atom(node["ref"]), atom(node["pin"])))
                nets.append((name, nodes))
    return components, nets


def add_segment(
    board: pcbnew.BOARD,
    start: tuple[float, float],
    end: tuple[float, float],
) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(mm(0.05))
    shape.SetStart(point(*start))
    shape.SetEnd(point(*end))
    board.Add(shape)


def add_arc(
    board: pcbnew.BOARD,
    start: tuple[float, float],
    mid: tuple[float, float],
    end: tuple[float, float],
) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_ARC)
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(mm(0.05))
    shape.SetArcGeometry(point(*start), point(*mid), point(*end))
    board.Add(shape)


def add_outline(board: pcbnew.BOARD) -> None:
    diagonal = RADIUS / math.sqrt(2)
    add_segment(board, (LEFT + RADIUS, TOP), (RIGHT - RADIUS, TOP))
    add_arc(
        board,
        (RIGHT - RADIUS, TOP),
        (RIGHT - RADIUS + diagonal, TOP + RADIUS - diagonal),
        (RIGHT, TOP + RADIUS),
    )
    add_segment(board, (RIGHT, TOP + RADIUS), (RIGHT, BOTTOM - RADIUS))
    add_arc(
        board,
        (RIGHT, BOTTOM - RADIUS),
        (RIGHT - RADIUS + diagonal, BOTTOM - RADIUS + diagonal),
        (RIGHT - RADIUS, BOTTOM),
    )
    add_segment(board, (RIGHT - RADIUS, BOTTOM), (LEFT + RADIUS, BOTTOM))
    add_arc(
        board,
        (LEFT + RADIUS, BOTTOM),
        (LEFT + RADIUS - diagonal, BOTTOM - RADIUS + diagonal),
        (LEFT, BOTTOM - RADIUS),
    )
    add_segment(board, (LEFT, BOTTOM - RADIUS), (LEFT, TOP + RADIUS))
    add_arc(
        board,
        (LEFT, TOP + RADIUS),
        (LEFT + RADIUS - diagonal, TOP + RADIUS - diagonal),
        (LEFT + RADIUS, TOP),
    )


PLACEMENT: dict[str, tuple[float, float, float, bool]] = {
    "J1": (32.00, 66.40, 90, False),
    "J2": (62.00, 66.40, 90, False),
    "U1": (58.00, 39.00, 0, False),
    "Y1": (52.00, 24.80, 0, False),
    "C13": (55.20, 23.80, 90, False),
    "C14": (55.20, 27.00, 90, False),
    "C15": (62.50, 46.20, 90, False),
    "C9": (69.50, 30.50, 90, False),
    "C10": (70.50, 35.00, 90, False),
    "C11": (70.50, 39.50, 90, False),
    "C12": (56.00, 46.20, 90, False),
    "NT1": (74.50, 46.50, 90, False),
    "R13": (80.00, 35.00, 0, False),
    "R14": (79.00, 42.00, 0, False),
    "SW1": (89.00, 38.00, 90, False),
    "SJ1": (84.50, 28.50, 90, True),
    "RB1": (28.50, 29.50, 0, False),
    "R1": (34.00, 27.80, 0, False),
    "R2": (34.00, 31.20, 0, False),
    "C1": (39.00, 27.80, 90, False),
    "C2": (39.00, 31.20, 90, False),
    "RB2": (28.50, 37.00, 0, False),
    "R3": (34.00, 35.30, 0, False),
    "R4": (34.00, 38.70, 0, False),
    "C3": (39.00, 35.30, 90, False),
    "C4": (39.00, 38.70, 90, False),
    "R5": (27.50, 47.00, 0, False),
    "R6": (32.00, 47.00, 0, False),
    "R7": (36.50, 47.00, 0, False),
    "R8": (27.50, 52.00, 0, False),
    "R9": (32.00, 52.00, 0, False),
    "R10": (36.50, 52.00, 0, False),
    "R11": (41.00, 47.00, 0, False),
    "R12": (41.00, 52.00, 0, False),
    "C5": (44.50, 47.00, 90, False),
    "C6": (44.50, 52.00, 90, False),
    "R15": (52.00, 53.00, 0, False),
    "R16": (56.50, 53.00, 0, False),
    "R17": (61.00, 53.00, 0, False),
    "R18": (52.00, 58.00, 0, False),
    "R19": (56.50, 58.00, 0, False),
    "R20": (61.00, 58.00, 0, False),
    "R21": (65.50, 53.00, 0, False),
    "R22": (65.50, 58.00, 0, False),
    "C7": (69.00, 53.00, 90, False),
    "C8": (69.00, 58.00, 90, False),
    "TP1": (29.50, 23.50, 0, True),
    "TP2": (35.00, 23.50, 0, True),
    "TP3": (40.50, 23.50, 0, True),
}


def add_mounting_holes(board: pcbnew.BOARD) -> None:
    for index, (x, y) in enumerate(((25, 25), (90, 25), (25, 65), (90, 65)), 1):
        hole = pcbnew.FootprintLoad(
            str(KICAD_FOOTPRINTS / "MountingHole.pretty"),
            "MountingHole_2.2mm_M2",
        )
        if hole is None:
            raise RuntimeError("Unable to load M2 mounting hole")
        hole.SetReference(f"H{index}")
        hole.SetPosition(point(x, y))
        hole.SetExcludedFromBOM(True)
        hole.SetExcludedFromPosFiles(True)
        hole.Reference().SetVisible(False)
        hole.Value().SetVisible(False)
        board.Add(hole)


def add_footprints(
    board: pcbnew.BOARD,
    components: dict[str, dict[str, str]],
) -> dict[str, pcbnew.FOOTPRINT]:
    footprints: dict[str, pcbnew.FOOTPRINT] = {}
    for reference, properties in components.items():
        if reference not in PLACEMENT:
            raise RuntimeError(f"No placement defined for {reference}")
        library, name = properties["footprint"].split(":", 1)
        footprint = pcbnew.FootprintLoad(
            str(KICAD_FOOTPRINTS / f"{library}.pretty"),
            name,
        )
        if footprint is None:
            raise RuntimeError(f"Unable to load {properties['footprint']}")
        x, y, rotation, bottom = PLACEMENT[reference]
        footprint.SetReference(reference)
        footprint.SetValue(properties["value"])
        footprint.SetPath(pcbnew.KIID_PATH(f"/{properties['uuid']}"))
        footprint.SetPosition(point(x, y))
        footprint.SetOrientationDegrees(rotation)
        footprint.Value().SetVisible(False)
        footprint.Reference().SetVisible(False)
        if reference == "U1":
            footprint.Models().clear()
            model = pcbnew.FP_3DMODEL()
            model.m_Filename = STPM34_MODEL
            footprint.Models().append(model)
        if reference.startswith("TP") or reference in {"NT1", "SJ1"}:
            footprint.SetExcludedFromBOM(True)
            footprint.SetExcludedFromPosFiles(True)
        board.Add(footprint)
        if bottom:
            footprint.Flip(point(x, y), False)
        footprints[reference] = footprint
    return footprints


def assign_nets(
    board: pcbnew.BOARD,
    footprints: dict[str, pcbnew.FOOTPRINT],
    nets: list[tuple[str, list[tuple[str, str]]]],
) -> None:
    for code, (name, nodes) in enumerate(nets, 1):
        net = pcbnew.NETINFO_ITEM(board, name, code)
        board.Add(net)
        for reference, pin in nodes:
            pad = footprints[reference].FindPadByNumber(pin)
            if pad is None:
                raise RuntimeError(f"Missing pad {reference}.{pin}")
            pad.SetNet(net)


def set_design_rules(board: pcbnew.BOARD) -> None:
    board.GetDesignSettings().m_TrackMinWidth = mm(0.15)
    default = board.GetAllNetClasses()["Default"]
    default.SetClearance(mm(0.18))
    default.SetTrackWidth(mm(0.18))
    default.SetViaDiameter(mm(0.60))
    default.SetViaDrill(mm(0.30))

    analog = pcbnew.NETCLASS("Analog")
    analog.SetClearance(mm(0.20))
    analog.SetTrackWidth(mm(0.25))
    analog.SetViaDiameter(mm(0.65))
    analog.SetViaDrill(mm(0.30))
    board.GetNetClasses()["Analog"] = analog

    power = pcbnew.NETCLASS("Power")
    power.SetClearance(mm(0.20))
    power.SetTrackWidth(mm(0.35))
    power.SetViaDiameter(mm(0.70))
    power.SetViaDrill(mm(0.35))
    board.GetNetClasses()["Power"] = power

    for name in (
        "VAC_P",
        "VAC_N",
        "VAC_P_MID",
        "VAC_N_MID",
        "VDIV_P",
        "VDIV_N",
        "VIP1",
        "VIN1",
        "V2AC_P",
        "V2AC_N",
        "V2AC_P_MID",
        "V2AC_N_MID",
        "V2DIV_P",
        "V2DIV_N",
        "VIP2",
        "VIN2",
        "CT1_P",
        "CT1_N",
        "IIP1",
        "IIN1",
        "CT2_P",
        "CT2_N",
        "IIP2",
        "IIN2",
        "VREF1",
        "VREF2",
        "XTAL1",
        "XTAL2",
    ):
        net = board.FindNet(name)
        if net is not None:
            net.SetNetClass(analog)
    for name in ("+3V3", "VDDA", "VDDD", "GNDA", "GND_REF", "DGND"):
        net = board.FindNet(name)
        if net is not None:
            net.SetNetClass(power)


def main() -> None:
    components, nets = read_netlist()
    board = pcbnew.BOARD()
    title = board.GetTitleBlock()
    title.SetTitle("STPM34 Dual-Voltage Dual-Current Energy Metering Breakout")
    title.SetCompany("Whatnick")
    title.SetRevision("A")
    title.SetComment(0, "Dual isolated 9 VAC and dual 100 A:50 mA CT development board")
    title.SetComment(1, "TAPR Open Hardware License 1.0")
    add_outline(board)
    add_mounting_holes(board)
    footprints = add_footprints(board, components)
    assign_nets(board, footprints, nets)
    set_design_rules(board)
    board.BuildConnectivity()
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Wrote {OUTPUT}")
    print(f"Footprints: {len(board.GetFootprints())}; nets: {board.GetNetCount() - 1}")


if __name__ == "__main__":
    main()
