# STPM34_Breakout

KiCad 10 scaffold for the STMicroelectronics STPM34.

- Channels: 2 voltage + 2 current
- Footprint: `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm`
- Board: 55 x 40 mm, 5.08 mm rounded corners, four M2 mounting holes
- Status: mechanical and library scaffold only; electrical design is pending

Place `STPM34` from the project-local `STPM3x` symbol library, then implement
the relevant blocks in `docs/design-requirements.md`. Do not connect hazardous
voltages directly to the board without a reviewed isolation and protection
design.
