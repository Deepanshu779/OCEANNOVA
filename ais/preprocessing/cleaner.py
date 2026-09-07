import pandas as pd
from datetime import datetime

def load_and_clean_ais(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Remove nulls and invalid coordinate ranges
    df = df.dropna(subset=['mmsi', 'lat', 'lon', 'timestamp'])
    df = df[(df['lat'].between(-90, 90)) & (df['lon'].between(-180, 180))]
    return df.sort_values(by=['mmsi', 'timestamp'])

def filter_spatio_temporal(
    df: pd.DataFrame, 
    min_lat: float, max_lat: float, 
    min_lon: float, max_lon: float, 
    start_time: str, end_time: str
) -> pd.DataFrame:
    t_start = pd.to_datetime(start_time)
    t_end = pd.to_datetime(end_time)
    
    mask = (
        df['lat'].between(min_lat, max_lat) &
        df['lon'].between(min_lon, max_lon) &
        df['timestamp'].between(t_start, t_end)
    )
    return df[mask].copy()