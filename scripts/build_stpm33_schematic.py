#!/usr/bin/env python3
"""Build the STPM33 breakout schematic with isolated voltage and dual CT inputs."""

from pathlib import Path

import kicad_sch_api as ksa

from stpm33_parts import apply_part_metadata


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_LIBRARY = ROOT / "symbols" / "STPM3x.kicad_sym"
OUTPUT = ROOT / "hardware" / "STPM33_Breakout" / "STPM33_Breakout.kicad_sch"

R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"


def main() -> None:
    cache = ksa.get_symbol_cache()
    cache.add_library_path(SYMBOL_LIBRARY)

    schematic = ksa.create_schematic("STPM33_Breakout")
    schematic.set_title_block(
        title="STPM33 Energy Metering Breakout",
        rev="A",
        company="Whatnick",
        comments={
            1: "Isolated 9 VAC voltage input and two 100 A:50 mA CT inputs",
            2: "TAPR Open Hardware License 1.0",
        },
    )

    def add(
        lib_id: str,
        reference: str,
        value: str,
        position: tuple[float, float],
        footprint: str = "",
        rotation: float = 0.0,
    ):
        return schematic.components.add(
            lib_id,
            reference,
            value,
            position=position,
            footprint=footprint,
            rotation=rotation,
        )

    def net(reference: str, pin: str, name: str) -> None:
        schematic.add_label(name, pin=(reference, pin), size=1.0)

    def two_pin(
        reference: str,
        value: str,
        position: tuple[float, float],
        pin1_net: str,
        pin2_net: str,
        *,
        capacitor: bool = False,
        footprint: str | None = None,
        rotation: float = 0.0,
    ) -> None:
        add(
            "Device:C" if capacitor else "Device:R",
            reference,
            value,
            position,
            footprint or (C0603 if capacitor else R0603),
            rotation,
        )
        net(reference, "1", pin1_net)
        net(reference, "2", pin2_net)

    u1 = add(
        "STPM3x:STPM33",
        "U1",
        "STPM33",
        (149.86, 91.44),
        "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
    )
    u1_nets = {
        "1": "CLKOUT_ZCR",
        "2": "XTAL2",
        "3": "XTAL1",
        "4": "LED1",
        "5": "LED2",
        "6": "INT1",
        "7": "INT2",
        "8": "EN",
        "9": "VIP1",
        "10": "VIN1",
        "11": "IIP1",
        "12": "IIN1",
        "13": "IIN2",
        "14": "IIP2",
        "17": "VREF1",
        "18": "GND_REF",
        "19": "VREF2",
        "20": "GNDA",
        "21": "VDDA",
        "22": "GNDA",
        "23": "+3V3",
        "26": "DGND",
        "27": "VDDD",
        "28": "SYN",
        "29": "SCS",
        "30": "SCL",
        "31": "MOSI_RXD",
        "32": "MISO_TXD",
    }
    for pin, name in u1_nets.items():
        net("U1", pin, name)
    for pin in ("15", "16", "24", "25"):
        schematic.no_connects.add(u1.get_pin_position(pin))

    two_pin("C9", "1u", (182.88, 73.66), "+3V3", "DGND", capacitor=True, footprint=C0805)
    two_pin("C10", "1u", (182.88, 83.82), "VDDA", "GNDA", capacitor=True, footprint=C0805)
    two_pin("C11", "4.7u", (182.88, 93.98), "VDDD", "DGND", capacitor=True, footprint=C0805)
    two_pin("C12", "100n", (170.18, 104.14), "VREF1", "GND_REF", capacitor=True)
    two_pin("C15", "100n", (182.88, 104.14), "VREF2", "GND_REF", capacitor=True)

    add(
        "Connector_Generic:Conn_01x03",
        "NT1",
        "ANALOG/DIGITAL STAR",
        (196.85, 104.14),
        "NetTie:NetTie-3_SMD_Pad0.5mm",
    )
    net("NT1", "1", "GNDA")
    net("NT1", "2", "GND_REF")
    net("NT1", "3", "DGND")

    add(
        "Device:Crystal",
        "Y1",
        "16MHz",
        (149.86, 50.80),
        "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
    )
    net("Y1", "1", "XTAL1")
    net("Y1", "2", "XTAL2")
    two_pin("C13", "15p", (140.97, 58.42), "XTAL1", "DGND", capacitor=True)
    two_pin("C14", "15p", (158.75, 58.42), "XTAL2", "DGND", capacitor=True)

    two_pin("R13", "10k", (170.18, 50.80), "+3V3", "EN")
    add(
        "Switch:SW_Push",
        "SW1",
        "RESET",
        (182.88, 50.80),
        "Button_Switch_SMD:SW_SPST_CK_RS282G05A3",
    )
    net("SW1", "1", "EN")
    net("SW1", "2", "DGND")
    two_pin("R14", "10k", (195.58, 50.80), "SCS", "MODE_BIAS")
    add(
        "Connector_Generic:Conn_01x03",
        "SJ1",
        "SPI / UART",
        (195.58, 63.50),
        "Jumper:SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm",
    )
    net("SJ1", "1", "DGND")
    net("SJ1", "2", "MODE_BIAS")
    net("SJ1", "3", "+3V3")

    two_pin("RB1", "2.4R", (43.18, 45.72), "CT1_P", "CT1_N")
    two_pin("R1", "100R", (63.50, 40.64), "CT1_P", "IIP1")
    two_pin("R2", "100R", (63.50, 50.80), "CT1_N", "IIN1")
    two_pin("C1", "330n", (83.82, 40.64), "IIP1", "GNDA", capacitor=True)
    two_pin("C2", "330n", (83.82, 50.80), "IIN1", "GNDA", capacitor=True)

    two_pin("RB2", "2.4R", (43.18, 71.12), "CT2_P", "CT2_N")
    two_pin("R3", "100R", (63.50, 66.04), "CT2_P", "IIP2")
    two_pin("R4", "100R", (63.50, 76.20), "CT2_N", "IIN2")
    two_pin("C3", "330n", (83.82, 66.04), "IIP2", "GNDA", capacitor=True)
    two_pin("C4", "330n", (83.82, 76.20), "IIN2", "GNDA", capacitor=True)

    two_pin("R5", "100k", (43.18, 106.68), "VAC_P", "VAC_P_MID")
    two_pin("R6", "100k", (58.42, 106.68), "VAC_P_MID", "VDIV_P")
    two_pin("R7", "2.49k", (73.66, 114.30), "VDIV_P", "GNDA")
    two_pin("R8", "100k", (43.18, 121.92), "VAC_N", "VAC_N_MID")
    two_pin("R9", "100k", (58.42, 121.92), "VAC_N_MID", "VDIV_N")
    two_pin("R10", "2.49k", (73.66, 129.54), "VDIV_N", "GNDA")
    two_pin("R11", "1k", (91.44, 106.68), "VDIV_P", "VIP1")
    two_pin("R12", "1k", (91.44, 121.92), "VDIV_N", "VIN1")
    two_pin("C5", "33n", (106.68, 111.76), "VIP1", "GNDA", capacitor=True)
    two_pin("C6", "33n", (106.68, 127.00), "VIN1", "GNDA", capacitor=True)

    add(
        "Connector_Generic:Conn_01x14",
        "J1",
        "BREADBOARD I/O",
        (226.06, 88.90),
        "Connector_PinHeader_2.54mm:PinHeader_1x14_P2.54mm_Vertical",
    )
    header_nets = {
        "1": "+3V3",
        "2": "DGND",
        "3": "VAC_P",
        "4": "VAC_N",
        "5": "CT1_P",
        "6": "CT1_N",
        "7": "CT2_P",
        "8": "CT2_N",
        "9": "SCS",
        "10": "SCL",
        "11": "MOSI_RXD",
        "12": "MISO_TXD",
        "13": "SYN",
        "14": "EN",
    }
    for pin, name in header_nets.items():
        net("J1", pin, name)

    for index, (reference, signal) in enumerate(
        (
            ("TP1", "INT1"),
            ("TP2", "INT2"),
            ("TP3", "LED1"),
            ("TP4", "LED2"),
            ("TP5", "CLKOUT_ZCR"),
        )
    ):
        add(
            "Connector_Generic:Conn_01x01",
            reference,
            signal,
            (203.20, 76.20 + index * 7.62),
            "TestPoint:TestPoint_Pad_D1.5mm",
        )
        net(reference, "1", signal)

    for index, signal in enumerate(("+3V3", "DGND", "GNDA", "GND_REF"), start=1):
        reference = f"#FLG0{index}"
        add("power:PWR_FLAG", reference, "PWR_FLAG", (190.50 + index * 7.62, 121.92))
        net(reference, "1", signal)

    schematic.add_text(
        "TWO CURRENT HEADER INPUTS: 100 A : 50 mA current-output CTs\n"
        "Each channel: 2.4 ohm burden = 120 mV RMS at 100 A; approx. 4.8 kHz LPF.",
        (25.40, 27.94),
        size=1.1,
        bold=True,
    )
    schematic.add_text(
        "VOLTAGE HEADER INPUT: isolated 9 VAC transformer secondary only\n"
        "200k/2.49k symmetric divider = approx. 111 mV RMS differential at 9 VAC.",
        (25.40, 91.44),
        size=1.1,
        bold=True,
    )
    schematic.add_text(
        "WARNING: NOT A CERTIFIED ISOLATION BARRIER.\n"
        "Never connect J1 directly to mains.",
        (25.40, 142.24),
        size=1.27,
        bold=True,
    )
    schematic.add_text(
        "STPM33 supports SPI or UART; I2C is not supported.\n"
        "SJ1 1-2 closed = SPI default. Cut 1-2 and bridge 2-3 for UART.",
        (157.48, 27.94),
        size=1.0,
    )

    apply_part_metadata(schematic)
    schematic.save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
