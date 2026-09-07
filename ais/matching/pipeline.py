import json
import pandas as pd
from ais.preprocessing.cleaner import load_and_clean_ais, filter_spatio_temporal
from ais.trajectory.builder import reconstruct_trajectories
from ais.attribution.scorer import score_vessel

def run_attribution_pipeline(
    ais_csv_path: str,
    spill_id: str,
    origin_lat: float,
    origin_lon: float,
    spill_timestamp: str,
    bounding_box: tuple,
    time_window: tuple
) -> dict:
    df = load_and_clean_ais(ais_csv_path)
    min_lat, max_lat, min_lon, max_lon = bounding_box
    start_t, end_t = time_window
    
    filtered_df = filter_spatio_temporal(df, min_lat, max_lat, min_lon, max_lon, start_t, end_t)
    trajectories = reconstruct_trajectories(filtered_df)
    
    vessels = []
    spill_dt = pd.to_datetime(spill_timestamp)
    for mmsi, track in trajectories.items():
        vessel_eval = score_vessel(track, origin_lat, origin_lon, spill_dt)
        if vessel_eval and vessel_eval['score'] > 0:
            vessels.append(vessel_eval)

    # Rank descending by score
    vessels.sort(key=lambda x: x['score'], reverse=True)

    result = {
        "spill_id": spill_id,
        "vessels": vessels
    }
    return result

if __name__ == "__main__":
    # Test run
    output = run_attribution_pipeline(
        ais_csv_path="data/sample_ais.csv",
        spill_id="SP-001",
        origin_lat=18.92,
        origin_lon=72.83,
        spill_timestamp="2026-09-06 10:00:00",
        bounding_box=(18.0, 20.0, 72.0, 74.0),
        time_window=("2026-09-05 00:00:00", "2026-09-07 00:00:00")
    )
    print(json.dumps(output, indent=2))