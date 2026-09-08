import {
  Circle,
  GeoJSON,
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect, useState } from "react";
import type { GeoJsonObject } from "geojson";
import type { Investigation, Vessel } from "../services/api";

interface MapViewProps {
  investigation: Investigation;
  selectedVessel?: Vessel | null;
}

delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const vesselIcon = L.divIcon({ className: "vessel-marker", html: "🚢", iconSize: [32, 32], iconAnchor: [16, 16] });
const spillIcon = L.divIcon({ className: "spill-marker", html: `<div class="spill-marker-inner"></div>`, iconSize: [30, 30], iconAnchor: [15, 15] });
const originIcon = L.divIcon({ className: "origin-marker", html: `<div class="origin-marker-inner"></div>`, iconSize: [28, 28], iconAnchor: [14, 14] });
const selectedVesselIcon = L.divIcon({ className: "selected-vessel-marker", html: `<div class="selected-vessel-inner">🚢</div>`, iconSize: [42, 42], iconAnchor: [21, 21] });

function IncidentOverview({ investigation }: { investigation: Investigation }) {
  const map = useMap();
  useEffect(() => {
    const points: [number, number][] = [[investigation.centroid.lat, investigation.centroid.lon]];
    if (investigation.origin) points.push([investigation.origin.latitude, investigation.origin.longitude]);
    investigation.drift.forEach((p) => points.push([p.latitude, p.longitude]));
    investigation.vessels.forEach((v) => {
      if (v.latitude != null && v.longitude != null) points.push([v.latitude, v.longitude]);
    });
    if (points.length > 1) {
      map.fitBounds(L.latLngBounds(points), { padding: [40, 40], maxZoom: 8, animate: false });
    }
  }, [map, investigation]);
  return null;
}

function FocusInvestigationButton({ investigation }: { investigation: Investigation }) {
  const map = useMap();
  const focusInvestigation = () => {
    const points: [number, number][] = [[investigation.centroid.lat, investigation.centroid.lon]];
    if (investigation.origin) points.push([investigation.origin.latitude, investigation.origin.longitude]);
    investigation.drift.forEach((p) => points.push([p.latitude, p.longitude]));
    investigation.vessels.forEach((v) => {
      if (v.latitude != null && v.longitude != null) points.push([v.latitude, v.longitude]);
    });
    map.fitBounds(L.latLngBounds(points), { padding: [60, 60], maxZoom: 10, animate: true });
  };
  return <button type="button" className="map-action-button" onClick={focusInvestigation}>Focus Investigation</button>;
}

function FocusSelectedVessel({ vessel }: { vessel?: Vessel | null }) {
  const map = useMap();
  useEffect(() => {
    if (vessel?.latitude != null && vessel.longitude != null) {
      map.flyTo([vessel.latitude, vessel.longitude], Math.max(map.getZoom(), 9), { duration: 0.7 });
    }
  }, [map, vessel]);
  return null;
}

export default function MapView({ investigation, selectedVessel }: MapViewProps) {
  const [spillGeoJson, setSpillGeoJson] = useState<GeoJsonObject | null>(null);

  useEffect(() => {
    fetch("/data/SP-001_spill.geojson")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to load AI spill footprint");
        return response.json();
      })
      .then((data) => setSpillGeoJson(data))
      .catch((error) => console.error("AI spill footprint:", error));
  }, []);

  const spillPosition: [number, number] = [investigation.centroid.lat, investigation.centroid.lon];
  const originPosition: [number, number] | null = investigation.origin
    ? [investigation.origin.latitude, investigation.origin.longitude]
    : null;
  const driftPath: [number, number][] = investigation.drift.map((point) => [point.latitude, point.longitude]);
  const topVessel = investigation.vessels[0];

  const tracksByVessel = investigation.vessel_tracks.reduce<Record<string, [number, number][]>>((groups, point) => {
    groups[point.mmsi] ??= [];
    groups[point.mmsi].push([point.latitude, point.longitude]);
    return groups;
  }, {});

  const driftDirection = driftPath.length >= 2
    ? driftPath[driftPath.length - 1]
    : null;

  return (
    <MapContainer center={[28.9, -89.0]} zoom={7} scrollWheelZoom style={{ height: "100%", width: "100%" }}>
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <IncidentOverview investigation={investigation} />
      <FocusSelectedVessel vessel={selectedVessel} />
      <FocusInvestigationButton investigation={investigation} />

      {spillGeoJson && (
        <GeoJSON
          data={spillGeoJson}
          style={() => ({
            color: "#ef4444",
            weight: 2,
            opacity: 0.95,
            fillColor: "#ef4444",
            fillOpacity: 0.24,
          })}
        >
          <Popup>
            <strong>AI-Detected Spill Footprint</strong><br />
            Source: Sentinel-1 SAR<br />
            Method: U-Net + radiometric validation<br />
            Area: {investigation.area_km2} km²<br />
            Mean AI confidence: {(investigation.confidence * 100).toFixed(1)}%
          </Popup>
        </GeoJSON>
      )}

      <div className="map-overview-label">
        GULF OF MEXICO • REAL SENTINEL-1 TEST SCENE
      </div>

      <div className="map-hero-card">
        <div className="map-hero-kicker">AI INVESTIGATION</div>
        <strong>{investigation.spill_id} • {investigation.area_km2} km²</strong>
        <span>Real SAR detection → prototype trace → AIS ranking</span>
      </div>

      <div className="map-legend">
        <div className="legend-title">MAP LEGEND</div>
        <div><span className="legend-footprint" /> AI-detected spill footprint</div>
        <div><span className="legend-dot legend-origin" /> Probable origin</div>
        <div><span className="legend-line" /> Prototype oil drift</div>
        <div><span className="legend-track" /> Representative AIS track</div>
        <div><span className="legend-ship">🚢</span> Ranked AIS candidate</div>
      </div>

      <div className="map-status-card">
        <strong>● INVESTIGATION ACTIVE</strong>
        <span>DETECT → TRACE → ATTRIBUTE</span>
      </div>

      <Marker position={spillPosition} icon={spillIcon}>
        <Popup>
          <strong>{investigation.spill_id}</strong><br />
          AI-validated oil-spill candidate<br />
          Confidence: {(investigation.confidence * 100).toFixed(0)}%<br />
          Area: {investigation.area_km2} km²<br />
          Age estimate: {investigation.characterization.estimated_age_hours != null ? `${investigation.characterization.estimated_age_hours} h` : "Not available"}
        </Popup>
      </Marker>

      {originPosition && (
        <>
          <Circle center={originPosition} radius={investigation.origin!.uncertainty_km * 1000} pathOptions={{ fillOpacity: 0.12, weight: 2, dashArray: "7 6" }} />
          <Marker position={originPosition} icon={originIcon}>
            <Popup>
              <strong>Probable Spill Origin</strong><br />
              Uncertainty: ±{investigation.origin!.uncertainty_km} km<br />
              Method: {investigation.origin!.method ?? "Unknown"}
            </Popup>
          </Marker>
        </>
      )}

      {driftPath.length > 1 && (
        <Polyline positions={driftPath} pathOptions={{ weight: 4, opacity: 0.9 }}>
          <Popup>Prototype backward hindcast + forward forecast drift path</Popup>
        </Polyline>
      )}

      {driftDirection && (
        <Marker position={driftDirection} icon={L.divIcon({ className: "drift-end-marker", html: "➤", iconSize: [24, 24], iconAnchor: [12, 12] })} interactive={false} />
      )}

      {Object.entries(tracksByVessel).map(([mmsi, points]) => (
        <Polyline key={`track-${mmsi}`} positions={points} pathOptions={{ weight: 2, dashArray: "6 7", opacity: 0.65 }}>
          <Popup>Representative AIS trajectory • {mmsi}</Popup>
        </Polyline>
      ))}

      {investigation.vessels.map((vessel) => {
        if (vessel.latitude == null || vessel.longitude == null) return null;
        const isSelected = selectedVessel?.mmsi === vessel.mmsi;
        const isTop = topVessel?.mmsi === vessel.mmsi;
        return (
          <Marker key={vessel.mmsi} position={[vessel.latitude, vessel.longitude]} icon={isSelected || isTop ? selectedVesselIcon : vesselIcon}>
            <Popup>
              <strong>{vessel.vessel_name ?? "Unknown Vessel"}</strong><br />
              {isTop ? "#1 ranked AIS candidate" : "AIS candidate"} • Representative data<br />
              MMSI: {vessel.mmsi}<br />
              Attribution Score: {(vessel.attribution_score * 100).toFixed(0)}%<br />
              Proximity: {vessel.proximity_score != null ? `${(vessel.proximity_score * 100).toFixed(0)}%` : "N/A"}<br />
              Temporal: {vessel.temporal_score != null ? `${(vessel.temporal_score * 100).toFixed(0)}%` : "N/A"}<br />
              Trajectory Match: {vessel.trajectory_match_score != null ? `${(vessel.trajectory_match_score * 100).toFixed(0)}%` : "N/A"}<br />
              Behaviour: {vessel.behavioral_anomaly_score != null ? `${(vessel.behavioral_anomaly_score * 100).toFixed(0)}%` : "N/A"}
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
