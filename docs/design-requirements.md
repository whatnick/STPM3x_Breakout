# STPM3x breakout design requirements

## Authoritative source

- STMicroelectronics, `DS10272 Rev 14`, *STPM32, STPM33, STPM34 ASSP for
  metering applications with up to four independent 24-bit 2nd-order
  sigma-delta ADCs, 4 MHz OSF and 2 embedded PGLNA*.
- The source PDF is not committed. Download the current revision from the
  [STPM34 product page](https://www.st.com/en/data-converters/stpm34.html).

## Shared electrical blocks

- 2.95 V to 3.65 V supply; nominal 3.3 V.
- 1 uF between VCC and ground.
- 1 uF between VDDA and GNDA.
- 4.7 uF between VDDD and GNDD.
- 100 nF from each implemented VREF output to GND_REF.
- 16 MHz crystal or an external clock satisfying the datasheet limits.
- EN exposed with a defined pull state and reset access.
- Interface selection is explicit:
  - STPM32 supports SPI and UART; it does not support I2C.
  - SCS low at power-up: SPI.
  - SCS high at power-up: UART.
  - A three-pad selector biases SCS through a resistor rather than hard-strapping
    it, preserving normal SPI chip-select operation.
  - The manufactured default bridges DGND to the bias resistor for SPI; UART
    requires cutting that bridge and connecting the bias resistor to +3V3.
- SYN, LED1, LED2, INT1, available INT2, and CLKOUT/ZCR remain accessible.
- Digital interface signals use a grouped 2.54 mm development header or
  equivalent compact connector.

## Analog design gates

Do not copy divider or burden values without tying them to the intended sensor
and range. The datasheet example is informative rather than universal:

- Differential analog pins are limited to +/-300 mV.
- Current-channel PGA ranges are +/-300, +/-150, +/-75, and +/-37.5 mV.
- Example line-voltage divider ratios are 1:1650 for 230 V RMS and 1:830 for
  110 V RMS.
- Example sensor sensitivities are 0.15 mV/A for Rogowski, 2.4 mV/A for CT,
  and 0.3 mV/A for shunt sensing.
- The reference design uses 150 pF input capacitors and channel-specific
  resistor networks; values must be re-derived for the selected transducer.

Every analog path must remain readable as:

```text
field connector -> burden/divider/protection -> anti-alias network -> IC pin
```

Use connector-side suffixes such as `_J` and IC-side signal names such as
`VIP1`, `VIN1`, `IIP1`, and `IIN1`.

## Mechanical formats

The implemented STPM33 board and STPM34 reference scaffold use:

- 55 x 40 mm bench-board envelope.
- 5.08 mm rounded corners.
- Four M2 NPTH holes, 2.2 mm drill.
- Metering IC near the center.
- Analog field/sensor region on the left.
- Digital power/debug region on the right.
- Clock and reference support immediately adjacent to U1 when populated.
- Board identity on F.SilkS.
- URL, TAPR OHL notice, and `NOT ISOLATED` warning on B.SilkS.

The implemented STPM32 board uses the compact Whatnick breakout format:

- 38.2 x 28.04 mm rounded outline.
- One long-edge 1x12, 2.54 mm breadboard header.
- Analog inputs enter through header pins; no screw terminals or audio jacks.
- INT1, LED1, LED2, and CLKOUT/ZCR use underside test pads.
- Separate AGND and DGND copper pours join through the three-pad net tie.
- `NOT FOR DIRECT MAINS` and isolated-source warnings remain visible.

## Variant intent

### STPM32

- One voltage and one current channel.
- Smallest BOM and lowest current consumption.
- Implemented for a 100 A:50 mA current-output CT and isolated 9 VAC voltage
  transformer.
- 2.4 ohm differential burden gives 120 mV RMS at 100 A.
- Symmetric 200 kohm / 2.49 kohm dividers give approximately 111 mV RMS at
  9 VAC differential input.
- Current and voltage anti-alias filters are approximately 4.8 kHz.
- Target: compact single-phase metering and driver development.

### STPM33

- One voltage and two current channels.
- Implemented for two 100 A:50 mA CTs and one isolated 9 VAC transformer.
- Each CT uses a 2.4 ohm differential burden and approximately 4.8 kHz input
  filtering.
- The voltage channel uses symmetric 200 kohm / 2.49 kohm dividers and
  approximately 4.8 kHz filtering.
- A 1x14 development header exposes both analog inputs and the host interface.
- Five underside test pads expose INT1, INT2, LED1, LED2, and CLKOUT/ZCR.
- Target: phase/neutral monitoring, tamper experiments, or two current sensors
  sharing one voltage channel.

### STPM34

- Two voltage and two current channels.
- Target: dual-circuit, split-phase, or two-phase development.
- It is not a complete three-phase meter by itself.

## Validation gates

- Project-local symbols match the datasheet pin table.
- Final footprints match the QFN mechanical tables and recommended land
  patterns.
- ERC: zero errors.
- Placement DRC: zero new mechanical errors.
- Final DRC: zero errors and zero unconnected items.
- Purchasing fields are present on every sourced schematic symbol:
  `Manufacturer`, `MPN`, `Description`, `DigiKey`, and `Mouser`.
