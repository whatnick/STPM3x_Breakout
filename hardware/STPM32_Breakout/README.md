# STPM32 breakout

Compact KiCad 10 development board for the single-voltage, single-current
STMicroelectronics STPM32 energy-metering ASIC.

## Implemented front end

- **Current input:** 100 A:50 mA current-output CT.
- **Burden:** 2.4 ohm differential, producing 120 mV RMS at 100 A.
- **Current filter:** 100 ohm series and 330 nF shunt on each differential leg,
  approximately 4.8 kHz.
- **Voltage input:** isolated 9 VAC transformer secondary.
- **Voltage divider:** 200 kohm / 2.49 kohm on each conductor, approximately
  81.3:1 differential scaling.
- **Voltage filter:** 1 kohm series and 33 nF shunt on each differential leg,
  approximately 4.8 kHz.
- **Clock:** 16 MHz crystal with 15 pF load capacitors.
- **Interface default:** SCS pulled low for SPI; drive SCS high before reset to
  select UART.

At 9 VAC differential input, the voltage channel receives approximately
111 mV RMS, or 157 mV peak. Both analog channels remain below the STPM32
maximum differential input of +/-300 mV at their stated full-scale inputs.

## Breadboard header

| Pin | Signal | Pin | Signal |
|---:|---|---:|---|
| 1 | +3V3 | 7 | SCS |
| 2 | DGND | 8 | SCL |
| 3 | VAC_P | 9 | MOSI/RXD |
| 4 | VAC_N | 10 | MISO/TXD |
| 5 | CT_P | 11 | SYN |
| 6 | CT_N | 12 | EN |

INT1, LED1, LED2, and CLKOUT/ZCR are available on underside test pads.

## Mechanical and validation status

- 38.2 x 28.04 mm rounded board.
- Single long-edge 1x12, 2.54 mm header.
- No screw terminals, audio jacks, or direct-mains connector.
- Routed two-layer PCB with separate AGND and DGND pours joined through the
  three-pad analog/reference/digital ground net tie.
- Production silkscreen uses 0.8 x 0.8 mm component and signal labels with
  0.2 mm stroke, project-local Whatnick and OSHW logos, and explicit revision
  and build-date marking.
- ERC: zero violations.
- DRC: zero violations and zero unconnected pads.

## Safety

The voltage input is for an isolated 9 VAC transformer secondary only. This
development board is not a certified isolation barrier and must never be
connected directly to mains.
