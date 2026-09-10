import json
import pandas as pd
from ais.preprocessing.cleaner import load_and_clean_ais, filter_spatio_temporal
from ais.trajectory.builder import reconstruct_trajectories
from ais.attribution.scoring import haversine_km, proximity_score, temporal_score, trajectory_match_score, attribution_score


def run_attribution_pipeline(
    ais_csv_path: str,
    spill_id: str,
    origin_lat: float,
    origin_lon: float,
    spill_timestamp: str,
    bounding_box: tuple,
    time_window: tuple,
) -> dict:
    """Run the explainable AIS attribution pipeline using the canonical scorer."""
    df = load_and_clean_ais(ais_csv_path)
    min_lat, max_lat, min_lon, max_lon = bounding_box
    start_t, end_t = time_window
    filtered_df = filter_spatio_temporal(
        df, min_lat, max_lat, min_lon, max_lon, start_t, end_t
    )
    trajectories = reconstruct_trajectories(filtered_df)
    spill_dt = pd.to_datetime(spill_timestamp, utc=True)
    vessels = []

    for mmsi, track in trajectories.items():
        if not track:
            continue
        # Normalize the legacy trajectory objects into the canonical scorer input.
        closest = min(
            track,
            key=lambda pt: haversine_km(
                float(pt["lat"]), float(pt["lon"]), origin_lat, origin_lon
            ),
        )
        distance = haversine_km(
            float(closest["lat"]), float(closest["lon"]), origin_lat, origin_lon
        )
        timestamp = pd.to_datetime(closest["timestamp"], utc=True)
        delta_hours = abs((timestamp - spill_dt).total_seconds()) / 3600.0
        course = float(closest.get("cog", 0.0) or 0.0)
        expected_course = course
        proximity = proximity_score(distance)
        temporal = temporal_score(delta_hours)
        trajectory = trajectory_match_score(course, expected_course)
        score = attribution_score(proximity, temporal, trajectory, 0.0)
        vessels.append({
            "mmsi": str(mmsi),
            "name": closest.get("vessel_name") or f"Vessel-{mmsi}",
            "score": round(score * 100.0, 2),
            "evidence": {
                "proximity_score": proximity,
                "temporal_score": temporal,
                "trajectory_score": trajectory,
                "closest_distance_km": round(distance, 2),
                "closest_timestamp": timestamp.isoformat(),
            },
        })

    vessels.sort(key=lambda item: item["score"], reverse=True)
    return {"spill_id": spill_id, "vessels": vessels}


if __name__ == "__main__":
    output = run_attribution_pipeline(
        ais_csv_path="data/sample_ais.csv",
        spill_id="SP-001",
        origin_lat=18.92,
        origin_lon=72.83,
        spill_timestamp="2026-09-06 10:00:00",
        bounding_box=(18.0, 20.0, 72.0, 74.0),
        time_window=("2026-09-05 00:00:00", "2026-09-07 00:00:00"),
    )
    print(json.dumps(output, indent=2))
