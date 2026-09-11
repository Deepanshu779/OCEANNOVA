import type { GeoJsonObject } from "geojson";

const PRODUCTION_API = "https://oceannova-api.onrender.com/api/v1";
const configuredApi = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "");

// A deployed Vercel build must never fall back to localhost or an accidentally
// stale environment variable. Local development can still override the API.
const API_BASE_URL = import.meta.env.PROD
  ? PRODUCTION_API
  : (configuredApi || "http://127.0.0.1:8000/api/v1");

export interface Coordinates { lat: number; lon: number; }
export interface Origin { latitude: number; longitude: number; uncertainty_km: number; method?: string | null; }
export interface DriftPoint { latitude: number; longitude: number; hours_from_detection: number; current_speed?: number | null; current_direction?: number | null; wind_speed?: number | null; wind_direction?: number | null; }
export interface Vessel { mmsi: string; vessel_name?: string | null; latitude?: number | null; longitude?: number | null; speed_knots?: number | null; course?: number | null; attribution_score: number; distance_km?: number | null; time_difference_hours?: number | null; proximity_score?: number | null; temporal_score?: number | null; trajectory_match_score?: number | null; behavioral_anomaly_score?: number | null; relevance?: string; }
export interface VesselTrackPoint { mmsi: string; timestamp_hours_from_origin: number; latitude: number; longitude: number; speed_knots?: number | null; course?: number | null; }
export interface SpillCharacterization { area_km2: number; perimeter_estimate_km?: number | null; compactness_estimate?: number | null; estimated_age_hours?: number | null; age_status: string; }
export interface TrafficSummary { total_vessels_considered: number; filtered_irrelevant: number; ranked_candidates: number; filtering_rule: string; }
export interface Investigation { spill_id: string; confidence: number; area_km2: number; centroid: Coordinates; characterization: SpillCharacterization; origin?: Origin | null; drift: DriftPoint[]; traffic: TrafficSummary; vessels: Vessel[]; vessel_tracks: VesselTrackPoint[]; }

export interface DatasetScene {
  scene_id: string;
  file: string;
  split: "train" | "test";
  has_image: boolean;
  has_mask: boolean;
  image_path: string;
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error(`OCEANNOVA API ${response.status}: ${path}`);
  return (await response.json()) as T;
}

export function getInvestigation(spillId: string): Promise<Investigation> {
  return request<Investigation>(`/radar/spills/${encodeURIComponent(spillId)}/investigation`);
}

export function getSpillGeoJSON(spillId: string): Promise<GeoJsonObject> {
  return request<GeoJsonObject>(`/radar/spills/${encodeURIComponent(spillId)}/geojson`);
}

export async function getDatasetScenes(): Promise<DatasetScene[]> {
  const data = await request<{ scenes: DatasetScene[] }>("/datasets");
  return data.scenes;
}
