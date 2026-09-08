"""Load ocean current and wind forcing for the drift engine.

The loader accepts CSV or JSON so the prototype can be connected to a real
Copernicus Marine/NOAA export without changing the drift algorithm.
Expected fields: timestamp, latitude, longitude, current_east_ms,
current_north_ms, wind_east_ms, wind_north_ms.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class OceanForcing:
    timestamp: datetime
    latitude: float
    longitude: float
    current_east_ms: float
    current_north_ms: float
    wind_east_ms: float
    wind_north_ms: float


def _dt(value: str) -> datetime:
    value = value.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def load_forcing(path: str | Path) -> list[OceanForcing]:
    """Load forcing records from .csv or .json, sorted by timestamp."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)

    if source.suffix.lower() == ".csv":
        with source.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    elif source.suffix.lower() == ".json":
        with source.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        rows = payload.get("records", payload) if isinstance(payload, (dict, list)) else []
    else:
        raise ValueError("Forcing file must be CSV or JSON")

    required = {
        "timestamp", "latitude", "longitude",
        "current_east_ms", "current_north_ms",
        "wind_east_ms", "wind_north_ms",
    }
    result: list[OceanForcing] = []
    for row in rows:
        missing = required - set(row)
        if missing:
            raise ValueError(f"Missing forcing fields: {sorted(missing)}")
        result.append(
            OceanForcing(
                timestamp=_dt(str(row["timestamp"])),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                current_east_ms=float(row["current_east_ms"]),
                current_north_ms=float(row["current_north_ms"]),
                wind_east_ms=float(row["wind_east_ms"]),
                wind_north_ms=float(row["wind_north_ms"]),
            )
        )
    return sorted(result, key=lambda item: item.timestamp)


def nearest_forcing(records: list[OceanForcing], latitude: float, longitude: float, timestamp: datetime) -> OceanForcing:
    """Select the nearest-in-time/space forcing record."""
    if not records:
        raise ValueError("No ocean forcing records available")
    return min(
        records,
        key=lambda item: abs((item.timestamp - timestamp).total_seconds())
        + 3600.0 * ((item.latitude - latitude) ** 2 + (item.longitude - longitude) ** 2) ** 0.5,
    )
