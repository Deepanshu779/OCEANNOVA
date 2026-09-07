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
 * Keep the initial map at an India-wide maritime view.
 * This gives the investigation proper ocean context instead of
 * automatically zooming into a nearby city.
 */
function IndiaMaritimeOverview() {
    const map = useMap();

    useEffect(() => {
        map.fitBounds(
            [
                [4, 64],
                [30, 100],
            ],
            {
                padding: [20, 20],
                animate: false,
            }
        );
    }, [map]);

    return null;
}


/*
 * Small map control for investigators who want to jump
 * from the India-wide overview to the active spill event.
 */
function FocusInvestigationButton({
    investigation,
}: {
    investigation: Investigation;
}) {
    const map = useMap();

    const focusInvestigation = () => {
        const points: [number, number][] = [
            [
                investigation.centroid.lat,
                investigation.centroid.lon,
            ],
        ];

        if (investigation.origin) {
            points.push([
                investigation.origin.latitude,
                investigation.origin.longitude,
            ]);
        }

        investigation.drift.forEach((point) => {
            points.push([
                point.latitude,
                point.longitude,
            ]);
        });

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

        map.fitBounds(L.latLngBounds(points), {
            padding: [60, 60],
            maxZoom: 10,
            animate: true,
        });
    };

    return (
        <button
            type="button"
            onClick={focusInvestigation}
            style={{
                position: "absolute",
                top: "14px",
                right: "14px",
                zIndex: 1000,
                border: "1px solid rgba(255,255,255,0.25)",
                borderRadius: "8px",
                background: "rgba(15, 23, 42, 0.94)",
                color: "#ffffff",
                padding: "9px 12px",
                fontSize: "12px",
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 4px 14px rgba(0,0,0,0.25)",
            }}
        >
            Focus Investigation
        </button>
    );
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
            center={[18, 80]}
            zoom={5}
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

            <IndiaMaritimeOverview />

            <FocusInvestigationButton
                investigation={investigation}
            />

            <div
                style={{
                    position: "absolute",
                    top: "14px",
                    left: "60px",
                    zIndex: 1000,
                    padding: "8px 11px",
                    borderRadius: "8px",
                    background: "rgba(15, 23, 42, 0.90)",
                    color: "#ffffff",
                    fontSize: "11px",
                    fontWeight: 700,
                    letterSpacing: "0.04em",
                    pointerEvents: "none",
                }}
            >
                INDIAN MARITIME OVERVIEW
            </div>


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
            ========================== */

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
            ========================== */

            {driftPath.length > 1 && (
                <Polyline
                    positions={driftPath}
                    pathOptions={{
                        weight: 4,
                    }}
                >
                    <Popup>
                        Reconstructed / predicted oil drift path
                    </Popup>
                </Polyline>
            )}


            {/* =========================
                AIS VESSEL CANDIDATES
            ========================== */

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

                            AIS candidate • Demonstration data

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
