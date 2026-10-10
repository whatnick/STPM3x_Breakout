#!/usr/bin/env python3
"""Render the FreeCAD-generated STPM34 isolated 9 VAC demonstration bench."""

import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM34_Breakout"
BENCH = PROJECT / "bench"
OBJ_DIR = BENCH / "obj"
OUTPUT = BENCH / "STPM34_Bench_Setup.png"
BLEND = BENCH / "STPM34_Bench_Setup.blend"


def material(name, color, metallic=0.0, roughness=0.45, emission=None):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*color, 1.0)
    value.use_nodes = True
    node = value.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1.0)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    if emission:
        node.inputs["Emission Color"].default_value = (*emission, 1.0)
        node.inputs["Emission Strength"].default_value = 3.0
    return value


def assign(obj, value):
    obj.data.materials.clear()
    obj.data.materials.append(value)


def add_text(text, location, size=0.07, color=None, rotation=(0, 0, 0)):
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.006
    assign(obj, color)
    return obj


def add_curve(name, points, radius, value):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for control, coordinate in zip(spline.bezier_points, points):
        control.co = coordinate
        control.handle_left_type = "AUTO"
        control.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    assign(obj, value)


def main():
    if not OBJ_DIR.exists():
        raise RuntimeError(f"Run build_stpm34_bench_freecad.py first: {OBJ_DIR}")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    imported = []
    for path in sorted(OBJ_DIR.glob("*.obj")):
        bpy.ops.wm.obj_import(
            filepath=str(path),
            forward_axis="NEGATIVE_Y",
            up_axis="Z",
        )
        for obj in bpy.context.selected_objects:
            obj.name = path.stem
            obj.scale = (0.01, 0.01, 0.01)
            imported.append(obj)

    white = material("Breadboard White", (0.88, 0.86, 0.80), roughness=0.7)
    green = material("PCB Green", (0.025, 0.22, 0.09), roughness=0.35)
    black = material("Connector Black", (0.018, 0.022, 0.028), roughness=0.32)
    grey = material("Hardware Grey", (0.18, 0.20, 0.23), metallic=0.25)
    gold = material("Pin Gold", (0.80, 0.45, 0.08), metallic=0.72, roughness=0.25)
    red = material("Wire Red", (0.65, 0.015, 0.01), roughness=0.35)
    blue = material("Wire Blue", (0.015, 0.08, 0.62), roughness=0.35)
    warm = material(
        "Lamp Glow",
        (1.0, 0.45, 0.06),
        roughness=0.2,
        emission=(1.0, 0.25, 0.02),
    )
    label = material("Label White", (0.95, 0.95, 0.92), roughness=0.5)

    for obj in imported:
        name = obj.name.lower()
        if "breadboard" in name:
            assign(obj, black if "groove" in name else white)
        elif "carrier" in name or "breakout" in name or "stpm34_pcb" in name:
            assign(obj, green)
        elif "stpm34" in name:
            assign(obj, grey)
        elif "wire_red" in name or "current_lead" in name:
            assign(obj, red)
        elif "wire_black" in name or "stereo_lead" in name:
            assign(obj, black)
        elif "return_lead" in name:
            assign(obj, blue)
        elif "bulb" in name:
            assign(obj, warm)
        elif "terminal" in name:
            assign(obj, blue)
        elif "jack" in name or "clamp" in name or "base" in name:
            assign(obj, black)
        elif "pin" in name or "plug" in name or "neck" in name:
            assign(obj, gold)
        else:
            assign(obj, grey)

    hole_mesh = None
    for x in range(-88, 89, 5):
        for y in (-31, -26, -21, -16, 16, 21, 26, 31):
            if hole_mesh is None:
                bpy.ops.mesh.primitive_cylinder_add(
                    vertices=12, radius=0.012, depth=0.006, location=(x / 100, y / 100, 0.083)
                )
                hole_mesh = bpy.context.object
                hole_mesh.name = "Breadboard_Hole"
                assign(hole_mesh, black)
            else:
                duplicate = hole_mesh.copy()
                duplicate.data = hole_mesh.data
                duplicate.location = (x / 100, y / 100, 0.083)
                bpy.context.collection.objects.link(duplicate)

    add_curve(
        "Lamp monitored conductor",
        [(-0.68, 0.24, 0.12), (0.15, 0.30, 0.22), (0.82, 0.30, 0.24)],
        0.014,
        red,
    )
    add_curve(
        "Lamp return conductor",
        [(0.82, 0.30, 0.24), (0.40, 0.43, 0.15), (-0.68, 0.28, 0.12)],
        0.014,
        blue,
    )

    add_text(
        "STPM34",
        (0.0, 0.08, 0.13),
        size=0.08,
        color=label,
        rotation=(0, 0, math.radians(-8)),
    )

    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -0.02))
    mat = material("Red Bench Mat", (0.16, 0.006, 0.004), roughness=0.7)
    assign(bpy.context.object, mat)

    bpy.ops.object.light_add(type="AREA", location=(-1.2, -1.0, 2.6))
    bpy.context.object.data.energy = 650
    bpy.context.object.data.shape = "DISK"
    bpy.context.object.data.size = 3.0
    bpy.ops.object.light_add(type="AREA", location=(1.8, 0.8, 1.8))
    bpy.context.object.data.energy = 350
    bpy.context.object.data.color = (1.0, 0.65, 0.35)
    bpy.context.object.data.size = 2.0

    bpy.ops.object.camera_add(location=(2.45, -3.05, 3.15))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    direction = mathutils.Vector((0.0, 0.0, 0.18)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 52

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(OUTPUT)
    scene.render.film_transparent = False
    scene.world.color = (0.025, 0.02, 0.02)
    scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    backup = BLEND.with_suffix(".blend1")
    if backup.exists():
        backup.unlink()
    bpy.ops.render.render(write_still=True)
    print(f"Wrote {BLEND}")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    import mathutils

    main()
