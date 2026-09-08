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
        <div><p className="eyebrow">ACTIVE CASE</p><h2>Investigation</h2></div>
        <span className="case-badge">{investigation.spill_id}</span>
      </div>

      <div className="spill-card">
        <div className="label">AI-VALIDATED SPILL</div>
        <h3>{investigation.spill_id}</h3>
        <div className="metric"><span>Confidence</span><strong>{(investigation.confidence * 100).toFixed(0)}%</strong></div>
        <div className="metric"><span>Area</span><strong>{investigation.area_km2} km²</strong></div>
        <div className="metric"><span>Perimeter</span><strong>{investigation.characterization.perimeter_estimate_km ?? "N/A"} km</strong></div>
        <div className="metric"><span>Compactness</span><strong>{investigation.characterization.compactness_estimate ?? "N/A"}</strong></div>
        <div className="metric"><span>Age estimate</span><strong>{investigation.characterization.estimated_age_hours != null ? `${investigation.characterization.estimated_age_hours} h` : "Not available"}</strong></div>
        {investigation.origin && <div className="metric"><span>Origin uncertainty</span><strong>±{investigation.origin.uncertainty_km} km</strong></div>}
      </div>

      <div className="evidence-panel">
        <div className="evidence-panel-header">
          <div>
            <p className="eyebrow">EVIDENCE STATUS</p>
            <h3>Multi-Source Investigation</h3>
          </div>
          <span className="evidence-live">ACTIVE</span>
        </div>
        <div className="evidence-item"><span className="evidence-icon">🛰</span><div><strong>Satellite</strong><p>Real Sentinel-1 SAR test scene</p></div><span className="evidence-tag real">REAL</span></div>
        <div className="evidence-item"><span className="evidence-icon">🤖</span><div><strong>AI Detection</strong><p>U-Net + radiometric validation</p></div><span className="evidence-tag real">REAL</span></div>
        <div className="evidence-item"><span className="evidence-icon">🌊</span><div><strong>Drift Model</strong><p>Backward + forward prototype</p></div><span className="evidence-tag demo">DEMO</span></div>
        <div className="evidence-item"><span className="evidence-icon">🚢</span><div><strong>AIS Correlation</strong><p>Representative vessel trajectories</p></div><span className="evidence-tag demo">DEMO</span></div>
      </div>

      <div className="section">
        <div className="section-heading"><h3>Top Suspects</h3><span>{topVessels.length} ranked</span></div>
        {topVessels.map((vessel, index) => {
          const score = vessel.attribution_score * 100;
          return (
            <button className={`suspect-card ${index === 0 ? "top-suspect" : ""}`} key={vessel.mmsi} type="button" onClick={() => onSelectVessel?.(vessel)}>
              <div className="suspect-header"><div><span className="rank">#{index + 1}</span><strong>{vessel.vessel_name ?? vessel.mmsi}</strong></div><strong className="suspect-score">{score.toFixed(0)}%</strong></div>
              <div className="score-bar"><div className="score-fill" style={{ width: `${score}%` }} /></div>
              {index === 0 && <div className="top-suspect-explanation">Highest-ranked candidate based on spatial proximity, temporal consistency, trajectory match and behavioral evidence.</div>}
              <div className="suspect-details">
                <div><span>Distance</span><strong>{vessel.distance_km ?? "N/A"} km</strong></div>
                <div><span>Time Δ</span><strong>{vessel.time_difference_hours ?? "N/A"} h</strong></div>
                <div><span>Proximity</span><strong>{vessel.proximity_score != null ? `${(vessel.proximity_score * 100).toFixed(0)}%` : "N/A"}</strong></div>
                <div><span>Trajectory</span><strong>{vessel.trajectory_match_score != null ? `${(vessel.trajectory_match_score * 100).toFixed(0)}%` : "N/A"}</strong></div>
                <div><span>Behavior</span><strong>{vessel.behavioral_anomaly_score != null ? `${(vessel.behavioral_anomaly_score * 100).toFixed(0)}%` : "N/A"}</strong></div>
                <div><span>Temporal</span><strong>{vessel.temporal_score != null ? `${(vessel.temporal_score * 100).toFixed(0)}%` : "N/A"}</strong></div>
              </div>
            </button>
          );
        })}
      </div>

      <div className="section">
        <div className="section-heading"><h3>AIS Evidence</h3><span>Representative tracks</span></div>
        <div className="metric"><span>Total vessels</span><strong>{investigation.traffic.total_vessels_considered}</strong></div>
        <div className="metric"><span>Filtered irrelevant</span><strong>{investigation.traffic.filtered_irrelevant}</strong></div>
        <div className="metric"><span>Ranked candidates</span><strong>{investigation.traffic.ranked_candidates}</strong></div>
        <p className="micro-copy">{investigation.traffic.filtering_rule}</p>
      </div>

      <div className="section">
        <div className="section-heading"><h3>Drift Analysis</h3><span>{investigation.drift.length} points</span></div>
        <div className="metric"><span>Origin method</span><strong>{investigation.origin?.method ?? "Unavailable"}</strong></div>
        <div className="metric"><span>Coverage</span><strong>{investigation.drift.some((p) => p.hours_from_detection < 0) ? "Backward + " : ""}{investigation.drift.some((p) => p.hours_from_detection > 0) ? "Forward" : "Observation"}</strong></div>
        <p className="micro-copy">Environmental inputs are prototype demonstration values for this case.</p>
      </div>

      <div className="section investigation-summary">
        <div className="section-heading"><h3>Investigation Summary</h3><span>Pipeline</span></div>
        <div className="summary-step"><span className="summary-number">01</span><div><strong>Detect + Characterize</strong><p>Sentinel-1 SAR + U-Net + radiometric validation</p></div></div>
        <div className="summary-step"><span className="summary-number">02</span><div><strong>Reconstruct Origin</strong><p>{investigation.origin ? `±${investigation.origin.uncertainty_km} km uncertainty` : "Not available"}</p></div></div>
        <div className="summary-step"><span className="summary-number">03</span><div><strong>Hindcast + Forecast</strong><p>{investigation.drift.length} timestamped drift points</p></div></div>
        <div className="summary-step"><span className="summary-number">04</span><div><strong>Filter + Rank AIS</strong><p>{investigation.traffic.ranked_candidates} candidates from {investigation.traffic.total_vessels_considered} vessels</p></div></div>
      </div>

      <div className="disclaimer-card">
        <strong>Evidence boundary</strong>
        <p>Satellite detection is evaluated on a real test scene. Environmental inputs and AIS tracks are representative demo data. Attribution is decision support, not proof of legal responsibility.</p>
      </div>
    </aside>
  );
}
