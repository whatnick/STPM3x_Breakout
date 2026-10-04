# STPM32_Breakout

KiCad 10 scaffold for the STMicroelectronics STPM32.

- Channels: 1 voltage + 1 current
- Footprint: `Package_DFN_QFN:VQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm`
- Board: 55 x 40 mm, 5.08 mm rounded corners, four M2 mounting holes
- Status: mechanical and library scaffold only; electrical design is pending

Place `STPM32` from the project-local `STPM3x` symbol library, then implement
the relevant blocks in `docs/design-requirements.md`. Do not connect hazardous
voltages directly to the board without a reviewed isolation and protection
design.
