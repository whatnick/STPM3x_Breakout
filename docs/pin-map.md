# STPM3x verified pin map

Source: STMicroelectronics DS10272 Rev 14, Figures 4-6 and Table 1.

## Shared pins

| Function | STPM34 | STPM33 | STPM32 |
|---|---:|---:|---:|
| CLKOUT/ZCR | 1 | 1 | 1 |
| CLKIN/XTAL2 | 2 | 2 | 2 |
| XTAL1 | 3 | 3 | 3 |
| LED1 | 4 | 4 | 4 |
| LED2 | 5 | 5 | 5 |
| INT1 | 6 | 6 | 6 |
| INT2 | 7 | 7 | - |
| EN | 8 | 8 | 7 |
| VIP1 | 9 | 9 | 8 |
| VIN1 | 10 | 10 | 9 |
| IIP1 | 11 | 11 | 10 |
| IIN1 | 12 | 12 | 11 |
| IIN2 | 13 | 13 | - |
| IIP2 | 14 | 14 | - |
| VIN2 | 15 | - | - |
| VIP2 | 16 | - | - |
| VREF1 | 17 | 17 | 12 |
| GND_REF | 18 | 18 | 13 |
| VREF2 | 19 | 19 | - |
| GNDA | 20 | 20 | 14 |
| VDDA | 21 | 21 | 15 |
| GND_REG | 22 | 22 | 16 |
| VCC | 23 | 23 | 17 |
| NC | 24 | 15, 16, 24, 25 | - |
| GNDD | 25, 26 | 26 | 18 |
| VDDD | 27 | 27 | 19 |
| SYN | 28 | 28 | 20 |
| SCS | 29 | 29 | 21 |
| SCL | 30 | 30 | 22 |
| MOSI/RXD | 31 | 31 | 23 |
| MISO/TXD | 32 | 32 | 24 |

## Package selection

| Device | Package | Datasheet exposed-pad size | Scaffold footprint |
|---|---|---:|---|
| STPM32 | QFN24L, 4 x 4 mm, 0.5 mm pitch | 2.45 x 2.45 mm typical | `VQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm` |
| STPM33 | QFN32L, 5 x 5 mm, 0.5 mm pitch | 3.45 x 3.45 mm typical | `QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm` |
| STPM34 | QFN32L, 5 x 5 mm, 0.5 mm pitch | 3.45 x 3.45 mm typical | `QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm` |

The datasheet pin table does not assign a numbered electrical function to the
package exposed pad. Its final net assignment remains an explicit design-review
item rather than being guessed in the symbols. Thermal-via geometry is also
deferred until that connection and the assembly process are confirmed.
