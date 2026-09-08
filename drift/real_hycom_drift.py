"""Real-data drift runner using historical HYCOM forcing.

This complements the deterministic MVP drift engine. It fetches actual 2018
Gulf of Mexico current + wind forcing around the Sentinel-1 SP-001 scene and
uses those values for hourly advection. The network calls are intentionally
kept outside the web request path so the demo can cache the resulting JSON.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.data_sources.hycom_gulf import fetch_point_forcing

EARTH_METERS_PER_DEGREE = 111_320.0


def meters_to_latlon(dx_m: float, dy_m: float, latitude: float) -> tuple[float, float]:
    dlat = dy_m / EARTH_METERS_PER_DEGREE
    dlon = dx_m / (EARTH_METERS_PER_DEGREE * max(math.cos(math.radians(latitude)), 0.01))
    return dlat, dlon


def advect(lat: float, lon: float, east_ms: float, north_ms: float, hours: float) -> tuple[float, float]:
    dx = east_ms * hours * 3600.0
    dy = north_ms * hours * 3600.0
    dlat, dlon = meters_to_latlon(dx, dy, lat)
    return lat + dlat, lon + dlon


def run_real_hycom_drift(
    incident_id: str,
    observed_lat: float,
    observed_lon: float,
    observed_time: datetime,
    hours_back: int = 12,
    hours_forward: int = 12,
    wind_drift_factor: float = 0.02,
) -> dict:
    """Run backward and forward hourly drift with real HYCOM forcing."""
    observed_time = observed_time.astimezone(timezone.utc) if observed_time.tzinfo else observed_time.replace(tzinfo=timezone.utc)

    backward = [{"hour": 0, "latitude": observed_lat, "longitude": observed_lon}]
    lat, lon = observed_lat, observed_lon
    forcing_records = []

    for step in range(1, hours_back + 1):
        t = observed_time - timedelta(hours=step)
        forcing = fetch_point_forcing(lat, lon, t)
        east = forcing.current_east_ms + forcing.wind_east_ms * wind_drift_factor
        north = forcing.current_north_ms + forcing.wind_north_ms * wind_drift_factor
        lat, lon = advect(lat, lon, east, north, -1.0)
        backward.append({"hour": -step, "latitude": round(lat, 6), "longitude": round(lon, 6)})
        forcing_records.append({
            "timestamp": forcing.timestamp.isoformat(),
            "current_east_ms": forcing.current_east_ms,
            "current_north_ms": forcing.current_north_ms,
            "wind_east_ms": forcing.wind_east_ms,
            "wind_north_ms": forcing.wind_north_ms,
        })

    origin = backward[-1]

    forward = [{"hour": 0, "latitude": observed_lat, "longitude": observed_lon}]
    lat, lon = observed_lat, observed_lon
    for step in range(1, hours_forward + 1):
        t = observed_time + timedelta(hours=step)
        forcing = fetch_point_forcing(lat, lon, t)
        east = forcing.current_east_ms + forcing.wind_east_ms * wind_drift_factor
        north = forcing.current_north_ms + forcing.wind_north_ms * wind_drift_factor
        lat, lon = advect(lat, lon, east, north, 1.0)
        forward.append({"hour": step, "latitude": round(lat, 6), "longitude": round(lon, 6)})
        forcing_records.append({
            "timestamp": forcing.timestamp.isoformat(),
            "current_east_ms": forcing.current_east_ms,
            "current_north_ms": forcing.current_north_ms,
            "wind_east_ms": forcing.wind_east_ms,
            "wind_north_ms": forcing.wind_north_ms,
        })

    return {
        "incident_id": incident_id,
        "data_status": "REAL_HYCOM_HISTORICAL_FORCING",
        "source": {
            "provider": "HYCOM-TSIS",
            "dataset": "Gulf of Mexico 1/25° reanalysis",
            "year": 2018,
            "resolution": "1/25 degree",
            "variables": ["u", "v", "wnd_ewd", "wnd_nwd"],
        },
        "observed_spill": {
            "latitude": observed_lat,
            "longitude": observed_lon,
            "timestamp": observed_time.isoformat(),
        },
        "origin": {
            "latitude": origin["latitude"],
            "longitude": origin["longitude"],
            "method": "12-hour backward advection using hourly HYCOM forcing",
        },
        "backward_hindcast": backward,
        "forward_forecast": forward,
        "forcing_samples": forcing_records,
        "model": {
            "type": "Lagrangian surface advection",
            "wind_drift_factor": wind_drift_factor,
            "time_step_hours": 1,
        },
    }


if __name__ == "__main__":
    result = run_real_hycom_drift(
        incident_id="SP-001",
        observed_lat=28.9067285145,
        observed_lon=-89.0199159563,
        observed_time=datetime(2018, 9, 26, 12, 0, tzinfo=timezone.utc),
    )
    output = Path("data/processed/ai_predictions/SP-001_real_hycom_drift.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {output}")
