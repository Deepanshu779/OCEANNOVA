import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    Circle,
    Polyline,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import L from "leaflet";

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

const vesselIcon = L.divIcon({
    className: "vessel-marker",
    html: "🚢",
    iconSize: [32, 32],
    iconAnchor: [16, 16],
});

interface MapViewProps {
    investigation: Investigation;
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


            {/* =========================
          DETECTED SPILL
      ========================== */}

            <Marker position={spillPosition}>

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

                    <Marker position={originPosition}>

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

