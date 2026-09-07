import type { Investigation, Vessel } from "../services/api";

interface SidebarProps {
  investigation: Investigation;
  onSelectVessel?: (vessel: Vessel) => void;
}

export default function Sidebar({ investigation, onSelectVessel }: SidebarProps) {
  const topVessels = investigation.vessels.slice(0, 3);

  return (
    <aside className="sidebar">
      <div className="sidebar-heading-row">
        <div>
          <p className="eyebrow">ACTIVE CASE</p>
          <h2>Investigation</h2>
        </div>
        <span className="case-badge">{investigation.spill_id}</span>
      </div>

      <div className="spill-card">
        <div className="label">DETECTED SPILL</div>
        <h3>{investigation.spill_id}</h3>
        <div className="metric"><span>Confidence</span><strong>{(investigation.confidence * 100).toFixed(0)}%</strong></div>
        <div className="metric"><span>Area</span><strong>{investigation.area_km2} km²</strong></div>
        {investigation.origin && (
          <div className="metric"><span>Origin uncertainty</span><strong>±{investigation.origin.uncertainty_km} km</strong></div>
        )}
      </div>

      <div className="section">
        <div className="section-heading">
          <h3>Top Suspects</h3>
          <span>{topVessels.length} ranked</span>
        </div>

        {topVessels.map((vessel, index) => {
          const score = vessel.attribution_score * 100;
          return (
            <button
              className={`suspect-card ${index === 0 ? "top-suspect" : ""}`}
              key={vessel.mmsi}
              type="button"
              onClick={() => onSelectVessel?.(vessel)}
            >
              <div className="suspect-header">
                <div><span className="rank">#{index + 1}</span><strong>{vessel.vessel_name ?? vessel.mmsi}</strong></div>
                <strong className="suspect-score">{score.toFixed(0)}%</strong>
              </div>
              <div className="score-bar"><div className="score-fill" style={{ width: `${score}%` }} /></div>
              <div className="suspect-details">
                <div><span>Distance</span><strong>{vessel.distance_km ?? "N/A"} km</strong></div>
                <div><span>Time Δ</span><strong>{vessel.time_difference_hours ?? "N/A"} h</strong></div>
                <div><span>Trajectory</span><strong>{vessel.trajectory_match_score != null ? `${(vessel.trajectory_match_score * 100).toFixed(0)}%` : "N/A"}</strong></div>
                <div><span>Behavior</span><strong>{vessel.behavioral_anomaly_score != null ? `${(vessel.behavioral_anomaly_score * 100).toFixed(0)}%` : "N/A"}</strong></div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="section">
        <div className="section-heading"><h3>Drift Analysis</h3><span>{investigation.drift.length} points</span></div>
        <div className="metric"><span>Origin method</span><strong>{investigation.origin?.method ?? "Unavailable"}</strong></div>
      </div>

      <div className="section investigation-summary">
        <div className="section-heading"><h3>Investigation Summary</h3><span>Pipeline</span></div>
        <div className="summary-step"><span className="summary-number">01</span><div><strong>Spill Detected</strong><p>Satellite-based event candidate</p></div></div>
        <div className="summary-step"><span className="summary-number">02</span><div><strong>Origin Reconstructed</strong><p>{investigation.origin ? `±${investigation.origin.uncertainty_km} km uncertainty` : "Not available"}</p></div></div>
        <div className="summary-step"><span className="summary-number">03</span><div><strong>Drift Analysed</strong><p>{investigation.drift.length} trajectory observations</p></div></div>
        <div className="summary-step"><span className="summary-number">04</span><div><strong>Vessels Ranked</strong><p>{investigation.vessels.length} demonstration AIS candidates</p></div></div>
      </div>

      <div className="disclaimer-card">
        <strong>Investigation score</strong>
        <p>Ranking is decision support based on available evidence. It is not proof of legal responsibility.</p>
      </div>
    </aside>
  );
}
