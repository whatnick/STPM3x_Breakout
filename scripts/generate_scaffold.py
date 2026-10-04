from __future__ import annotations

import json
import math
import uuid
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "hardware"
SYMBOLS = ROOT / "symbols"
KICAD_SHARE = Path(r"C:\Program Files\KiCad\10.0\share\kicad")

VARIANTS = {
    "STPM32": {
        "channels": "1 voltage + 1 current",
        "package": "Package_DFN_QFN:VQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm",
        "footprint": "VQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm",
        "pins": [
            (1, "CLKOUT/ZCR", "output"), (2, "CLKIN/XTAL2", "input"),
            (3, "XTAL1", "input"), (4, "LED1", "output"),
            (5, "LED2", "output"), (6, "INT1", "output"),
            (7, "EN", "input"), (8, "VIP1", "input"),
            (9, "VIN1", "input"), (10, "IIP1", "input"),
            (11, "IIN1", "input"), (12, "VREF1", "power_out"),
            (13, "GND_REF", "power_in"), (14, "GNDA", "power_in"),
            (15, "VDDA", "power_out"), (16, "GND_REG", "power_in"),
            (17, "VCC", "power_in"), (18, "GNDD", "power_in"),
            (19, "VDDD", "power_out"), (20, "SYN", "input"),
            (21, "SCS", "input"), (22, "SCL", "input"),
            (23, "MOSI/RXD", "input"), (24, "MISO/TXD", "output"),
        ],
    },
    "STPM33": {
        "channels": "1 voltage + 2 current",
        "package": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "footprint": "QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "pins": [
            (1, "CLKOUT/ZCR", "output"), (2, "CLKIN/XTAL2", "input"),
            (3, "XTAL1", "input"), (4, "LED1", "output"),
            (5, "LED2", "output"), (6, "INT1", "output"),
            (7, "INT2", "output"), (8, "EN", "input"),
            (9, "VIP1", "input"), (10, "VIN1", "input"),
            (11, "IIP1", "input"), (12, "IIN1", "input"),
            (13, "IIN2", "input"), (14, "IIP2", "input"),
            (15, "NC1", "no_connect"), (16, "NC2", "no_connect"),
            (17, "VREF1", "power_out"), (18, "GND_REF", "power_in"),
            (19, "VREF2", "power_out"), (20, "GNDA", "power_in"),
            (21, "VDDA", "power_out"), (22, "GND_REG", "power_in"),
            (23, "VCC", "power_in"), (24, "NC3", "no_connect"),
            (25, "NC4", "no_connect"), (26, "GNDD", "power_in"),
            (27, "VDDD", "power_out"), (28, "SYN", "input"),
            (29, "SCS", "input"), (30, "SCL", "input"),
            (31, "MOSI/RXD", "input"), (32, "MISO/TXD", "output"),
        ],
    },
    "STPM34": {
        "channels": "2 voltage + 2 current",
        "package": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "footprint": "QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "pins": [
            (1, "CLKOUT/ZCR", "output"), (2, "CLKIN/XTAL2", "input"),
            (3, "XTAL1", "input"), (4, "LED1", "output"),
            (5, "LED2", "output"), (6, "INT1", "output"),
            (7, "INT2", "output"), (8, "EN", "input"),
            (9, "VIP1", "input"), (10, "VIN1", "input"),
            (11, "IIP1", "input"), (12, "IIN1", "input"),
            (13, "IIN2", "input"), (14, "IIP2", "input"),
            (15, "VIN2", "input"), (16, "VIP2", "input"),
            (17, "VREF1", "power_out"), (18, "GND_REF", "power_in"),
            (19, "VREF2", "power_out"), (20, "GNDA", "power_in"),
            (21, "VDDA", "power_out"), (22, "GND_REG", "power_in"),
            (23, "VCC", "power_in"), (24, "NC", "no_connect"),
            (25, "GNDD", "power_in"), (26, "GNDD", "power_in"),
            (27, "VDDD", "power_out"), (28, "SYN", "input"),
            (29, "SCS", "input"), (30, "SCL", "input"),
            (31, "MOSI/RXD", "input"), (32, "MISO/TXD", "output"),
        ],
    },
}


def q(value_mm: float) -> int:
    return pcbnew.FromMM(value_mm)


def point(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(q(x_mm), q(y_mm))


def add_segment(board: pcbnew.BOARD, start: tuple[float, float], end: tuple[float, float]) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(q(0.05))
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
    shape.SetWidth(q(0.05))
    shape.SetArcGeometry(point(*start), point(*mid), point(*end))
    board.Add(shape)


def add_text(
    board: pcbnew.BOARD,
    text: str,
    x_mm: float,
    y_mm: float,
    layer: int,
    size_mm: float = 1.0,
) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(point(x_mm, y_mm))
    item.SetLayer(layer)
    if layer == pcbnew.B_SilkS:
        item.SetMirrored(True)
    item.SetTextSize(point(size_mm, size_mm))
    item.SetTextThickness(q(0.2))
    board.Add(item)


def add_zone_box(
    board: pcbnew.BOARD,
    left: float,
    top: float,
    right: float,
    bottom: float,
) -> None:
    for start, end in (
        ((left, top), (right, top)),
        ((right, top), (right, bottom)),
        ((right, bottom), (left, bottom)),
        ((left, bottom), (left, top)),
    ):
        shape = pcbnew.PCB_SHAPE(board)
        shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
        shape.SetLayer(pcbnew.Cmts_User)
        shape.SetWidth(q(0.15))
        shape.SetStart(point(*start))
        shape.SetEnd(point(*end))
        board.Add(shape)


def add_rounded_outline(board: pcbnew.BOARD) -> None:
    left, top, right, bottom, radius = 20.0, 20.0, 75.0, 60.0, 5.08
    diagonal = radius / math.sqrt(2)
    add_segment(board, (left + radius, top), (right - radius, top))
    add_arc(
        board,
        (right - radius, top),
        (right - radius + diagonal, top + radius - diagonal),
        (right, top + radius),
    )
    add_segment(board, (right, top + radius), (right, bottom - radius))
    add_arc(
        board,
        (right, bottom - radius),
        (right - radius + diagonal, bottom - radius + diagonal),
        (right - radius, bottom),
    )
    add_segment(board, (right - radius, bottom), (left + radius, bottom))
    add_arc(
        board,
        (left + radius, bottom),
        (left + radius - diagonal, bottom - radius + diagonal),
        (left, bottom - radius),
    )
    add_segment(board, (left, bottom - radius), (left, top + radius))
    add_arc(
        board,
        (left, top + radius),
        (left + radius - diagonal, top + radius - diagonal),
        (left + radius, top),
    )


def add_footprint(
    board: pcbnew.BOARD,
    library: str,
    name: str,
    reference: str,
    value: str,
    x_mm: float,
    y_mm: float,
) -> pcbnew.FOOTPRINT:
    footprint = pcbnew.FootprintLoad(str(KICAD_SHARE / "footprints" / f"{library}.pretty"), name)
    if footprint is None:
        raise RuntimeError(f"Could not load {library}:{name}")
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetPosition(point(x_mm, y_mm))
    board.Add(footprint)
    return footprint


def build_board(project_dir: Path, device: str, config: dict) -> None:
    board = pcbnew.BOARD()
    title = board.GetTitleBlock()
    title.SetTitle(f"{device} Breakout")
    title.SetCompany("Whatnick")
    title.SetComment(0, "KiCad 10 scaffold - analog front end not yet implemented")
    title.SetComment(1, "TAPR OHL 1.0")

    add_rounded_outline(board)
    for index, (x_mm, y_mm) in enumerate(((25, 25), (70, 25), (25, 55), (70, 55)), 1):
        hole = add_footprint(
            board,
            "MountingHole",
            "MountingHole_2.2mm_M2",
            f"H{index}",
            "M2",
            x_mm,
            y_mm,
        )
        hole.SetExcludedFromBOM(True)
        hole.SetExcludedFromPosFiles(True)

    add_footprint(
        board,
        "Package_DFN_QFN",
        config["footprint"],
        "U1",
        device,
        47.5,
        40.0,
    )

    add_zone_box(board, 27.5, 28.0, 41.0, 52.0)
    add_zone_box(board, 54.0, 28.0, 67.5, 52.0)
    add_text(board, "ANALOG INPUT / FILTER ZONE", 34.25, 53.5, pcbnew.Cmts_User, 0.8)
    add_text(board, "POWER / DIGITAL I/O ZONE", 60.75, 53.5, pcbnew.Cmts_User, 0.8)
    add_text(board, f"{device} BREAKOUT", 47.5, 23.0, pcbnew.F_SilkS, 1.2)
    add_text(board, config["channels"], 47.5, 57.0, pcbnew.F_SilkS, 0.8)
    add_text(board, "whatnick.com | TAPR OHL | NOT ISOLATED", 47.5, 57.0, pcbnew.B_SilkS, 0.8)

    pcbnew.SaveBoard(str(project_dir / f"{device}_Breakout.kicad_pcb"), board)


def blank_schematic(device: str) -> str:
    return f"""(kicad_sch
\t(version 20250114)
\t(generator \"stpm3x-scaffold\")
\t(generator_version \"1.0\")
\t(uuid \"{uuid.uuid4()}\")
\t(paper \"A4\")
\t(title_block
\t\t(title \"{device} Breakout\")
\t\t(company \"Whatnick\")
\t\t(comment 1 \"Electrical scaffold: place verified STPM3x symbol and implement datasheet blocks\")
\t)
\t(lib_symbols)
\t(sheet_instances
\t\t(path \"/\"
\t\t\t(page \"1\")
\t\t)
\t)
\t(embedded_fonts no)
)
"""


def project_json(device: str, schematic_uuid: str) -> dict:
    project_name = f"{device}_Breakout"
    return {
        "board": {
            "design_settings": {
                "defaults": {
                    "board_outline_line_width": 0.05,
                    "copper_line_width": 0.2,
                    "silk_line_width": 0.1,
                    "silk_text_size_h": 0.8,
                    "silk_text_size_v": 0.8,
                    "silk_text_thickness": 0.2,
                },
                "rules": {
                    "min_clearance": 0.15,
                    "min_copper_edge_clearance": 0.5,
                    "min_hole_clearance": 0.15,
                    "min_hole_to_hole": 0.25,
                    "min_text_height": 0.8,
                    "min_text_thickness": 0.08,
                    "min_track_width": 0.15,
                    "min_via_annular_width": 0.1,
                    "min_via_diameter": 0.45,
                },
            }
        },
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "erc": {"erc_exclusions": [], "meta": {"version": 0}},
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        "meta": {"filename": f"{project_name}.kicad_pro", "version": 3},
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12,
                    "clearance": 0.15,
                    "diff_pair_gap": 0.25,
                    "diff_pair_via_gap": 0.25,
                    "diff_pair_width": 0.2,
                    "line_style": 0,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Default",
                    "priority": 2147483647,
                    "track_width": 0.15,
                    "via_diameter": 0.45,
                    "via_drill": 0.2,
                    "wire_width": 6,
                },
                {
                    "bus_width": 12,
                    "clearance": 0.15,
                    "diff_pair_gap": 0.25,
                    "diff_pair_via_gap": 0.25,
                    "diff_pair_width": 0.2,
                    "line_style": 0,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Power",
                    "priority": 0,
                    "track_width": 0.25,
                    "via_diameter": 0.5,
                    "via_drill": 0.25,
                    "wire_width": 6,
                },
            ],
            "meta": {"version": 5},
            "netclass_patterns": [
                {"netclass": "Power", "pattern": "VCC"},
                {"netclass": "Power", "pattern": "VDDA"},
                {"netclass": "Power", "pattern": "VDDD"},
            ],
        },
        "pcbnew": {"last_paths": {"plot": "gerbers"}},
        "schematic": {
            "annotate_start_num": 0,
            "drawing": {"default_line_thickness": 6, "default_text_size": 50},
            "top_level_sheets": [
                {
                    "filename": f"{project_name}.kicad_sch",
                    "name": project_name,
                    "uuid": schematic_uuid,
                }
            ],
        },
        "sheets": [],
        "text_variables": {},
    }


def make_symbol(device: str, config: dict) -> str:
    pins = config["pins"]
    half = (len(pins) + 1) // 2
    left = pins[:half]
    right = pins[half:]
    height = max(len(left), len(right)) * 2.54 + 2.54
    body_top = height / 2
    body_bottom = -body_top
    pin_lines = []

    for index, (number, name, pin_type) in enumerate(left):
        y = body_top - 2.54 - index * 2.54
        pin_lines.append(
            f"""\t\t(pin {pin_type} line
\t\t\t(at {-12.7:g} {y:g} 0)
\t\t\t(length 2.54)
\t\t\t(name \"{name}\" (effects (font (size 1.27 1.27))))
\t\t\t(number \"{number}\" (effects (font (size 1.27 1.27))))
\t\t)"""
        )
    for index, (number, name, pin_type) in enumerate(right):
        y = body_top - 2.54 - index * 2.54
        pin_lines.append(
            f"""\t\t(pin {pin_type} line
\t\t\t(at {12.7:g} {y:g} 180)
\t\t\t(length 2.54)
\t\t\t(name \"{name}\" (effects (font (size 1.27 1.27))))
\t\t\t(number \"{number}\" (effects (font (size 1.27 1.27))))
\t\t)"""
        )

    return f"""\t(symbol \"{device}\"
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(property \"Reference\" \"U\" (at 0 {body_top + 2.54:g} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property \"Value\" \"{device}\" (at 0 {body_bottom - 2.54:g} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property \"Footprint\" \"{config['package']}\" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property \"Datasheet\" \"https://www.st.com/resource/en/datasheet/stpm34.pdf\" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property \"Description\" \"STMicroelectronics {device} energy metering IC, {config['channels']}\" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property \"Manufacturer\" \"STMicroelectronics\" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property \"MPN\" \"{device}TR\" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property \"DigiKey\" \"https://www.digikey.com/en/products/result?keywords={device}TR\" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property \"Mouser\" \"https://www.mouser.com/c/?q={device}TR\" (at 0 0 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(symbol \"{device}_0_1\"
\t\t\t(rectangle
\t\t\t\t(start -10.16 {body_bottom:g})
\t\t\t\t(end 10.16 {body_top:g})
\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t(fill (type background))
\t\t\t)
\t\t)
\t\t(symbol \"{device}_1_1\"
{chr(10).join(pin_lines)}
\t\t)
\t)"""


def build_symbol_library() -> None:
    SYMBOLS.mkdir(parents=True, exist_ok=True)
    symbols = "\n".join(make_symbol(device, config) for device, config in VARIANTS.items())
    content = f"""(kicad_symbol_lib
\t(version 20241209)
\t(generator \"stpm3x-scaffold\")
\t(generator_version \"1.0\")
{symbols}
)
"""
    (SYMBOLS / "STPM3x.kicad_sym").write_text(content, encoding="utf-8")


def build_project(device: str, config: dict) -> None:
    project_name = f"{device}_Breakout"
    project_dir = HARDWARE / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    schematic = blank_schematic(device)
    schematic_uuid = schematic.split('(uuid "', 1)[1].split('"', 1)[0]
    (project_dir / f"{project_name}.kicad_sch").write_text(schematic, encoding="utf-8")
    (project_dir / f"{project_name}.kicad_pro").write_text(
        json.dumps(project_json(device, schematic_uuid), indent=2) + "\n",
        encoding="utf-8",
    )
    (project_dir / "sym-lib-table").write_text(
        '(sym_lib_table\n'
        '  (lib (name "STPM3x")(type "KiCad")'
        '(uri "${KIPRJMOD}/../../symbols/STPM3x.kicad_sym")(options "")(descr ""))\n'
        ')\n',
        encoding="utf-8",
    )
    (project_dir / "README.md").write_text(
        f"""# {project_name}

KiCad 10 scaffold for the STMicroelectronics {device}.

- Channels: {config['channels']}
- Footprint: `{config['package']}`
- Board: 55 x 40 mm, 5.08 mm rounded corners, four M2 mounting holes
- Status: mechanical and library scaffold only; electrical design is pending

Place `{device}` from the project-local `STPM3x` symbol library, then implement
the relevant blocks in `docs/design-requirements.md`. Do not connect hazardous
voltages directly to the board without a reviewed isolation and protection
design.
""",
        encoding="utf-8",
    )
    build_board(project_dir, device, config)


def main() -> None:
    build_symbol_library()
    for device, config in VARIANTS.items():
        build_project(device, config)
    print(f"Generated {len(VARIANTS)} KiCad 10 project scaffolds.")


if __name__ == "__main__":
    main()
