import numpy as np
from shapely.geometry import Polygon

def extract_geometric_features(polygon: Polygon, pixel_resolution_m: float = 10.0):
    """
    Extracts geometric properties from a Shapely Polygon.
    """
    # Check if coordinates are in lat/lon degrees (e.g. values between -180 and 180)
    bounds = polygon.bounds # (minx, miny, maxx, maxy)
    is_latlon = abs(bounds[0]) <= 180 and abs(bounds[1]) <= 90

    if is_latlon:
        # Approximate conversion: 1 degree ~ 111 km
        area_km2 = polygon.area * (111 ** 2)
        perimeter_km = polygon.length * 111
    else:
        # Projected in meters (e.g. UTM)
        area_km2 = polygon.area / 1e6
        perimeter_km = polygon.length / 1e3

    # Centroid
    centroid_lat = polygon.centroid.y
    centroid_lon = polygon.centroid.x

    # Compactness (Isoperimetric Quotient)
    compactness = (4 * np.pi * area_km2) / (perimeter_km ** 2) if perimeter_km > 0 else 0.0

    return {
        "area_km2": round(area_km2, 3),
        "perimeter_km": round(perimeter_km, 3),
        "compactness": round(compactness, 4),
        "centroid": {"lat": round(centroid_lat, 5), "lon": round(centroid_lon, 5)},
        "bbox": [round(c, 5) for c in bounds]
    }