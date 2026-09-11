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
import { getSpillGeoJSON, type Investigation, type Vessel } from "../services/api";

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

const spillIcon = L.divIcon({ className: "spill-marker", html: `<div class="spill-marker-inner"></div>`, iconSize: [30, 30], iconAnchor: [15, 15] });
const originIcon = L.divIcon({ className: "origin-marker", html: `<div class="origin-marker-inner"></div>`, iconSize: [28, 28], iconAnchor: [14, 14] });

const vesselIcon = L.divIcon({
  className: "vessel-ship-marker",
  html: `<div class="vessel-ship-icon" aria-label="Vessel">🚢</div>`,
  iconSize: [40, 40],
  iconAnchor: [20, 20],
  popupAnchor: [0, -18],
});

function IncidentOverview({ investigation }: { investigation: Investigation }) {
  const map = useMap();
  useEffect(() => {
    const points: [number, number][] = [[investigation.centroid.lat, investigation.centroid.lon]];
    if (investigation.origin) points.push([investigation.origin.latitude, investigation.origin.longitude]);
    investigation.drift.forEach((p) => points.push([p.latitude, p.longitude]));
    investigation.vessels.forEach((v) => {
      if (v.latitude != null && v.longitude != null) points.push([v.latitude, v.longitude]);
    });
    map.fitBounds(L.latLngBounds(points), { padding: [40, 40], maxZoom: 9, animate: false });
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

function vesselPopup(vessel: Vessel) {
  const score = vessel.attribution_score.toFixed(1);
  const distance = vessel.distance_km == null ? "—" : `${vessel.distance_km.toFixed(2)} km`;
  const time = vessel.time_difference_hours == null ? "—" : `${vessel.time_difference_hours >= 0 ? "+" : ""}${vessel.time_difference_hours.toFixed(1)} h`;
  return (
    <>
      <strong>{vessel.vessel_name ?? vessel.mmsi}</strong><br />
      MMSI: {vessel.mmsi}<br />
      Attribution score: {score}%<br />
      Distance to origin: {distance}<br />
      Time difference: {time}<br />
      Speed: {vessel.speed_knots == null ? "—" : `${vessel.speed_knots.toFixed(1)} kn`}<br />
      Course: {vessel.course == null ? "—" : `${vessel.course.toFixed(0)}°`}<br />
      <span>{vessel.relevance === "filtered" ? "Filtered traffic" : "Representative candidate"}</span>
    </>
  );
}

export default function MapView({ investigation }: MapViewProps) {
  const [spillGeoJson, setSpillGeoJson] = useState<GeoJsonObject | null>(null);

  useEffect(() => {
    let active = true;
    setSpillGeoJson(null);
    getSpillGeoJSON(investigation.spill_id)
      .then((data) => { if (active) setSpillGeoJson(data); })
      .catch((error) => console.error("Radar_data spill footprint:", error));
    return () => { active = false; };
  }, [investigation.spill_id]);

  const spillPosition: [number, number] = [investigation.centroid.lat, investigation.centroid.lon];
  const originPosition: [number, number] | null = investigation.origin
    ? [investigation.origin.latitude, investigation.origin.longitude]
    : null;
  const driftPath: [number, number][] = investigation.drift.map((point) => [point.latitude, point.longitude]);

  return (
    <MapContainer center={spillPosition} zoom={7} scrollWheelZoom style={{ height: "100%", width: "100%" }}>
      <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <IncidentOverview investigation={investigation} />
      <FocusInvestigationButton investigation={investigation} />

      {spillGeoJson && (
        <GeoJSON
          data={spillGeoJson}
          style={() => ({ color: "#ef4444", weight: 2, opacity: 0.95, fillColor: "#ef4444", fillOpacity: 0.24 })}
        >
          <Popup>
            <strong>Real Radar_data Spill Footprint</strong><br />
            Source: Sentinel-1 SAR<br />
            Method: U-Net + radiometric/look-alike filtering<br />
            Area: {investigation.area_km2} km²<br />
            Mean AI confidence: {(investigation.confidence * 100).toFixed(1)}%
          </Popup>
        </GeoJSON>
      )}

      <div className="map-overview-label">GULF OF MEXICO • REAL RADAR_DATA SCENE</div>
      <div className="map-hero-card">
        <div className="map-hero-kicker">REAL RADAR INVESTIGATION</div>
        <strong>{investigation.spill_id} • {investigation.area_km2} km²</strong>
        <span>Sentinel-1 SAR → U-Net → characterization</span>
      </div>
      <div className="map-legend">
        <div className="legend-title">MAP LEGEND</div>
        <div><span className="legend-footprint" /> Real processed spill footprint</div>
        <div><span className="legend-dot legend-origin" /> Origin analysis when available</div>
        <div><span className="legend-line" /> Drift when available</div>
        <div><span className="legend-vessel-icon">🚢</span> Vessel candidate</div>
      </div>
      <div className="map-status-card">
        <strong>● RADAR INVESTIGATION ACTIVE</strong>
        <span>DETECT → CHARACTERIZE</span>
      </div>

      <Marker position={spillPosition} icon={spillIcon}>
        <Popup>
          <strong>{investigation.spill_id}</strong><br />
          Real processed Radar_data candidate<br />
          Confidence: {(investigation.confidence * 100).toFixed(1)}%<br />
          Area: {investigation.area_km2} km²<br />
          Age: Not available from a single scene
        </Popup>
      </Marker>

      {originPosition && (
        <>
          <Circle center={originPosition} radius={investigation.origin!.uncertainty_km * 1000} pathOptions={{ fillOpacity: 0.12, weight: 2, dashArray: "7 6" }} />
          <Marker position={originPosition} icon={originIcon} />
        </>
      )}

      {driftPath.length > 1 && <Polyline positions={driftPath} pathOptions={{ weight: 4, opacity: 0.9 }} />}

      {investigation.vessels.map((vessel) => {
        if (vessel.latitude == null || vessel.longitude == null) return null;
        return (
          <Marker key={vessel.mmsi} position={[vessel.latitude, vessel.longitude]} icon={vesselIcon}>
            <Popup>{vesselPopup(vessel)}</Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
