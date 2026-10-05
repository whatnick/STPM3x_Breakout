"""STPM32 production part selections and Elecrow BOM helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"


@dataclass(frozen=True)
class PartSelection:
    references: tuple[str, ...]
    value: str
    footprint: str
    manufacturer: str
    mpn: str
    lcsc: str
    package: str
    description: str
    assembly: str = "SMT"
    notes: str = ""

    @property
    def purchase_url(self) -> str:
        return f"https://www.lcsc.com/product-detail/{self.lcsc}.html"

    @property
    def schematic_properties(self) -> dict[str, str]:
        properties = {
            "Manufacturer": self.manufacturer,
            "MPN": self.mpn,
            "LCSC": self.lcsc,
            "Package": self.package,
            "Assembly": self.assembly,
            "Description": self.description,
            "Purchase URL": self.purchase_url,
        }
        if self.notes:
            properties["Notes"] = self.notes
        return properties


PARTS = (
    PartSelection(
        ("U1",),
        "STPM32",
        "Package_DFN_QFN:VQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm",
        "STMicroelectronics",
        "STPM32TR",
        "C128380",
        "VQFN-24-EP, 4 x 4 mm, 0.5 mm pitch",
        "Single-phase energy-metering ASIC",
        notes="Inspect exposed-pad paste and voiding during DFM review.",
    ),
    PartSelection(
        ("R1", "R2"),
        "100R",
        R0603,
        "YAGEO",
        "RC0603FR-07100RL",
        "C105588",
        "0603 (1608 Metric)",
        "100 ohm, 1%, 0.1 W thick-film resistor",
    ),
    PartSelection(
        ("R3", "R4", "R6", "R7"),
        "100k",
        R0603,
        "YAGEO",
        "RT0603BRD07100KL",
        "C122538",
        "0603 (1608 Metric)",
        "100 kohm, 0.1%, 25 ppm/C thin-film resistor",
        notes="Use one lot for all four voltage-divider resistors.",
    ),
    PartSelection(
        ("R5", "R8"),
        "2.49k",
        R0603,
        "YAGEO",
        "RT0603BRD072K49L",
        "C861299",
        "0603 (1608 Metric)",
        "2.49 kohm, 0.1%, 25 ppm/C thin-film resistor",
        notes="Use one lot for the matched voltage-divider low sides.",
    ),
    PartSelection(
        ("R9", "R10"),
        "1k",
        R0603,
        "YAGEO",
        "RC0603FR-071KL",
        "C22548",
        "0603 (1608 Metric)",
        "1 kohm, 1%, 0.1 W thick-film resistor",
    ),
    PartSelection(
        ("R11", "R12"),
        "10k",
        R0603,
        "YAGEO",
        "RC0603FR-0710KL",
        "C98220",
        "0603 (1608 Metric)",
        "10 kohm, 1%, 0.1 W thick-film resistor",
    ),
    PartSelection(
        ("RB1",),
        "2.4R",
        R0603,
        "YAGEO",
        "RC0603FR-072R4L",
        "C137746",
        "0603 (1608 Metric)",
        "2.4 ohm, 1%, 0.1 W CT burden resistor",
        notes=(
            "About 6 mW at 50 mA RMS. The 200 ppm/C TCR is suitable for "
            "development; use a lower-TCR burden for calibration-grade builds."
        ),
    ),
    PartSelection(
        ("C1", "C2"),
        "330n",
        C0603,
        "CCTC",
        "TCC0603X7R334K500CT",
        "C282682",
        "0603 (1608 Metric)",
        "330 nF, 50 V, 10%, X7R MLCC",
    ),
    PartSelection(
        ("C3", "C4"),
        "33n",
        C0603,
        "Samsung Electro-Mechanics",
        "CL10B333KB8NNNC",
        "C21117",
        "0603 (1608 Metric)",
        "33 nF, 50 V, 10%, X7R MLCC",
    ),
    PartSelection(
        ("C12",),
        "100n",
        C0603,
        "Samsung Electro-Mechanics",
        "CL10B104KB8NNNC",
        "C1591",
        "0603 (1608 Metric)",
        "100 nF, 50 V, 10%, X7R MLCC",
    ),
    PartSelection(
        ("C13", "C14"),
        "15p",
        C0603,
        "Samsung Electro-Mechanics",
        "CL10C150JB8NNNC",
        "C1644",
        "0603 (1608 Metric)",
        "15 pF, 50 V, 5%, C0G MLCC",
    ),
    PartSelection(
        ("C9", "C10"),
        "1u",
        C0805,
        "Samsung Electro-Mechanics",
        "CL21B105KAFNNNE",
        "C116352",
        "0805 (2012 Metric)",
        "1 uF, 25 V, 10%, X7R MLCC",
    ),
    PartSelection(
        ("C11",),
        "4.7u",
        C0805,
        "Samsung Electro-Mechanics",
        "CL21A475KOFNNNG",
        "C16194928",
        "0805 (2012 Metric)",
        "4.7 uF, 16 V, 10%, X5R MLCC",
    ),
    PartSelection(
        ("Y1",),
        "16MHz",
        "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
        "YXC",
        "X322516MOB4SI",
        "C12668",
        "SMD3225-4P",
        "16 MHz, 12 pF load crystal",
        notes=(
            "12 pF load is consistent with two 15 pF capacitors plus estimated "
            "pin and PCB stray capacitance; verify oscillator margin on prototypes."
        ),
    ),
    PartSelection(
        ("SW1",),
        "RESET",
        "Button_Switch_SMD:SW_SPST_CK_RS282G05A3",
        "C&K",
        "RS-282G05A3-SMRT",
        "C221930",
        "C&K RS-282G05A3 SMD",
        "Momentary SPST reset switch",
    ),
    PartSelection(
        ("J1",),
        "BREADBOARD I/O",
        "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical",
        "XFCN",
        "PZ254V-11-12P",
        "C2840012",
        "1x12, 2.54 mm pitch, vertical THT",
        "Single-row male pin header",
        assembly="THT",
        notes="Quote THT assembly separately and confirm pin protrusion suits breadboards.",
    ),
)

NON_BOM_REFERENCES = ("NT1", "TP1", "TP2", "TP3", "TP4")


def apply_part_metadata(schematic) -> None:
    selected_references: set[str] = set()
    for part in PARTS:
        for reference in part.references:
            component = schematic.components.get(reference)
            if component is None:
                raise RuntimeError(f"Missing expected component {reference}")
            if component.value != part.value:
                raise RuntimeError(
                    f"{reference} value is {component.value!r}, expected {part.value!r}"
                )
            if component.footprint != part.footprint:
                raise RuntimeError(
                    f"{reference} footprint is {component.footprint!r}, "
                    f"expected {part.footprint!r}"
                )
            component.in_bom = True
            component.add_properties(part.schematic_properties, hidden=True)
            selected_references.add(reference)

    for reference in NON_BOM_REFERENCES:
        component = schematic.components.get(reference)
        if component is None:
            raise RuntimeError(f"Missing expected non-BOM item {reference}")
        component.in_bom = False

    uncovered = sorted(
        component.reference
        for component in schematic.components.all()
        if component.footprint
        and component.in_bom
        and component.reference not in selected_references
    )
    if uncovered:
        raise RuntimeError(f"Physical BOM items lack selections: {', '.join(uncovered)}")


def write_elecrow_bom(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(
            (
                "Reference Designator",
                "Quantity",
                "Manufacturer",
                "Manufacturer Part Number",
                "Description / Value",
                "Package / Footprint",
                "LCSC Part Number",
                "Assembly Type",
                "Purchase URL",
                "Notes",
            )
        )
        for part in PARTS:
            writer.writerow(
                (
                    ",".join(part.references),
                    len(part.references),
                    part.manufacturer,
                    part.mpn,
                    part.description,
                    f"{part.package}; {part.footprint}",
                    part.lcsc,
                    part.assembly,
                    part.purchase_url,
                    part.notes,
                )
            )


def selected_references() -> Iterable[str]:
    for part in PARTS:
        yield from part.references
