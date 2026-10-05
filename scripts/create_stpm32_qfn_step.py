#!/usr/bin/env python3
"""Generate the project-local STPM32 VQFN-24 STEP model."""

from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "hardware"
    / "STPM32_Breakout"
    / "models"
    / "step"
    / "STPM32_VQFN24_4x4_EP2.45.step"
)

BODY_SIZE = 4.0
BODY_BOTTOM = 0.05
BODY_HEIGHT = 0.95
LEAD_WIDTH = 0.24
LEAD_LENGTH = 0.40
LEAD_HEIGHT = 0.20
PITCH = 0.5
# The package drawing specifies 2.45 mm nominal; the ST vendor STEP measures
# 2.425 mm and is used here to avoid the body/pad coplanarity overlap.
EXPOSED_PAD_SIZE = 2.425


def box(x: float, y: float, z: float, center: tuple[float, float, float]):
    return cq.Workplane("XY").box(x, y, z).translate(center)


def make_body():
    body = box(
        BODY_SIZE,
        BODY_SIZE,
        BODY_HEIGHT,
        (0, 0, BODY_BOTTOM + BODY_HEIGHT / 2),
    )
    body = body.edges("|Z").chamfer(0.08)
    pin_one_dimple = (
        cq.Workplane("XY")
        .workplane(offset=BODY_BOTTOM + BODY_HEIGHT - 0.06)
        .center(-1.45, 1.45)
        .circle(0.18)
        .extrude(0.12)
    )
    return body.cut(pin_one_dimple)


def make_leads():
    lead_solids = []
    coordinates = tuple((index - 2.5) * PITCH for index in range(6))
    edge_center = BODY_SIZE / 2 - LEAD_LENGTH / 2

    for coordinate in coordinates:
        lead_solids.append(
            box(
                LEAD_LENGTH,
                LEAD_WIDTH,
                LEAD_HEIGHT,
                (-edge_center, coordinate, LEAD_HEIGHT / 2),
            ).val()
        )
        lead_solids.append(
            box(
                LEAD_LENGTH,
                LEAD_WIDTH,
                LEAD_HEIGHT,
                (edge_center, coordinate, LEAD_HEIGHT / 2),
            ).val()
        )
        lead_solids.append(
            box(
                LEAD_WIDTH,
                LEAD_LENGTH,
                LEAD_HEIGHT,
                (coordinate, -edge_center, LEAD_HEIGHT / 2),
            ).val()
        )
        lead_solids.append(
            box(
                LEAD_WIDTH,
                LEAD_LENGTH,
                LEAD_HEIGHT,
                (coordinate, edge_center, LEAD_HEIGHT / 2),
            ).val()
        )

    exposed_pad = box(
        EXPOSED_PAD_SIZE,
        EXPOSED_PAD_SIZE,
        LEAD_HEIGHT,
        (0, 0, LEAD_HEIGHT / 2),
    ).val()
    return cq.Compound.makeCompound([*lead_solids, exposed_pad])


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    assembly = cq.Assembly(name="STPM32_VQFN24")
    assembly.add(make_body(), name="molded_body", color=cq.Color(0.06, 0.06, 0.065))
    assembly.add(make_leads(), name="terminals", color=cq.Color(0.72, 0.72, 0.68))
    assembly.save(str(OUTPUT), exportType="STEP", mode="default")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
