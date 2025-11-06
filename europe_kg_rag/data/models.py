from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True)
class Country:
    name: str
    capital: str
    eu_member: bool
    borders_with: List[str] = field(default_factory=list)


@dataclass(slots=True)
class River:
    name: str
    length: Optional[float] = None
    basin: Optional[float] = None
    flow: Optional[float] = None
    mouth: Optional[str] = None
    parent: Optional[str] = None
    rank_of_length: Optional[int] = None
    rank_of_area: Optional[int] = None
    rank_of_flow: Optional[int] = None
    countries: List[str] = field(default_factory=list)


@dataclass(slots=True)
class GraphDataset:
    countries: List[Country] = field(default_factory=list)
    rivers: List[River] = field(default_factory=list)
