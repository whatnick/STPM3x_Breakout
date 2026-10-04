# STPM3x Energy Metering Breakouts

Open-hardware development boards for the STMicroelectronics STPM32, STPM33,
and STPM34 energy-metering ASIC family.

The STPM3x devices combine precision analog conversion with on-chip
calculation of voltage, current, power, energy, and power-quality events. They
support current transformers, shunts, and Rogowski coils, with SPI or UART
host communication and CRC-protected data transfers.

This repository develops a consistent breakout family around all three channel
configurations:

| Board | Measurement channels | Best fit |
|---|---|---|
| **STPM32 Breakout** | 1 voltage + 1 current | Single-phase meters, smart appliances, and compact sensor development |
| **STPM33 Breakout** | 1 voltage + 2 current | Phase/neutral monitoring, tamper detection, and dual-current experiments |
| **STPM34 Breakout** | 2 voltage + 2 current | Split-phase systems, two independent circuits, and two-phase monitoring |

The STPM34 is the most capable member of this family, but it is not a complete
three-phase meter by itself. Applications requiring three simultaneous voltage
and current phases are better served by devices such as the ADE9000 or
ATM90E36.

## Place in the Whatnick ecosystem

The Whatnick energy-monitoring ecosystem includes breakout boards and drivers
for several metering architectures:

- **ATM90E26** for established single-phase SPI metering.
- **ATM90E32/ATM90E36** for three-phase monitoring.
- **ADE7763 and ADE7816** for Analog Devices single- and multi-channel designs.
- **ADE9000** for advanced polyphase metering and power-quality work.
- **CS5464 and CS5490** for Cirrus Logic single-phase applications.
- **MCP39F511 and MCP39F521** for Microchip calculation-engine devices.
- **V9203 and V93xx** for additional polyphase and single-phase platforms.
- **STPM3x** for a scalable STMicroelectronics family using a common register
  model across single-, dual-current, and dual-channel applications.

The aim is not only to expose IC pins. Each breakout should provide a known
hardware platform for driver development, calibration tools, sensor-interface
experiments, waveform analysis, and comparison between metering ASIC families.

## Intended software ecosystem

The three boards are intended to share one transport-independent STPM3x driver
core with device-specific channel capabilities layered on top. Planned software
support includes:

- Register definitions and typed configuration helpers.
- SPI and UART transports.
- CRC generation and checking.
- RMS, power, energy, event, and status access.
- Calibration and register-dump tools.
- Arduino and Python/MicroPython-facing APIs.
- Examples for CT, shunt, and Rogowski-coil measurements.

Keeping a common API across STPM32, STPM33, and STPM34 will allow applications
to move between board variants without maintaining three unrelated drivers.

## Hardware philosophy

These boards are intended as accessible bench-development platforms:

- Clearly separated analog sensor and digital host interfaces.
- Exposed pulse, interrupt, synchronization, clock, and enable signals.
- Space for channel-specific burden, divider, protection, and filtering
  networks.
- 3.3 V host compatibility.
- Compact breadboard modules or larger bench boards according to channel count.
- Readable safety labels and accessible test points.
- Open KiCad 10 source and project-local STPM3x symbols.

The STPM32 variant now implements a complete compact front end for a
100 A:50 mA current-output CT and an isolated 9 VAC transformer secondary. It
uses a single 1x12 breadboard header, underside test pads, separate analog and
digital ground pours, and no field-wiring connectors. The STPM33 and STPM34
projects remain larger reference scaffolds until their sensor combinations are
selected.

## Repository contents

- [`hardware/STPM32_Breakout`](hardware/STPM32_Breakout) - single voltage and
  current channel.
- [`hardware/STPM33_Breakout`](hardware/STPM33_Breakout) - single voltage and
  dual current channels.
- [`hardware/STPM34_Breakout`](hardware/STPM34_Breakout) - dual voltage and
  current channels.
- [`symbols/STPM3x.kicad_sym`](symbols/STPM3x.kicad_sym) - project-local,
  datasheet-verified symbols.
- [`docs/pin-map.md`](docs/pin-map.md) - family pin and package comparison.
- [`docs/design-requirements.md`](docs/design-requirements.md) - shared
  electrical, mechanical, and safety requirements.

## Safety

These are development boards, not certified energy meters. They must not be
connected directly to hazardous voltages without correctly rated isolation,
protection, fusing, spacing, enclosure, and appropriate electrical-safety
practices.

## License

Hardware design files are released under the
[TAPR Open Hardware License 1.0](LICENSE).
