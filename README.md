# STPM3x Breakout

KiCad 10 hardware scaffolding for three STMicroelectronics energy-metering
ASIC breakouts:

- **STPM32** - one voltage and one current channel, QFN24L 4 x 4 mm.
- **STPM33** - one voltage and two current channels, QFN32L 5 x 5 mm.
- **STPM34** - two voltage and two current channels, QFN32L 5 x 5 mm.

The projects follow the reusable workflows from
[`whatnick/whatnick-energy-monitor-skills`](https://github.com/whatnick/whatnick-energy-monitor-skills):
datasheet-first circuits, project-local metering symbols, separated analog and
digital regions, rounded bench-board mechanics, four M2 mounting holes, a
power netclass, and explicit ERC/DRC gates.

## Repository layout

```text
hardware/
  STPM32_Breakout/
  STPM33_Breakout/
  STPM34_Breakout/
symbols/
  STPM3x.kicad_sym
docs/
  design-requirements.md
  pin-map.md
scripts/
  generate_scaffold.py
```

Each project starts as a mechanically valid 55 x 40 mm bench breakout with
5.08 mm corner radii, four M2 NPTH mounting holes, the correct IC package,
analog/digital placement zones, and board markings. The schematics are left
electrically empty until the sensor topology and isolation policy are selected;
the verified device symbols are ready in the project-local symbol library.

## Generate the scaffold

Run with the KiCad 10 Python interpreter:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\scripts\generate_scaffold.py
```

## Validate

```powershell
$kicad = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

Get-ChildItem .\hardware -Directory | ForEach-Object {
    $name = $_.Name
    & $kicad sch erc --format json --output "$($_.FullName)\erc.json" "$($_.FullName)\$name.kicad_sch"
    & $kicad pcb drc --format json --output "$($_.FullName)\drc.json" "$($_.FullName)\$name.kicad_pcb"
}
```

## Design status

This repository is at **scaffold stage**. Before routing:

1. Select CT, shunt, or Rogowski sensing for each current channel.
2. Select isolated low-voltage sensing or a documented mains-rated front end.
3. Dimension dividers and burdens from the required measurement range.
4. Confirm exposed-pad treatment with ST package/application guidance.
5. Implement the datasheet decoupling, reference, clock, reset/enable, and
   SPI/UART support circuits.
6. Complete ERC, placement DRC, routing, final DRC, BOM sourcing, and 3D review.

These boards are development instruments, not certified energy meters. They
must not be connected to hazardous voltages without appropriately rated
isolation, protection, fusing, enclosure, and electrical-safety practices.

## License

Hardware design files are released under the TAPR Open Hardware License 1.0.

