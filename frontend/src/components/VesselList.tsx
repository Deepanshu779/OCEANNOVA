import type { Vessel } from "../services/api";

interface VesselListProps {
  vessels: Vessel[];
  onSelect?: (vessel: Vessel) => void;
}

export default function VesselList({ vessels, onSelect }: VesselListProps) {
  if (!vessels.length) return <p className="empty-state">No vessel candidates available.</p>;

  return (
    <div className="vessel-list">
      {vessels.map((vessel, index) => (
        <button key={vessel.mmsi} type="button" className="vessel-row" onClick={() => onSelect?.(vessel)}>
          <span className="vessel-rank">#{index + 1}</span>
          <span className="vessel-name">{vessel.vessel_name ?? vessel.mmsi}</span>
          <strong>{(vessel.attribution_score * 100).toFixed(0)}%</strong>
        </button>
      ))}
    </div>
  );
}
