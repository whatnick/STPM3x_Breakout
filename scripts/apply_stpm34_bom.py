#!/usr/bin/env python3
"""Apply STPM34 sourcing metadata without reformatting the KiCad schematic."""

import re
from pathlib import Path

from stpm34_parts import NON_BOM_REFERENCES, PARTS, write_elecrow_bom


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "hardware" / "STPM34_Breakout"
SCHEMATIC_PATH = PROJECT / "STPM34_Breakout.kicad_sch"
BOM_PATH = PROJECT / "manufacturing" / "STPM34_Breakout_Elecrow_BOM.csv"
MANAGED_FIELDS = (
    "Manufacturer",
    "MPN",
    "LCSC",
    "Package",
    "Assembly",
    "Purchase URL",
    "DigiKey",
    "Mouser",
    "Notes",
)


def balanced_end(text: str, start: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        character = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            continue
        if character == '"':
            quoted = True
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    raise RuntimeError(f"Unbalanced S-expression beginning at byte {start}")


def property_span(symbol: str, name: str) -> tuple[int, int] | None:
    marker = f'\n\t\t(property "{name}" '
    start = symbol.find(marker)
    if start < 0:
        return None
    expression_start = start + 3
    return start, balanced_end(symbol, expression_start)


def quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def property_expression(name: str, value: str, x: str, y: str) -> str:
    return (
        f'\n\t\t(property "{quote(name)}" "{quote(value)}"\n'
        f"\t\t\t(at {x} {y} 0)\n"
        "\t\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n"
        "\t\t\t\t(font\n"
        "\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n"
        "\t\t\t)\n"
        "\t\t)"
    )


def set_description(symbol: str, description: str) -> str:
    span = property_span(symbol, "Description")
    if span is None:
        raise RuntimeError("Symbol lacks the standard Description property")
    start, end = span
    block = symbol[start:end]
    block = re.sub(
        r'(\(property "Description" )"(?:\\.|[^"])*"',
        rf'\1"{quote(description)}"',
        block,
        count=1,
    )
    return symbol[:start] + block + symbol[end:]


def apply_properties(symbol: str, properties: dict[str, str]) -> str:
    position = re.search(r"\n\t\t\(at ([^ ]+) ([^ )]+)", symbol)
    if position is None:
        raise RuntimeError("Symbol lacks a position")
    x, y = position.groups()

    for name in MANAGED_FIELDS:
        span = property_span(symbol, name)
        if span is not None:
            start, end = span
            symbol = symbol[:start] + symbol[end:]

    symbol = set_description(symbol, properties["Description"])
    insertion_candidates = [
        offset
        for offset in (
            symbol.find("\n\t\t(pin "),
            symbol.find("\n\t\t(instances"),
        )
        if offset >= 0
    ]
    if not insertion_candidates:
        raise RuntimeError("Unable to locate property insertion point")
    insertion = min(insertion_candidates)
    custom = "".join(
        property_expression(name, value, x, y)
        for name, value in properties.items()
        if name != "Description"
    )
    return symbol[:insertion] + custom + symbol[insertion:]


def update_schematic(text: str) -> str:
    selections = {
        reference: part
        for part in PARTS
        for reference in part.references
    }
    non_bom = set(NON_BOM_REFERENCES)
    found: set[str] = set()
    physical_bom: set[str] = set()

    spans: list[tuple[int, int]] = []
    offset = 0
    marker = "\n\t(symbol\n"
    while True:
        marker_start = text.find(marker, offset)
        if marker_start < 0:
            break
        start = marker_start + 2
        end = balanced_end(text, start)
        spans.append((start, end))
        offset = end

    for start, end in reversed(spans):
        symbol = text[start:end]
        reference_match = re.search(
            r'\n\t\t\(property "Reference" "([^"]+)"', symbol
        )
        footprint_match = re.search(
            r'\n\t\t\(property "Footprint" "([^"]*)"', symbol
        )
        if reference_match is None or footprint_match is None:
            continue
        reference = reference_match.group(1)
        footprint = footprint_match.group(1)

        if reference in selections:
            part = selections[reference]
            value_match = re.search(r'\n\t\t\(property "Value" "([^"]*)"', symbol)
            if value_match is None or value_match.group(1) != part.value:
                actual = value_match.group(1) if value_match else "<missing>"
                raise RuntimeError(
                    f"{reference} value is {actual!r}, expected {part.value!r}"
                )
            if footprint != part.footprint:
                raise RuntimeError(
                    f"{reference} footprint is {footprint!r}, "
                    f"expected {part.footprint!r}"
                )
            symbol = symbol.replace("\n\t\t(in_bom no)", "\n\t\t(in_bom yes)", 1)
            symbol = apply_properties(symbol, part.schematic_properties)
            found.add(reference)
            physical_bom.add(reference)
        elif reference in non_bom:
            symbol = symbol.replace("\n\t\t(in_bom yes)", "\n\t\t(in_bom no)", 1)
            found.add(reference)
        elif footprint and "\n\t\t(in_bom yes)" in symbol:
            physical_bom.add(reference)

        text = text[:start] + symbol + text[end:]

    expected = set(selections) | non_bom
    missing = sorted(expected - found)
    if missing:
        raise RuntimeError(f"Schematic is missing expected references: {', '.join(missing)}")
    uncovered = sorted(physical_bom - set(selections))
    if uncovered:
        raise RuntimeError(f"Physical BOM items lack selections: {', '.join(uncovered)}")
    return text


def main() -> None:
    source = SCHEMATIC_PATH.read_bytes()
    newline = "\r\n" if b"\r\n" in source else "\n"
    original = source.decode("utf-8").replace("\r\n", "\n")
    updated = update_schematic(original)
    SCHEMATIC_PATH.write_bytes(updated.replace("\n", newline).encode("utf-8"))
    write_elecrow_bom(BOM_PATH)
    print(f"Updated {SCHEMATIC_PATH}")
    print(f"Wrote {BOM_PATH}")


if __name__ == "__main__":
    main()
