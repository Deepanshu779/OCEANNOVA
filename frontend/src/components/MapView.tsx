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
import { useEffect, useMemo, useState } from "react";
import type { GeoJsonObject } from "geojson";
import { getSpillGeoJSON, type Investigation, type Vessel } from "../services/api";

interface MapViewProps { investigation: Investigation; }

delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const spillIcon = L.divIcon({ className: "spill-marker", html: `<div class="spill-marker-inner"></div>`, iconSize: [30, 30], iconAnchor: [15, 15] });
const originIcon = L.divIcon({ className: "origin-marker", html: `<div class="origin-marker-inner"></div>`, iconSize: [28, 28], iconAnchor: [14, 14] });
const vesselIcon = L.divIcon({ className: "vessel-ship-marker", html: `<div class="vessel-ship-icon" aria-label="Representative vessel candidate">🚢</div>`, iconSize: [40, 40], iconAnchor: [20, 20], popupAnchor: [0, -18] });

function investigationPoints(investigation: Investigation): [number, number][] {
  const points: [number, number][] = [[investigation.centroid.lat, investigation.centroid.lon]];
  if (investigation.origin) points.push([investigation.origin.latitude, investigation.origin.longitude]);
  investigation.drift.forEach((point) => points.push([point.latitude, point.longitude]));
  return points;
}

function IncidentOverview({ investigation }: { investigation: Investigation }) {
  const map = useMap();
  useEffect(() => {
    const points = investigationPoints(investigation);
    map.fitBounds(L.latLngBounds(points), { padding: [45, 45], maxZoom: 10, animate: false });
  }, [map, investigation]);
  return null;
}

function FocusInvestigationButton({ investigation }: { investigation: Investigation }) {
  const map = useMap();
  const focusInvestigation = () => {
    const points = investigationPoints(investigation);
    map.fitBounds(L.latLngBounds(points), { padding: [70, 70], maxZoom: 11, animate: true });
  };
  return <button type="button" className="map-action-button" onClick={focusInvestigation}>Focus spill</button>;
}

function vesselPopup(vessel: Vessel) {
  const score = vessel.attribution_score.toFixed(1);
  const distance = vessel.distance_km == null ? "—" : `${vessel.distance_km.toFixed(2)} km`;
  const time = vessel.time_difference_hours == null ? "—" : `${vessel.time_difference_hours >= 0 ? "+" : ""}${vessel.time_difference_hours.toFixed(1)} h`;
  const representative = vessel.relevance !== "filtered";
  return (
    <div className="vessel-popup">
      <strong>{vessel.vessel_name ?? vessel.mmsi}</strong>
      <span className="popup-provenance">{representative ? "REPRESENTATIVE DEMO CANDIDATE" : "FILTERED AIS TRAFFIC"}</span>
      <div>MMSI: {vessel.mmsi}</div><div>Attribution score: {score}%</div><div>Distance to origin: {distance}</div><div>Time difference: {time}</div>
      <div>Speed: {vessel.speed_knots == null ? "—" : `${vessel.speed_knots.toFixed(1)} kn`}</div><div>Course: {vessel.course == null ? "—" : `${vessel.course.toFixed(0)}°`}</div>
      {representative && <small>No historical AIS claim — corroboration required.</small>}
    </div>
  );
}

function VesselAttributionPanel({ vessels }: { vessels: Vessel[] }) {
  const ranked = useMemo(() => [...vessels].sort((a, b) => b.attribution_score - a.attribution_score).slice(0, 4), [vessels]);
  return (
    <aside className="vessel-attribution-panel" aria-label="Vessel attribution ranking">
      <div className="vessel-panel-head">
        <div>
          <span className="vessel-panel-kicker">VESSEL ATTRIBUTION</span>
          <h3>Potential vessels</h3>
        </div>
        <span className="vessel-demo-badge">DEMO DATASET</span>
      </div>
      <p className="vessel-panel-subtitle">Ranked by proximity, temporal correlation, trajectory and behavioral evidence.</p>
      <div className="vessel-ranking">
        {ranked.map((vessel, index) => {
          const score = Math.max(0, Math.min(100, vessel.attribution_score));
          const level = score >= 90 ? "high" : score >= 75 ? "medium" : "low";
          return (
            <div className={`vessel-rank-card ${level}`} key={vessel.mmsi}>
              <div className="vessel-rank-number">{index + 1}</div>
              <div className="vessel-rank-icon">🚢</div>
              <div className="vessel-rank-main">
                <strong>{vessel.vessel_name ?? vessel.mmsi}</strong>
                <span>{vessel.distance_km == null ? "Distance unavailable" : `${vessel.distance_km.toFixed(1)} km from origin`} · {vessel.time_difference_hours == null ? "time unavailable" : `${Math.abs(vessel.time_difference_hours).toFixed(1)} h offset`}</span>
                <div className="vessel-score-track"><i style={{ width: `${score}%` }} /></div>
              </div>
              <b className="vessel-score">{score.toFixed(1)}%</b>
            </div>
          );
        })}
      </div>
      <div className="vessel-panel-note"><span>i</span><p>Attribution score indicates evidence-based likelihood, not proof of responsibility. Current candidates are representative demo data.</p></div>
    </aside>
  );
}

export default function MapView({ investigation }: MapViewProps) {
  const [spillGeoJson, setSpillGeoJson] = useState<GeoJsonObject | null>(null);
  useEffect(() => {
    let active = true;
    setSpillGeoJson(null);
    getSpillGeoJSON(investigation.spill_id).then((data) => { if (active) setSpillGeoJson(data); }).catch((error) => console.error("Radar_data spill footprint:", error));
    return () => { active = false; };
  }, [investigation.spill_id]);

  const spillPosition: [number, number] = [investigation.centroid.lat, investigation.centroid.lon];
  const originPosition: [number, number] | null = investigation.origin ? [investigation.origin.latitude, investigation.origin.longitude] : null;
  const driftPath: [number, number][] = investigation.drift.map((point) => [point.latitude, point.longitude]);

  return (
    <MapContainer center={spillPosition} zoom={7} scrollWheelZoom style={{ height: "100%", width: "100%" }}>
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <IncidentOverview investigation={investigation} />
      <FocusInvestigationButton investigation={investigation} />
      {spillGeoJson && <GeoJSON data={spillGeoJson} style={() => ({ color: "#ef4444", weight: 2.5, opacity: 0.95, fillColor: "#ef4444", fillOpacity: 0.24 })}>
        <Popup><strong>Processed spill footprint</strong><br />Evidence: Sentinel-1 SAR<br />Method: U-Net + radiometric/look-alike filtering<br />Predicted area: {investigation.area_km2} km²<br />Mean AI confidence: {(investigation.confidence * 100).toFixed(1)}%</Popup>
      </GeoJSON>}
      <div className="map-overview-label">GULF OF MEXICO • RADAR EVIDENCE</div>
      <div className="map-hero-card"><div className="map-hero-kicker">REAL RADAR INVESTIGATION</div><strong>{investigation.spill_id} • {investigation.area_km2} km²</strong><span>Sentinel-1 SAR → U-Net → characterization</span></div>
      <div className="map-legend"><div className="legend-title">EVIDENCE LEGEND</div><div><span className="legend-footprint" /> Processed spill footprint</div><div><span className="legend-dot legend-origin" /> Origin analysis when available</div><div><span className="legend-line" /> Drift when available</div><div><span className="legend-vessel-icon">🚢</span> Vessel attribution candidate</div></div>
      <div className="map-status-card"><strong>● RADAR EVIDENCE ACTIVE</strong><span>DETECT → CHARACTERIZE → CORRELATE</span></div>
      <VesselAttributionPanel vessels={investigation.vessels} />
      <Marker position={spillPosition} icon={spillIcon}><Popup><strong>{investigation.spill_id}</strong><br />Real processed Radar_data candidate<br />Confidence: {(investigation.confidence * 100).toFixed(1)}%<br />Predicted area: {investigation.area_km2} km²<br />Age: Not available from a single scene</Popup></Marker>
      {originPosition && <><Circle center={originPosition} radius={investigation.origin!.uncertainty_km * 1000} pathOptions={{ fillOpacity: 0.12, weight: 2, dashArray: "7 6" }} /><Marker position={originPosition} icon={originIcon} /></>}
      {driftPath.length > 1 && <Polyline positions={driftPath} pathOptions={{ weight: 4, opacity: 0.9 }} />}
      {investigation.vessels.map((vessel) => vessel.latitude == null || vessel.longitude == null ? null : <Marker key={vessel.mmsi} position={[vessel.latitude, vessel.longitude]} icon={vesselIcon}><Popup>{vesselPopup(vessel)}</Popup></Marker>)}
    </MapContainer>
  );
}
