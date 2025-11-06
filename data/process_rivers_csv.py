from __future__ import annotations

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import List, Optional, Tuple


PREPOSITION_PATTERN = re.compile(
    r"\b(near|at|in|into|onto|to|on|by|via|off|within|between)\b",
    flags=re.IGNORECASE,
)


def _clean_text(value: str) -> str:
    cleaned = value.replace("\xa0", " ").strip()
    cleaned = re.sub(r"\[[^\]]*]", "", cleaned)  # drop reference-style brackets
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _clean_name(value: str) -> str:
    text = _clean_text(value)
    text = text.replace("←", "<-")
    return text


def _parse_numeric(value: str) -> Optional[float | int | str]:
    text = _clean_text(value)
    if not text or text in {"-", "?", "—"}:
        return None

    normalized = text.replace(",", "").replace("~", "").replace("−", "-")
    try:
        if normalized.count("-") > 1:
            raise ValueError
        if "." in normalized:
            return float(normalized)
        return int(normalized)
    except ValueError:
        match = re.search(r"\d+(?:\.\d+)?", normalized)
        if match:
            number = match.group()
            return float(number) if "." in number else int(number)
        return text


def _parse_rank(value: str) -> Optional[int]:
    text = _clean_text(value)
    if not text or text in {"-", "?", "—"}:
        return None
    match = re.match(r"\d+", text)
    return int(match.group()) if match else None


def _parse_countries(value: str) -> Optional[str]:
    text = _clean_text(value)
    if not text:
        return None

    text = text.replace(";", ",")
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        return None
    return ", ".join(parts)


def _split_mouth(value: str) -> Tuple[Optional[str], Optional[str]]:
    text = _clean_text(value)
    if not text:
        return None, None

    match = PREPOSITION_PATTERN.search(text)
    if not match:
        return text if text else None, None

    parent = text[: match.start()].strip(" ,;")
    area = text[match.end():].strip(" ,;")
    return (parent or None, area or None)


def _determine_depth(levels: List[str]) -> Optional[int]:
    for idx, val in enumerate(levels):
        if val:
            return idx
    return None


def _extract_name(levels: List[str]) -> Optional[str]:
    for val in reversed(levels):
        if val:
            return val
    return None


def convert_rivers_csv_to_json(
    csv_path: Path,
    output_path: Path,
) -> None:
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)

        # Skip multi-row header
        for _ in range(3):
            next(reader, None)

        rivers = []
        stack: List[Optional[str]] = [None] * 5  # track hierarchy depth

        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue

            levels_raw = [_clean_name(value) for value in row[3:8]]
            name = _extract_name(levels_raw)
            if not name:
                continue

            depth = _determine_depth(levels_raw)
            if depth is None:
                continue

            stack[depth] = name
            for idx in range(depth + 1, len(stack)):
                stack[idx] = None

            mouth_parent, area = _split_mouth(row[11])
            if depth > 0:
                parent = stack[depth - 1] or mouth_parent
            else:
                parent = mouth_parent

            river_entry = {
                "name": name,
                "rank_of_length": _parse_rank(row[0]),
                "rank_of_area": _parse_rank(row[1]),
                "rank_of_flow": _parse_rank(row[2]),
                "length": _parse_numeric(row[8]),
                "basin": _parse_numeric(row[9]),
                "flow": _parse_numeric(row[10]),
                "mounth": area,
                "parent": parent,
                "countries": _parse_countries(row[12]),
            }

            rivers.append(river_entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump({"rivers": rivers}, fh, ensure_ascii=False, indent=2)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert the exported List of rivers of Europe CSV into structured JSON."
    )
    parser.add_argument(
        "--input",
        default="data/crawled_data/rivers/list_of_rivers_of_europe.csv",
        type=Path,
        help="Path to the CSV file exported from Wikipedia.",
    )
    parser.add_argument(
        "--output",
        default="data/crawled_data/rivers/list_of_rivers_of_europe.json",
        type=Path,
        help="Path to write the JSON output.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    convert_rivers_csv_to_json(args.input, args.output)


if __name__ == "__main__":
    main()
