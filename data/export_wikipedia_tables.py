from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

import pandas as pd
import requests
from lxml import html

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[\W_]+", "_", text.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_")


def _extract_tables(html_content: str) -> List[Tuple[pd.DataFrame, str]]:
    """Extract tables and optional captions from raw HTML."""
    document = html.fromstring(html_content)
    tables: List[Tuple[pd.DataFrame, str]] = []
    for table_element in document.xpath("//table[.//tr]"):
        caption_nodes = table_element.xpath(".//caption")
        caption_text = caption_nodes[0].text_content().strip() if caption_nodes else ""

        table_html = html.tostring(table_element, encoding="unicode")
        try:
            dataframe = pd.read_html(table_html)[0]
        except (ValueError, ImportError):
            continue

        if dataframe.empty:
            continue

        tables.append((dataframe, caption_text))
    return tables


def _build_filename(base_slug: str, caption: str, index: int, used_names: Set[str]) -> str:
    caption_slug = _slugify(caption)[:60]
    candidates = [
        part for part in (base_slug, caption_slug, f"table_{index:02d}") if part
    ]
    filename = "_".join(candidates) or f"table_{index:02d}"

    unique_name = filename
    counter = 1
    while unique_name in used_names:
        unique_name = f"{filename}_{counter}"
        counter += 1
    return unique_name


def export_wikipedia_tables(url: str, output_dir: str = "data/wikipedia_tables") -> List[Path]:
    """
    Download all tables from a Wikipedia page and export them as CSV files.

    Returns a list of Paths to the generated CSV files.
    """
    response = requests.get(url, timeout=20, headers=DEFAULT_HEADERS)
    response.raise_for_status()

    tables = _extract_tables(response.text)
    if not tables:
        raise ValueError("No tables were found on the provided page.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    base_slug = _slugify(urlparse(url).path.rsplit("/", 1)[-1])
    exported_paths: List[Path] = []
    used_names: Set[str] = set()

    for index, (dataframe, caption) in enumerate(tables, start=1):
        filename = _build_filename(base_slug, caption, index, used_names)
        used_names.add(filename)

        csv_path = output_path / f"{filename}.csv"
        dataframe.to_csv(csv_path, index=False)
        exported_paths.append(csv_path)

    return exported_paths


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export Wikipedia tables to CSV files."
    )
    parser.add_argument("url", help="URL of the Wikipedia page to export.")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="data/wikipedia_tables",
        help="Directory where CSV files will be stored (created if missing).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        exported_paths = export_wikipedia_tables(args.url, args.output_dir)
    except Exception as exc:  # pragma: no cover - CLI surface for clarity
        raise SystemExit(f"Error: {exc}")

    for path in exported_paths:
        print(path)


if __name__ == "__main__":
    main()
