"""NOAA MarineCadastre historical AIS integration helpers.

Primary public source for the 2018 incident case:
https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/ais/aistrack/index-aistrack.html

The annual 2018 vessel-track archive is large (~3.23 GB), so it is intentionally
NOT committed to Git. The application accepts a locally clipped CSV export,
which keeps deployment lightweight while preserving an authoritative source.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

NOAA_AIS_2018_URL = (
    "https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/ais/aistrack/"
    "AISVesselTracks2018.zip"
)
NOAA_AIS_INDEX_URL = (
    "https://ocmgeodatastor1.blob.core.windows.net/marinecadastre/ais/aistrack/"
    "index-aistrack.html"
)


@dataclass(frozen=True)
class AISPoint:
    mmsi: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed_knots: float | None = None
    course: float | None = None
    vessel_name: str | None = None
    vessel_type: str | None = None


def _first(row: dict[str, str], *names: str) -> str | None:
    normalized = {str(k).strip().lower(): v for k, v in row.items()}
    for name in names:
        value = normalized.get(name.lower())
        if value not in (None, ""):
            return value
    return None


def _timestamp(value: str) -> datetime:
    raw = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(raw)
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def load_csv(path: str | Path) -> list[AISPoint]:
    """Load a clipped NOAA/MarineCadastre CSV into normalized AIS points."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    points: list[AISPoint] = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            mmsi = _first(row, "MMSI", "mmsi")
            lat = _first(row, "LAT", "Latitude", "latitude")
            lon = _first(row, "LON", "Longitude", "longitude")
            ts = _first(row, "BaseDateTime", "Timestamp", "timestamp", "TrackStartTime")
            if not all((mmsi, lat, lon, ts)):
                continue
            points.append(
                AISPoint(
                    mmsi=str(mmsi),
                    timestamp=_timestamp(str(ts)),
                    latitude=float(lat),
                    longitude=float(lon),
                    speed_knots=float(_first(row, "SOG", "Speed", "speed") or 0),
                    course=float(_first(row, "COG", "Course", "course") or 0),
                    vessel_name=_first(row, "VesselName", "Vessel Name", "name"),
                    vessel_type=_first(row, "VesselType", "Vessel Type", "type"),
                )
            )
    return sorted(points, key=lambda p: p.timestamp)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def filter_origin_window(
    points: list[AISPoint],
    origin_lat: float,
    origin_lon: float,
    origin_time: datetime,
    radius_km: float = 50.0,
    hours_before: int = 12,
    hours_after: int = 12,
) -> list[AISPoint]:
    """Keep AIS positions relevant to the reconstructed spill-origin window."""
    origin_time = origin_time.astimezone(timezone.utc) if origin_time.tzinfo else origin_time.replace(tzinfo=timezone.utc)
    return [
        point for point in points
        if abs((point.timestamp - origin_time).total_seconds()) <= hours_before * 3600
        or abs((point.timestamp - origin_time).total_seconds()) <= hours_after * 3600
        if haversine_km(point.latitude, point.longitude, origin_lat, origin_lon) <= radius_km
    ]


def group_tracks(points: list[AISPoint]) -> dict[str, list[AISPoint]]:
    tracks: dict[str, list[AISPoint]] = {}
    for point in points:
        tracks.setdefault(point.mmsi, []).append(point)
    for track in tracks.values():
        track.sort(key=lambda p: p.timestamp)
    return tracks
