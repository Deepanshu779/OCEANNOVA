"""Historical AIS CSV ingestion utilities.

Accepts common AIS exports with MMSI, timestamp, latitude, longitude and
optional speed/course columns. This keeps the attribution engine independent
of a particular AIS provider.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class AISRecord:
    mmsi: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed_knots: float | None = None
    course: float | None = None


def _first(row: dict[str, str], *names: str) -> str | None:
    lowered = {key.strip().lower(): value for key, value in row.items()}
    for name in names:
        if name.lower() in lowered and lowered[name.lower()] not in (None, ""):
            return lowered[name.lower()]
    return None


def load_ais_csv(path: str | Path) -> list[AISRecord]:
    """Load and validate AIS records from a CSV export."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    records: list[AISRecord] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            mmsi = _first(row, "mmsi", "MMSI", "vessel_mmsi")
            timestamp = _first(row, "timestamp", "time", "datetime", "base_datetime")
            lat = _first(row, "latitude", "lat")
            lon = _first(row, "longitude", "lon", "lng")
            if not all((mmsi, timestamp, lat, lon)):
                continue
            dt = datetime.fromisoformat(timestamp.strip().replace("Z", "+00:00"))
            records.append(
                AISRecord(
                    mmsi=str(mmsi).strip(),
                    timestamp=dt,
                    latitude=float(lat),
                    longitude=float(lon),
                    speed_knots=float(_first(row, "speed_knots", "sog", "speed")) if _first(row, "speed_knots", "sog", "speed") else None,
                    course=float(_first(row, "course", "cog", "heading")) if _first(row, "course", "cog", "heading") else None,
                )
            )
    return sorted(records, key=lambda record: record.timestamp)


def group_tracks(records: list[AISRecord]) -> dict[str, list[AISRecord]]:
    """Group AIS records into vessel tracks."""
    tracks: dict[str, list[AISRecord]] = {}
    for record in records:
        tracks.setdefault(record.mmsi, []).append(record)
    return tracks
