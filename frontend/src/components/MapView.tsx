import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    Circle,
    Polyline,
    useMap,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { useEffect } from "react";

import type { Investigation } from "../services/api";


// Fix Leaflet marker icons when using Vite
delete (
    L.Icon.Default.prototype as unknown as {
        _getIconUrl?: unknown;
    }
)._getIconUrl;

L.Icon.Default.mergeOptions({
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

    iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

    shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});


// Vessel icon
const vesselIcon = L.divIcon({
    className: "vessel-marker",
    html: "🚢",
    iconSize: [32, 32],
    iconAnchor: [16, 16],
});

const spillIcon = L.divIcon({
    className: "spill-marker",
    html: `<div class="spill-marker-inner"></div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
});

const originIcon = L.divIcon({
    className: "origin-marker",
    html: `<div class="origin-marker-inner"></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
});


interface MapViewProps {
    investigation: Investigation;
}


/*
 * Automatically fits the map around the complete investigation.
 *
 * Includes:
 * - detected spill
 * - probable origin
 * - drift trajectory
 * - AIS vessels
 */
function FitInvestigationBounds({
    investigation,
}: {
    investigation: Investigation;
}) {
    const map = useMap();

    useEffect(() => {
        const points: [number, number][] = [];

        // Detected spill
        points.push([
            investigation.centroid.lat,
            investigation.centroid.lon,
        ]);

        // Probable origin
        if (investigation.origin) {
            points.push([
                investigation.origin.latitude,
                investigation.origin.longitude,
            ]);
        }

        // Drift trajectory
        investigation.drift.forEach((point) => {
            points.push([
                point.latitude,
                point.longitude,
            ]);
        });

        // AIS vessels
        investigation.vessels.forEach((vessel) => {
            if (
                vessel.latitude !== null &&
                vessel.latitude !== undefined &&
                vessel.longitude !== null &&
                vessel.longitude !== undefined
            ) {
                points.push([
                    vessel.latitude,
                    vessel.longitude,
                ]);
            }
        });

        // Nothing to fit
        if (points.length === 0) {
            return;
        }

        const bounds = L.latLngBounds(points);

        map.fitBounds(bounds, {
            padding: [50, 50],
            maxZoom: 10,
            animate: true,
        });
    }, [map, investigation]);

    return null;
}


export default function MapView({
    investigation,
}: MapViewProps) {

    const spillPosition: [number, number] = [
        investigation.centroid.lat,
        investigation.centroid.lon,
    ];


    const originPosition =
        investigation.origin
            ? [
                investigation.origin.latitude,
                investigation.origin.longitude,
            ] as [number, number]
            : null;


    const driftPath: [number, number][] =
        investigation.drift.map((point) => [
            point.latitude,
            point.longitude,
        ]);


    return (
        <MapContainer
            center={spillPosition}
            zoom={8}
            scrollWheelZoom={true}
            style={{
                height: "100%",
                width: "100%",
            }}
        >

            <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />


            {/* Automatically frame the investigation */}
            <FitInvestigationBounds
                investigation={investigation}
            />


            {/* =========================
                DETECTED SPILL
            ========================== */}

            <Marker
                position={spillPosition}
                icon={spillIcon}
            >

                <Popup>

                    <strong>
                        {investigation.spill_id}
                    </strong>

                    <br />

                    Oil Spill Detected

                    <br />

                    Confidence:{" "}
                    {(investigation.confidence * 100).toFixed(0)}%

                    <br />

                    Area:{" "}
                    {investigation.area_km2} km²

                </Popup>

            </Marker>


            {/* =========================
                PROBABLE ORIGIN
            ========================== */}

            {originPosition && (
                <>
                    <Circle
                        center={originPosition}
                        radius={
                            investigation.origin!.uncertainty_km * 1000
                        }
                        pathOptions={{
                            fillOpacity: 0.15,
                        }}
                    />

                    <Marker
                        position={originPosition}
                        icon={originIcon}
                    >

                        <Popup>

                            <strong>
                                Probable Spill Origin
                            </strong>

                            <br />

                            Uncertainty:{" "}
                            {investigation.origin!.uncertainty_km} km

                            <br />

                            Method:{" "}
                            {investigation.origin!.method ?? "Unknown"}

                        </Popup>

                    </Marker>
                </>
            )}


            {/* =========================
                OIL DRIFT PATH
            ========================== */}

            {driftPath.length > 1 && (
                <Polyline
                    positions={driftPath}
                    pathOptions={{
                        weight: 4,
                    }}
                >
                    <Popup>
                        Predicted / reconstructed oil drift path
                    </Popup>
                </Polyline>
            )}


            {/* =========================
                AIS VESSELS
            ========================== */}

            {investigation.vessels.map((vessel) => {

                if (
                    vessel.latitude === undefined ||
                    vessel.longitude === undefined ||
                    vessel.latitude === null ||
                    vessel.longitude === null
                ) {
                    return null;
                }

                return (
                    <Marker
                        key={vessel.mmsi}
                        position={[
                            vessel.latitude,
                            vessel.longitude,
                        ]}
                        icon={vesselIcon}
                    >

                        <Popup>

                            <strong>
                                {vessel.vessel_name ?? "Unknown Vessel"}
                            </strong>

                            <br />

                            MMSI: {vessel.mmsi}

                            <br />

                            Attribution Score:{" "}
                            {(vessel.attribution_score * 100).toFixed(0)}%

                            <br />

                            Distance:{" "}
                            {vessel.distance_km ?? "N/A"} km

                            <br />

                            Time Difference:{" "}
                            {vessel.time_difference_hours ?? "N/A"} hours

                            <br />

                            Trajectory Match:{" "}
                            {vessel.trajectory_match_score !== null &&
                                vessel.trajectory_match_score !== undefined
                                ? `${(
                                    vessel.trajectory_match_score * 100
                                ).toFixed(0)}%`
                                : "N/A"}

                        </Popup>

                    </Marker>
                );
            })}

        </MapContainer>
    );
}