#!/usr/bin/env python3
"""Build the STPM32 breakout schematic with isolated voltage and CT inputs."""

from pathlib import Path

import kicad_sch_api as ksa

from stpm32_parts import apply_part_metadata


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_LIBRARY = ROOT / "symbols" / "STPM3x.kicad_sym"
OUTPUT = (
    ROOT
    / "hardware"
    / "STPM32_Breakout"
    / "STPM32_Breakout.kicad_sch"
)

R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"


def main() -> None:
    cache = ksa.get_symbol_cache()
    cache.add_library_path(SYMBOL_LIBRARY)

    schematic = ksa.create_schematic("STPM32_Breakout")
    schematic.set_title_block(
        title="STPM32 Energy Metering Breakout",
        rev="B",
        company="Whatnick",
        comments={
            1: "Isolated 9 VAC voltage input and 100 A:50 mA current-output CT",
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

    # Metering IC and all mandatory support circuitry.
    add(
        "STPM3x:STPM32",
        "U1",
        "STPM32",
        (140.97, 88.90),
        "Package_DFN_QFN:VQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm",
    )
    u1_nets = {
        "1": "CLKOUT_ZCR",
        "2": "XTAL2",
        "3": "XTAL1",
        "4": "LED1",
        "5": "LED2",
        "6": "INT1",
        "7": "EN",
        "8": "VIP1",
        "9": "VIN1",
        "10": "IIP1",
        "11": "IIN1",
        "12": "VREF1",
        "13": "GND_REF",
        "14": "AGND",
        "15": "VDDA",
        "16": "AGND",
        "17": "+3V3",
        "18": "DGND",
        "19": "VDDD",
        "20": "SYN",
        "21": "SCS",
        "22": "SCL",
        "23": "MOSI_RXD",
        "24": "MISO_TXD",
    }
    for pin, name in u1_nets.items():
        net("U1", pin, name)

    two_pin("C9", "1u", (172.72, 78.74), "+3V3", "DGND", capacitor=True, footprint=C0805)
    two_pin("C10", "1u", (172.72, 88.90), "VDDA", "AGND", capacitor=True, footprint=C0805)
    two_pin("C11", "4.7u", (172.72, 99.06), "VDDD", "DGND", capacitor=True, footprint=C0805)
    two_pin("C12", "100n", (160.02, 109.22), "VREF1", "GND_REF", capacitor=True)

    add(
        "Connector_Generic:Conn_01x03",
        "NT1",
        "ANALOG/DIGITAL STAR",
        (172.72, 109.22),
        "NetTie:NetTie-3_SMD_Pad0.5mm",
    )
    net("NT1", "1", "AGND")
    net("NT1", "2", "GND_REF")
    net("NT1", "3", "DGND")

    # 16 MHz crystal oscillator.
    add(
        "Device:Crystal",
        "Y1",
        "16MHz",
        (140.97, 55.88),
        "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
    )
    net("Y1", "1", "XTAL1")
    net("Y1", "2", "XTAL2")
    two_pin("C13", "15p", (132.08, 63.50), "XTAL1", "DGND", capacitor=True)
    two_pin("C14", "15p", (149.86, 63.50), "XTAL2", "DGND", capacitor=True)

    # Enable and interface-mode defaults: enabled and SPI unless reconfigured.
    two_pin("R11", "10k", (160.02, 55.88), "+3V3", "EN")
    add(
        "Switch:SW_Push",
        "SW1",
        "RESET",
        (172.72, 55.88),
        "Button_Switch_SMD:SW_SPST_CK_RS282G05A3",
    )
    net("SW1", "1", "EN")
    net("SW1", "2", "DGND")
    two_pin("R12", "10k", (185.42, 55.88), "SCS", "MODE_BIAS")
    add(
        "Connector_Generic:Conn_01x03",
        "SJ1",
        "SPI / UART",
        (185.42, 68.58),
        "Jumper:SolderJumper-3_P1.3mm_Bridged12_Pad1.0x1.5mm",
    )
    net("SJ1", "1", "DGND")
    net("SJ1", "2", "MODE_BIAS")
    net("SJ1", "3", "+3V3")

    # Current channel: header input, 2.4 ohm differential burden and LPF.
    two_pin("RB1", "2.4R", (55.88, 58.42), "CT_P", "CT_N")
    two_pin("R1", "100R", (76.20, 53.34), "CT_P", "IIP1")
    two_pin("R2", "100R", (76.20, 63.50), "CT_N", "IIN1")
    two_pin("C1", "330n", (96.52, 53.34), "IIP1", "AGND", capacitor=True)
    two_pin("C2", "330n", (96.52, 63.50), "IIN1", "AGND", capacitor=True)

    # Voltage channel: isolated 9 VAC source, symmetric 200k/2.49k divider and LPF.
    two_pin("R3", "100k", (55.88, 101.60), "VAC_P", "VAC_P_MID")
    two_pin("R4", "100k", (71.12, 101.60), "VAC_P_MID", "VDIV_P")
    two_pin("R5", "2.49k", (86.36, 109.22), "VDIV_P", "AGND")
    two_pin("R6", "100k", (55.88, 116.84), "VAC_N", "VAC_N_MID")
    two_pin("R7", "100k", (71.12, 116.84), "VAC_N_MID", "VDIV_N")
    two_pin("R8", "2.49k", (86.36, 124.46), "VDIV_N", "AGND")
    two_pin("R9", "1k", (104.14, 101.60), "VDIV_P", "VIP1")
    two_pin("R10", "1k", (104.14, 116.84), "VDIV_N", "VIN1")
    two_pin("C3", "33n", (119.38, 106.68), "VIP1", "AGND", capacitor=True)
    two_pin("C4", "33n", (119.38, 121.92), "VIN1", "AGND", capacitor=True)

    # Single breadboard I/O header. VDDD and VDDA remain local regulator outputs.
    add(
        "Connector_Generic:Conn_01x12",
        "J1",
        "BREADBOARD I/O",
        (213.36, 88.90),
        "Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Vertical",
    )
    header_nets = {
        "1": "+3V3",
        "2": "DGND",
        "3": "VAC_P",
        "4": "VAC_N",
        "5": "CT_P",
        "6": "CT_N",
        "7": "SCS",
        "8": "SCL",
        "9": "MOSI_RXD",
        "10": "MISO_TXD",
        "11": "SYN",
        "12": "EN",
    }
    for pin, name in header_nets.items():
        net("J1", pin, name)

    for index, (name, signal) in enumerate(
        (
            ("TP1", "INT1"),
            ("TP2", "LED1"),
            ("TP3", "LED2"),
            ("TP4", "CLKOUT_ZCR"),
        )
    ):
        add(
            "Connector_Generic:Conn_01x01",
            name,
            signal,
            (187.96, 78.74 + index * 7.62),
            "TestPoint:TestPoint_Pad_D1.5mm",
        )
        net(name, "1", signal)

    # Explicit power-source markers keep ERC meaningful.
    add("power:PWR_FLAG", "#FLG01", "PWR_FLAG", (195.58, 53.34))
    net("#FLG01", "1", "+3V3")
    add("power:PWR_FLAG", "#FLG02", "PWR_FLAG", (203.20, 53.34))
    net("#FLG02", "1", "DGND")
    add("power:PWR_FLAG", "#FLG03", "PWR_FLAG", (195.58, 63.50))
    net("#FLG03", "1", "AGND")
    add("power:PWR_FLAG", "#FLG04", "PWR_FLAG", (203.20, 63.50))
    net("#FLG04", "1", "GND_REF")

    # Readable design intent on the sheet.
    schematic.add_text(
        "CURRENT HEADER INPUT: 100 A : 50 mA current-output CT\n"
        "2.4 ohm burden = 120 mV RMS at 100 A; approximately 4.8 kHz LPF.",
        (30.48, 35.56),
        size=1.1,
        bold=True,
    )
    schematic.add_text(
        "VOLTAGE HEADER INPUT: isolated 9 VAC transformer secondary only\n"
        "200k/2.49k symmetric divider = approx. 111 mV RMS differential at 9 VAC.",
        (30.48, 86.36),
        size=1.1,
        bold=True,
    )
    schematic.add_text(
        "WARNING: NOT A CERTIFIED ISOLATION BARRIER.\n"
        "Never connect J1 directly to mains.",
        (30.48, 137.16),
        size=1.27,
        bold=True,
    )
    schematic.add_text(
        "STPM32 supports SPI or UART; I2C is not supported.\n"
        "SJ1 1-2 closed = SPI default. Cut 1-2 and bridge 2-3 for UART.",
        (147.32, 35.56),
        size=1.0,
    )

    apply_part_metadata(schematic)
    schematic.save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
