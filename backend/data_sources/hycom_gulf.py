"""Live historical HYCOM Gulf of Mexico forcing adapter.

HYCOM publishes a 1/25-degree Gulf of Mexico reanalysis with hourly fields
for 2018. OCEANNOVA uses the NCSS point-subset service so only the small
space/time window around an incident is requested.

Source:
https://ncss.hycom.org/thredds/catalogs/GOMb0.04/reanalysis.html

This module deliberately has no third-party dependency; it uses urllib.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen


HYCOM_3Z_2018 = "https://ncss.hycom.org/thredds/ncss/grid/GOMb0.04/reanalysis/2018/3z"
HYCOM_2D_2018 = "https://ncss.hycom.org/thredds/ncss/grid/GOMb0.04/reanalysis/2018/2d"


@dataclass(frozen=True)
class HYCOMForcing:
    timestamp: datetime
    latitude: float
    longitude: float
    current_east_ms: float
    current_north_ms: float
    wind_east_ms: float
    wind_north_ms: float
    source: str = "HYCOM-TSIS Gulf of Mexico 1/25° reanalysis"


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _fetch_csv(base_url: str, variables: str, latitude: float, longitude: float, timestamp: datetime) -> list[dict[str, str]]:
    params = {
        "var": variables,
        "latitude": f"{latitude:.6f}",
        "longitude": f"{longitude:.6f}",
        "time": _utc(timestamp).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vertCoord": "0",
        "accept": "csv",
    }
    url = f"{base_url}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "OCEANNOVA/1.0"})
    with urlopen(request, timeout=90) as response:
        text = response.read().decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(text)))


def _number(row: dict[str, str], *names: str) -> float:
    lowered = {str(k).strip().lower(): v for k, v in row.items()}
    for name in names:
        if name.lower() in lowered and lowered[name.lower()] not in (None, ""):
            return float(lowered[name.lower()])
    raise KeyError(f"None of {names!r} found in HYCOM response columns {list(row)}")


def fetch_point_forcing(latitude: float, longitude: float, timestamp: datetime) -> HYCOMForcing:
    """Fetch real surface current and wind forcing at one historical point."""
    current_rows = _fetch_csv(HYCOM_3Z_2018, "u,v", latitude, longitude, timestamp)
    wind_rows = _fetch_csv(HYCOM_2D_2018, "wnd_ewd,wnd_nwd", latitude, longitude, timestamp)
    if not current_rows or not wind_rows:
        raise RuntimeError("HYCOM returned no forcing rows for the requested point/time")

    current = current_rows[0]
    wind = wind_rows[0]
    return HYCOMForcing(
        timestamp=_utc(timestamp),
        latitude=latitude,
        longitude=longitude,
        current_east_ms=_number(current, "u", "water_u"),
        current_north_ms=_number(current, "v", "water_v"),
        wind_east_ms=_number(wind, "wnd_ewd", "wind_east", "wind_u"),
        wind_north_ms=_number(wind, "wnd_nwd", "wind_north", "wind_v"),
    )


def fetch_series(latitude: float, longitude: float, start: datetime, hours: int, step_hours: int = 1) -> list[HYCOMForcing]:
    """Fetch an hourly/stepped forcing series for drift hindcast or forecast."""
    if hours < 0 or step_hours <= 0:
        raise ValueError("hours must be >= 0 and step_hours must be > 0")
    result: list[HYCOMForcing] = []
    current = _utc(start)
    for _ in range(hours // step_hours + 1):
        result.append(fetch_point_forcing(latitude, longitude, current))
        current = current.replace() + __import__("datetime").timedelta(hours=step_hours)
    return result
