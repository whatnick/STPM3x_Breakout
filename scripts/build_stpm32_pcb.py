#!/usr/bin/env python3
"""Build the compact STPM32 breakout PCB from the exported KiCad netlist."""

from __future__ import annotations

import math
from pathlib import Path

import pcbnew
from sexpdata import Symbol, loads


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM32_Breakout"
NETLIST = PROJECT / "STPM32_Breakout.net"
OUTPUT = PROJECT / "STPM32_Breakout.kicad_pcb"
KICAD_FOOTPRINTS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

LEFT = 20.0
TOP = 20.0
RIGHT = 58.2
BOTTOM = 48.04
RADIUS = 2.0


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
    layer: int = pcbnew.Edge_Cuts,
    width: float = 0.05,
) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(layer)
    shape.SetWidth(mm(width))
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


def add_text(
    board: pcbnew.BOARD,
    text: str,
    x: float,
    y: float,
    layer: int,
    size: float,
) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(point(x, y))
    item.SetLayer(layer)
    item.SetTextSize(point(size, size))
    item.SetTextThickness(mm(max(0.12, size * 0.16)))
    if layer in (pcbnew.B_SilkS, pcbnew.B_Cu):
        item.SetMirrored(True)
    board.Add(item)


PLACEMENT: dict[str, tuple[float, float, float, bool]] = {
    "J1": (25.00, 45.30, 90, False),
    "U1": (44.00, 30.90, 0, False),
    "Y1": (36.80, 24.50, 0, False),
    "C13": (40.50, 23.60, 90, False),
    "C14": (40.50, 27.30, 90, False),
    "TP1": (22.60, 22.60, 0, True),
    "TP2": (26.20, 22.60, 0, True),
    "TP3": (29.80, 22.60, 0, True),
    "TP4": (33.40, 22.60, 0, True),
    "R3": (29.75, 41.65, 90, False),
    "R4": (29.75, 38.65, 90, False),
    "R5": (27.20, 36.45, 0, False),
    "R9": (34.90, 36.45, 0, False),
    "C3": (38.00, 35.80, 90, False),
    "R6": (32.55, 41.65, 90, False),
    "R7": (32.55, 38.65, 90, False),
    "R8": (29.90, 34.15, 0, False),
    "R10": (35.20, 32.70, 0, False),
    "C4": (38.20, 32.80, 90, False),
    "RB1": (36.43, 42.45, 0, False),
    "R1": (36.20, 39.25, 90, False),
    "R2": (38.50, 39.25, 90, False),
    "C1": (40.20, 36.10, 90, False),
    "C2": (42.00, 36.30, 90, False),
    "C12": (47.40, 34.70, 0, False),
    "NT1": (50.10, 35.10, 90, False),
    "C10": (49.00, 32.00, 90, False),
    "C9": (49.00, 28.00, 90, False),
    "C11": (46.80, 24.30, 90, False),
    "R11": (50.30, 38.20, 0, False),
    "R12": (44.80, 41.00, 0, False),
    "SW1": (54.20, 34.20, 90, False),
}

STPM32_MODEL = "${KIPRJMOD}/models/step/STPM32_VQFN24_4x4_EP2.45.step"


def replace_3d_model(footprint: pcbnew.FOOTPRINT, filename: str) -> None:
    models = footprint.Models()
    models.clear()
    model = pcbnew.FP_3DMODEL()
    model.m_Filename = filename
    models.append(model)


def add_footprints(
    board: pcbnew.BOARD,
    components: dict[str, dict[str, str]],
) -> dict[str, pcbnew.FOOTPRINT]:
    footprints: dict[str, pcbnew.FOOTPRINT] = {}
    for reference, properties in components.items():
        library, name = properties["footprint"].split(":", 1)
        footprint = pcbnew.FootprintLoad(
            str(KICAD_FOOTPRINTS / f"{library}.pretty"),
            name,
        )
        if footprint is None:
            raise RuntimeError(f"Unable to load {properties['footprint']}")
        if reference not in PLACEMENT:
            raise RuntimeError(f"No placement defined for {reference}")
        x, y, rotation, bottom = PLACEMENT[reference]
        footprint.SetReference(reference)
        footprint.SetValue(properties["value"])
        footprint.SetPath(pcbnew.KIID_PATH(f"/{properties['uuid']}"))
        footprint.SetPosition(point(x, y))
        footprint.SetOrientationDegrees(rotation)
        footprint.Value().SetVisible(False)
        footprint.Reference().SetVisible(False)
        if reference == "U1":
            replace_3d_model(footprint, STPM32_MODEL)
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
    default = board.GetAllNetClasses()["Default"]
    default.SetClearance(mm(0.18))
    # The 0.5 mm-pitch QFN escape uses short 0.15 mm neckdowns.
    default.SetTrackWidth(mm(0.15))
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
        "CT_P",
        "CT_N",
        "IIP1",
        "IIN1",
        "VREF1",
        "XTAL1",
        "XTAL2",
    ):
        board.FindNet(name).SetNetClass(analog)
    for name in ("+3V3", "VDDA", "VDDD", "AGND", "GND_REF", "DGND"):
        board.FindNet(name).SetNetClass(power)


def add_identification(board: pcbnew.BOARD) -> None:
    add_text(board, "STPM32 ENERGY", 49.5, 22.0, pcbnew.F_SilkS, 1.0)
    add_text(board, "whatnick.com", 52.5, 24.0, pcbnew.F_SilkS, 0.8)
    add_text(board, "ISOLATED 9 VAC + CT ONLY", 39.1, 46.8, pcbnew.B_SilkS, 0.8)
    add_text(board, "NOT FOR DIRECT MAINS", 39.1, 20.9, pcbnew.B_SilkS, 0.8)
    add_text(board, "TAPR OHL 1.0", 53.0, 21.5, pcbnew.B_SilkS, 0.8)


def main() -> None:
    components, nets = read_netlist()
    board = pcbnew.BOARD()
    title = board.GetTitleBlock()
    title.SetTitle("STPM32 Energy Metering Breakout")
    title.SetCompany("Whatnick")
    title.SetRevision("A")
    title.SetComment(0, "Compact breadboard format; isolated 9 VAC and 100 A:50 mA CT")
    title.SetComment(1, "TAPR Open Hardware License 1.0")

    add_outline(board)
    footprints = add_footprints(board, components)
    assign_nets(board, footprints, nets)
    set_design_rules(board)
    add_identification(board)
    board.BuildConnectivity()
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Wrote {OUTPUT}")
    print(f"Footprints: {len(board.GetFootprints())}; nets: {board.GetNetCount() - 1}")


if __name__ == "__main__":
    main()
