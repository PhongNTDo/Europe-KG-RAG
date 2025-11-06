from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Optional

from .models import Country, GraphDataset, River


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"yes", "y", "true", "1"}


def _as_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> Optional[int]:
    float_value = _as_float(value)
    if float_value is None:
        return None
    return int(float_value)


def _clean_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


class DatabaseLoader:
    """Load graph-ready data from the local JSON database."""

    def __init__(self, base_path: str | Path = "data/database") -> None:
        self.base_path = Path(base_path)
        self.countries_path = self.base_path / "europe_countries.json"
        self.rivers_path = self.base_path / "europe_rivers.json"

    def load(self) -> GraphDataset:
        countries_payload = self._load_json(self.countries_path).get("countries", [])
        rivers_payload = self._load_json(self.rivers_path).get("rivers", [])
        return GraphDataset(
            countries=[self._build_country(item) for item in countries_payload],
            rivers=[self._build_river(item) for item in rivers_payload],
        )

    def _load_json(self, path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(f"Expected data file is missing: {path}")
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _build_country(self, payload: dict) -> Country:
        return Country(
            name=_clean_string(payload.get("name")),
            capital=_clean_string(payload.get("capital")),
            eu_member=_as_bool(payload.get("eu_member")),
            borders_with=self._normalize_string_list(payload.get("borders_with", [])),
        )

    def _build_river(self, payload: dict) -> River:
        countries = self._normalize_string_list(payload.get("countries", []))
        mouth = payload.get("mouth")
        if mouth is None:
            mouth = payload.get("mounth")  # historical typo in upstream data

        return River(
            name=_clean_string(payload.get("name")),
            length=_as_float(payload.get("length")),
            basin=_as_float(payload.get("basin")),
            flow=_as_float(payload.get("flow")),
            mouth=_clean_string(mouth),
            parent=_clean_string(payload.get("parent")),
            rank_of_length=_as_int(payload.get("rank_of_length")),
            rank_of_area=_as_int(payload.get("rank_of_area")),
            rank_of_flow=_as_int(payload.get("rank_of_flow")),
            countries=countries,
        )

    @staticmethod
    def _normalize_string_list(values: Any) -> list[str]:
        if not values:
            return []
        if isinstance(values, str):
            candidates: Iterable[str] = [values]
        elif isinstance(values, Iterable):
            candidates = values
        else:
            return []
        normalized: list[str] = []
        for candidate in candidates:
            text = str(candidate).strip()
            if text:
                normalized.append(text)
        return normalized
