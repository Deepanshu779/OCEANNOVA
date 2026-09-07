import pandas as pd
from haversine import haversine, Unit

def reconstruct_trajectories(df: pd.DataFrame) -> dict:
    trajectories = {}
    for mmsi, group in df.groupby('mmsi'):
        trajectories[mmsi] = group.sort_values('timestamp').to_dict(orient='records')
    return trajectories

def find_closest_point(track: list, origin_lat: float, origin_lon: float) -> dict:
    best_pt = None
    min_dist = float('inf')
    
    for pt in track:
        dist = haversine((pt['lat'], pt['lon']), (origin_lat, origin_lon), unit=Unit.KILOMETERS)
        if dist < min_dist:
            min_dist = dist
            best_pt = {**pt, 'distance_km': dist}
            
    return best_pt