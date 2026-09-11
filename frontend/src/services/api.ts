import type { GeoJsonObject } from "geojson";

const PRODUCTION_API = "https://oceannova-api.onrender.com/api/v1";
const GITHUB_DATA_ROOT = "https://raw.githubusercontent.com/Deepanshu779/OCEANNOVA/main/data/processed/all_scenes";
const GITHUB_MANIFEST_URL = `${GITHUB_DATA_ROOT}/manifest.json`;
const configuredApi = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "");

// Production uses Render first. If Render is asleep, unavailable, or missing
// repository-level data, the committed processed Radar_data artifacts remain
// available directly from the public repository as a deterministic fallback.
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

async function githubJson<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error(`Committed Radar_data artifact ${response.status}`);
  return (await response.json()) as T;
}

async function committedInvestigation(spillId: string): Promise<Investigation> {
  const data = await githubJson<any>(`${GITHUB_DATA_ROOT}/${encodeURIComponent(spillId)}/characterization.json`);
  const detection = data.detection ?? {};
  const centroid = data.centroid ?? detection.centroid ?? {};
  if (typeof centroid.latitude !== "number" || typeof centroid.longitude !== "number") {
    throw new Error(`Committed result ${spillId} has no centroid`);
  }

  return {
    spill_id: data.incident_id ?? spillId,
    confidence: Number(detection.mean_ai_confidence ?? 0),
    area_km2: Number(detection.area_km2 ?? 0),
    centroid: { lat: Number(centroid.latitude), lon: Number(centroid.longitude) },
    characterization: {
      area_km2: Number(detection.area_km2 ?? 0),
      perimeter_estimate_km: detection.perimeter_km ?? null,
      compactness_estimate: detection.compactness ?? null,
      estimated_age_hours: null,
      age_status: "not_available_from_single_radar_scene",
    },
    origin: null,
    drift: [],
    traffic: {
      total_vessels_considered: 0,
      filtered_irrelevant: 0,
      ranked_candidates: 0,
      filtering_rule: "Historical AIS not loaded",
    },
    vessels: [],
    vessel_tracks: [],
  };
}

export async function getInvestigation(spillId: string): Promise<Investigation> {
  try {
    return await request<Investigation>(`/radar/spills/${encodeURIComponent(spillId)}/investigation`);
  } catch (error) {
    console.warn(`OCEANNOVA API unavailable for ${spillId}; loading committed Radar_data result.`, error);
    return committedInvestigation(spillId);
  }
}

export async function getSpillGeoJSON(spillId: string): Promise<GeoJsonObject> {
  try {
    return await request<GeoJsonObject>(`/radar/spills/${encodeURIComponent(spillId)}/geojson`);
  } catch (error) {
    console.warn(`OCEANNOVA API unavailable for ${spillId}; loading committed GeoJSON.`, error);
    return githubJson<GeoJsonObject>(`${GITHUB_DATA_ROOT}/${encodeURIComponent(spillId)}/spill.geojson`);
  }
}

export async function getDatasetScenes(): Promise<DatasetScene[]> {
  try {
    const data = await request<{ scenes: DatasetScene[] }>("/datasets");
    return data.scenes;
  } catch (error) {
    console.warn("OCEANNOVA dataset API unavailable; loading committed Radar_data manifest.", error);
    const manifest = await githubJson<any>(GITHUB_MANIFEST_URL);
    return (manifest.scenes ?? []).map((item: any) => ({
      scene_id: item.scene_id,
      file: String(item.source?.image ?? "").split(/[\\/]/).pop() ?? "",
      split: item.split,
      has_image: true,
      has_mask: Boolean(item.source?.ground_truth),
      image_path: String(item.source?.image ?? "").replaceAll("\\", "/"),
    }));
  }
}
