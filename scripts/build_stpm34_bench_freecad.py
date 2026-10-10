#!/usr/bin/env python3
"""Build the STPM34 isolated-low-voltage demonstration bench in FreeCAD."""

from pathlib import Path
import re
import shutil

import FreeCAD as App
import Import
import Mesh
import Part


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM34_Breakout"
OUTPUT = PROJECT / "bench"


def add_shape(doc, name, shape, color):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = name
    obj.Shape = shape
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = color
    return obj


def cylinder_between(start, end, radius):
    vector = end.sub(start)
    return Part.makeCylinder(radius, vector.Length, start, vector)


def add_wire(doc, name, points, radius, color):
    pieces = [
        cylinder_between(first, second, radius)
        for first, second in zip(points, points[1:])
    ]
    return add_shape(doc, name, Part.makeCompound(pieces), color)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    doc = App.newDocument("STPM34_Bench_Setup")

    white = (0.92, 0.92, 0.88)
    dark = (0.04, 0.05, 0.06)
    green = (0.08, 0.32, 0.18)
    red = (0.75, 0.04, 0.03)
    blue = (0.03, 0.15, 0.75)
    gold = (0.82, 0.52, 0.08)
    grey = (0.25, 0.27, 0.30)

    add_shape(
        doc,
        "Breadboard_Base",
        Part.makeBox(200, 90, 8, App.Vector(-100, -45, 0)),
        white,
    )
    add_shape(
        doc,
        "Breadboard_Centre_Groove",
        Part.makeBox(190, 4, 1, App.Vector(-95, -2, 8)),
        dark,
    )
    add_shape(
        doc,
        "STPM34_PCB",
        Part.makeBox(75, 50, 1.6, App.Vector(-37.5, -25, 10)),
        green,
    )
    for x in (-32.5, 32.5):
        for y in (-20, 20):
            add_shape(
                doc,
                f"Board_Standoff_{x}_{y}",
                Part.makeCylinder(2.2, 2, App.Vector(x, y, 8)),
                grey,
            )

    add_shape(
        doc,
        "STPM34_U1",
        Part.makeBox(7, 7, 1.4, App.Vector(-3.5, -3.5, 11.6)),
        dark,
    )
    add_shape(
        doc,
        "STPM34_Reset",
        Part.makeBox(7, 5, 4, App.Vector(26, -2.5, 11.6)),
        grey,
    )
    for header, start, count in (("J1", -31, 8), ("J2", 6, 10)):
        for index in range(count):
            x = start + index * 2.54
            add_shape(
                doc,
                f"STPM34_{header}_Pin_{index + 1}",
                Part.makeBox(0.65, 0.65, 9, App.Vector(x, -23, 7)),
                gold,
            )
            add_shape(
                doc,
                f"STPM34_{header}_Body_{index + 1}",
                Part.makeBox(2.2, 2.2, 2.5, App.Vector(x - 0.78, -23.78, 11)),
                dark,
            )
    for index, (x, y) in enumerate(
        (
            (-26, -10), (-21, -10), (-16, -10), (-26, -5), (-21, -5),
            (-16, -5), (14, -9), (19, -9), (24, -9), (14, -4),
            (19, -4), (24, -4), (-8, 12), (-2, 12), (4, 12),
        )
    ):
        add_shape(
            doc,
            f"STPM34_Passive_{index + 1}",
            Part.makeBox(3.2, 1.6, 1.2, App.Vector(x, y, 11.6)),
            grey,
        )

    barrel_body = Part.makeCylinder(
        6, 22, App.Vector(-84, 24, 11), App.Vector(1, 0, 0)
    )
    barrel_tip = Part.makeCylinder(
        3.5, 8, App.Vector(-62, 24, 11), App.Vector(1, 0, 0)
    )
    add_shape(doc, "Isolated_9VAC_Barrel_Jack", barrel_body.fuse(barrel_tip), dark)
    add_shape(
        doc,
        "Barrel_Breakout",
        Part.makeBox(24, 18, 4, App.Vector(-62, 15, 8)),
        green,
    )
    for index, x in enumerate((-57, -49)):
        add_shape(
            doc,
            f"Barrel_Terminal_{index}",
            Part.makeBox(6, 8, 7, App.Vector(x, 20, 12)),
            blue,
        )

    add_shape(
        doc,
        "Stereo_Jack_Breakout",
        Part.makeBox(28, 18, 4, App.Vector(52, -32, 8)),
        green,
    )
    add_shape(
        doc,
        "Stereo_Jack",
        Part.makeCylinder(5, 22, App.Vector(58, -23, 12), App.Vector(1, 0, 0)),
        dark,
    )
    add_shape(
        doc,
        "Stereo_Plug",
        Part.makeCylinder(3, 20, App.Vector(80, -23, 12), App.Vector(1, 0, 0)),
        gold,
    )

    clamp = Part.makeTorus(18, 4, App.Vector(72, 12, 25))
    clamp.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
    add_shape(doc, "YHDC_CT_Clamp", clamp, dark)
    add_shape(
        doc,
        "YHDC_CT_Hinge",
        Part.makeBox(12, 10, 9, App.Vector(66, 8, 21)),
        grey,
    )

    add_shape(
        doc,
        "Lamp_Base",
        Part.makeCylinder(13, 12, App.Vector(82, 30, 8)),
        dark,
    )
    add_shape(
        doc,
        "Lamp_Bulb",
        Part.makeSphere(13, App.Vector(82, 30, 32)),
        (1.0, 0.72, 0.15),
    )
    add_shape(
        doc,
        "Lamp_Neck",
        Part.makeCylinder(7, 14, App.Vector(82, 30, 20)),
        gold,
    )

    add_wire(
        doc,
        "Voltage_Wire_Red",
        [App.Vector(-49, 24, 18), App.Vector(-30, 34, 16), App.Vector(-18, 24, 16)],
        1.2,
        red,
    )
    add_wire(
        doc,
        "Voltage_Wire_Black",
        [App.Vector(-57, 24, 18), App.Vector(-38, 40, 15), App.Vector(-15, 22, 15)],
        1.2,
        dark,
    )
    add_wire(
        doc,
        "CT_Stereo_Lead",
        [App.Vector(100, -23, 12), App.Vector(91, -5, 18), App.Vector(76, 2, 23)],
        1.4,
        dark,
    )
    add_wire(
        doc,
        "Lamp_Current_Lead",
        [App.Vector(-68, 24, 11), App.Vector(40, 30, 13), App.Vector(82, 30, 20)],
        1.5,
        red,
    )
    add_wire(
        doc,
        "Lamp_Return_Lead",
        [App.Vector(82, 30, 20), App.Vector(55, 42, 12), App.Vector(-68, 28, 11)],
        1.5,
        blue,
    )

    doc.recompute()
    fcstd = OUTPUT / "STPM34_Bench_Setup.FCStd"
    step = OUTPUT / "STPM34_Bench_Setup.step"
    obj_dir = OUTPUT / "obj"
    doc.saveAs(str(fcstd))
    backup = OUTPUT / "STPM34_Bench_Setup.FCStd1"
    if backup.exists():
        backup.unlink()
    shape_objects = [
        item
        for item in doc.Objects
        if hasattr(item, "Shape") and not item.Shape.isNull()
    ]
    Import.export(shape_objects, str(step))
    legacy_obj = OUTPUT / "STPM34_Bench_Setup.obj"
    if legacy_obj.exists():
        legacy_obj.unlink()
    if obj_dir.exists():
        shutil.rmtree(obj_dir)
    obj_dir.mkdir()
    for index, item in enumerate(shape_objects):
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.Label).strip("_")
        Mesh.export([item], str(obj_dir / f"{index:03d}_{safe}.obj"))
    print(f"Wrote {fcstd}")
    print(f"Wrote {step}")
    print(f"Wrote {len(shape_objects)} OBJ parts to {obj_dir}")


if __name__ == "__main__":
    main()
