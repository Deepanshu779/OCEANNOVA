const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://127.0.0.1:8000/api/v1";

export interface Coordinates {
  lat: number;
  lon: number;
}

export interface Origin {
  latitude: number;
  longitude: number;
  uncertainty_km: number;
  method?: string | null;
}

export interface DriftPoint {
  latitude: number;
  longitude: number;
  hours_from_detection: number;
  current_speed?: number | null;
  current_direction?: number | null;
  wind_speed?: number | null;
  wind_direction?: number | null;
}

export interface Vessel {
  mmsi: string;
  vessel_name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  speed_knots?: number | null;
  course?: number | null;
  attribution_score: number;
  distance_km?: number | null;
  time_difference_hours?: number | null;
  trajectory_match_score?: number | null;
  behavioral_anomaly_score?: number | null;
}

export interface Investigation {
  spill_id: string;
  confidence: number;
  area_km2: number;
  centroid: Coordinates;
  origin?: Origin | null;
  drift: DriftPoint[];
  vessels: Vessel[];
}

export async function getInvestigation(spillId: string): Promise<Investigation> {
  const response = await fetch(
    `${API_BASE_URL}/spills/${encodeURIComponent(spillId)}/investigation`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch investigation: ${response.status}`);
  }

  return (await response.json()) as Investigation;
}
