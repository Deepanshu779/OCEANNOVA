import type { Investigation, Vessel } from "../services/api";

interface SidebarProps {
  investigation: Investigation;
  onSelectVessel?: (vessel: Vessel) => void;
}

export default function Sidebar({ investigation, onSelectVessel }: SidebarProps) {
  const topVessels = investigation.vessels.slice(0, 3);
  const confidence = investigation.confidence * 100;
  const best = topVessels[0];
  const earliestHindcast = investigation.drift.length
    ? Math.min(...investigation.drift.map((point) => point.hours_from_detection))
    : 0;
  const latestForecast = investigation.drift.length
    ? Math.max(...investigation.drift.map((point) => point.hours_from_detection))
    : 0;

  return (
    <aside className="sidebar">
      <div className="sidebar-heading-row">
        <div><p className="eyebrow">ACTIVE CASE</p><h2>Investigation</h2></div>
        <span className="case-badge">{investigation.spill_id}</span>
      </div>

      <div className="spill-card">
        <div className="label">AI-VALIDATED SPILL</div>
        <h3>{investigation.spill_id}</h3>
        <div className="metric"><span>AI confidence</span><strong>{confidence.toFixed(1)}%</strong></div>
        <div className="metric"><span>Detected area</span><strong>{investigation.area_km2} km²</strong></div>
        <div className="metric"><span>Perimeter</span><strong>{investigation.characterization.perimeter_estimate_km ?? "N/A"} km</strong></div>
        <div className="metric"><span>Compactness</span><strong>{investigation.characterization.compactness_estimate ?? "N/A"}</strong></div>
        <div className="metric"><span>Spill age</span><strong>{investigation.characterization.estimated_age_hours != null ? `${investigation.characterization.estimated_age_hours} h` : "Not estimated"}</strong></div>
        <div className="metric"><span>Age status</span><strong>{investigation.characterization.estimated_age_hours != null ? "Estimated" : "Insufficient observations"}</strong></div>
        {investigation.origin && <div className="metric"><span>Origin uncertainty</span><strong>±{investigation.origin.uncertainty_km} km</strong></div>}
      </div>

      <div className="evidence-panel">
        <div className="evidence-panel-header">
          <div><p className="eyebrow">EVIDENCE STATUS</p><h3>Multi-Source Investigation</h3></div>
          <span className="evidence-live">ACTIVE</span>
        </div>
        <div className="evidence-item"><span className="evidence-icon">🛰</span><div><strong>01 · Detect</strong><p>Sentinel-1 SAR + U-Net segmentation</p></div><span className="evidence-tag real">REAL</span></div>
        <div className="evidence-item"><span className="evidence-icon">✓</span><div><strong>02 · Validate</strong><p>Radiometric + connected-component filtering</p></div><span className="evidence-tag real">REAL</span></div>
        <div className="evidence-item"><span className="evidence-icon">🌊</span><div><strong>03 · Trace</strong><p>Backward / forward drift reconstruction</p></div><span className="evidence-tag demo">DEMO</span></div>
        <div className="evidence-item"><span className="evidence-icon">🚢</span><div><strong>04 · Correlate</strong><p>AIS proximity + temporal + trajectory evidence</p></div><span className="evidence-tag demo">DEMO</span></div>
      </div>

      <div className="section decision-card">
        <div className="section-heading"><h3>Investigation Signal</h3><span>Explainable</span></div>
        <p className="micro-copy">The pipeline narrows a detected slick into a probable origin and ranks nearby vessel candidates using independent evidence factors.</p>
        {best && <div className="decision-highlight"><span>Current #1 candidate</span><strong>{best.vessel_name ?? best.mmsi} · {(best.attribution_score * 100).toFixed(1)}%</strong><small>Review the factor breakdown below before drawing conclusions.</small></div>}
      </div>

      <div className="section">
        <div className="section-heading"><h3>Top Suspects</h3><span>{topVessels.length} ranked</span></div>
        {topVessels.map((vessel, index) => {
          const score = vessel.attribution_score * 100;
          return (
            <button className={`suspect-card ${index === 0 ? "top-suspect" : ""}`} key={vessel.mmsi} type="button" onClick={() => onSelectVessel?.(vessel)}>
              <div className="suspect-header"><div><span className="rank">#{index + 1}</span><strong>{vessel.vessel_name ?? vessel.mmsi}</strong></div><strong className="suspect-score">{score.toFixed(1)}%</strong></div>
              <div className="score-bar"><div className="score-fill" style={{ width: `${Math.min(score, 100)}%` }} /></div>
              {index === 0 && <div className="top-suspect-explanation">Explainable score: proximity 35% · temporal 20% · trajectory 30% · behavior 15%.</div>}
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
        <div className="section-heading"><h3>AIS Evidence</h3><span>Source status</span></div>
        <div className="metric"><span>Total vessels</span><strong>{investigation.traffic.total_vessels_considered}</strong></div>
        <div className="metric"><span>Filtered irrelevant</span><strong>{investigation.traffic.filtered_irrelevant}</strong></div>
        <div className="metric"><span>Ranked candidates</span><strong>{investigation.traffic.ranked_candidates}</strong></div>
        <p className="micro-copy">{investigation.traffic.filtering_rule}</p>
        <p className="micro-copy">AIS source: representative demonstration trajectories; real historical AIS can be supplied through the same pipeline.</p>
      </div>

      <div className="section">
        <div className="section-heading"><h3>Drift Analysis</h3><span>{investigation.drift.length} points</span></div>
        <div className="metric"><span>Origin method</span><strong>{investigation.origin?.method ?? "Unavailable"}</strong></div>
        <div className="metric"><span>Origin window</span><strong>{earliestHindcast < 0 ? `T${earliestHindcast} h` : "Observation"}</strong></div>
        <div className="metric"><span>Detection reference</span><strong>T0</strong></div>
        <div className="metric"><span>Forecast horizon</span><strong>{latestForecast > 0 ? `+${latestForecast} h` : "N/A"}</strong></div>
        <p className="micro-copy">Origin time is reconstructed from the earliest backward-hindcast point relative to the SAR detection time. Environmental inputs are prototype demonstration values for this case.</p>
      </div>

      <div className="section investigation-summary">
        <div className="section-heading"><h3>Investigation Pipeline</h3><span>SIH flow</span></div>
        <div className="summary-step"><span className="summary-number">01</span><div><strong>DETECT</strong><p>SAR + U-Net identifies dark slick candidates</p></div></div>
        <div className="summary-step"><span className="summary-number">02</span><div><strong>CHARACTERIZE</strong><p>Area, perimeter, compactness and confidence</p></div></div>
        <div className="summary-step"><span className="summary-number">03</span><div><strong>TRACE</strong><p>Drift hindcast reconstructs probable origin point + time</p></div></div>
        <div className="summary-step"><span className="summary-number">04</span><div><strong>CORRELATE</strong><p>AIS traffic filtered around the origin window</p></div></div>
        <div className="summary-step"><span className="summary-number">05</span><div><strong>RANK</strong><p>Explainable multi-factor candidate scoring</p></div></div>
      </div>

      <div className="disclaimer-card">
        <strong>Evidence boundary</strong>
        <p>Satellite detection is evaluated on a real test scene. Environmental inputs and AIS tracks are representative demo data. Attribution is investigative decision support, not proof of legal responsibility.</p>
      </div>
    </aside>
  );
}
