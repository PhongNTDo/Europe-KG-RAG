from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

Row = Dict[str, Optional[str]]

with open("data/database/entities/europe_countries.json") as f:
    data_countries = json.load(f)
country_names = data_countries['countries']
country_names = [country['name'].lower() for country in country_names]


def _read_csv_file(csv_path: Path) -> List[Row]:
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return []

        rows: List[Row] = []
        for row in reader:
            countries = [c.lower().strip() for c in row['Country'].split('/')]
            for country in countries:
                if country not in country_names:
                    print(country)
            if not row:
                continue
            if not any((value or "").strip() for value in row.values()):
                continue

            normalized = {
                key: (value.strip() if isinstance(value, str) else value)
                for key, value in row.items()
            }
            rows.append(normalized)

    return rows


def convert_mountains_folder_to_json(input_dir: Path, output_path: Path) -> None:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    mountains: List[Row] = []
    for csv_path in sorted(input_dir.glob("*.csv")):
        mountains.extend(_read_csv_file(csv_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump({"mountains": mountains}, fh, ensure_ascii=False, indent=2)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Concatenate mountain CSV files into a JSON list."
    )
    parser.add_argument(
        "--input-dir",
        default=Path("data/crawled_data/mountains"),
        type=Path,
        help="Directory containing the mountain CSV files.",
    )
    parser.add_argument(
        "--output",
        default=Path("data/crawled_data/mountains/list_of_european_ultra_prominent_peaks.json"),
        type=Path,
        help="Path to write the JSON output.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    convert_mountains_folder_to_json(args.input_dir, args.output)


if __name__ == "__main__":
    main()
