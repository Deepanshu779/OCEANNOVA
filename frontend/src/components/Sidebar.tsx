import type { Investigation, Vessel } from "../services/api";

interface SidebarProps {
  investigation: Investigation;
  onSelectVessel?: (vessel: Vessel) => void;
}

export default function Sidebar({ investigation }: SidebarProps) {
  const confidence = investigation.confidence * 100;
  const hasValidation = investigation.characterization.area_km2 > 0;

  return (
    <aside className="sidebar">
      <div className="sidebar-heading-row">
        <div><p className="eyebrow">ACTIVE REAL SCENE</p><h2>Investigation</h2></div>
        <span className="case-badge">{investigation.spill_id}</span>
      </div>

      <div className="spill-card">
        <div className="label">REAL RADAR DETECTION</div>
        <h3>{investigation.spill_id}</h3>
        <div className="metric"><span>AI confidence</span><strong>{confidence.toFixed(1)}%</strong></div>
        <div className="metric"><span>Detected area</span><strong>{investigation.area_km2.toFixed(4)} km²</strong></div>
        <div className="metric"><span>Perimeter</span><strong>{investigation.characterization.perimeter_estimate_km ?? "N/A"} km</strong></div>
        <div className="metric"><span>Compactness</span><strong>{investigation.characterization.compactness_estimate ?? "N/A"}</strong></div>
        <div className="metric"><span>Spill age</span><strong>Not available</strong></div>
      </div>

      <div className="evidence-panel">
        <div className="evidence-panel-header">
          <div><p className="eyebrow">EVIDENCE STATUS</p><h3>Radar_data Pipeline</h3></div>
          <span className="evidence-live">REAL</span>
        </div>
        <div className="evidence-item"><span className="evidence-icon">🛰</span><div><strong>01 · Detect</strong><p>Sentinel-1 SAR + U-Net segmentation</p></div><span className="evidence-tag real">REAL</span></div>
        <div className="evidence-item"><span className="evidence-icon">✓</span><div><strong>02 · Validate</strong><p>Radiometric + component + shape filtering</p></div><span className="evidence-tag real">REAL</span></div>
        <div className="evidence-item"><span className="evidence-icon">▣</span><div><strong>03 · Characterize</strong><p>Area, perimeter, compactness and centroid</p></div><span className="evidence-tag real">REAL</span></div>
        <div className="evidence-item"><span className="evidence-icon">◎</span><div><strong>04 · Trace / AIS</strong><p>Waiting for real ocean forcing and historical AIS</p></div><span className="evidence-tag demo">PENDING</span></div>
      </div>

      <div className="section">
        <div className="section-heading"><h3>Ground-Truth Status</h3><span>{hasValidation ? "Available" : "N/A"}</span></div>
        <div className="metric"><span>Scene type</span><strong>Sentinel-1 SAR</strong></div>
        <div className="metric"><span>AI output</span><strong>Processed footprint</strong></div>
        <div className="metric"><span>Age estimate</span><strong>Not available</strong></div>
        <p className="micro-copy">A single SAR scene can provide a detected footprint and geometric characterization, but it does not by itself establish spill age or source vessel.</p>
      </div>

      <div className="section">
        <div className="section-heading"><h3>Ocean Drift</h3><span>Not loaded</span></div>
        <div className="metric"><span>Hindcast points</span><strong>0</strong></div>
        <div className="metric"><span>Forecast points</span><strong>0</strong></div>
        <p className="micro-copy">No synthetic current or wind values are shown. Real ocean forcing can be connected later without changing the Radar_data detection pipeline.</p>
      </div>

      <div className="section">
        <div className="section-heading"><h3>AIS Correlation</h3><span>Not loaded</span></div>
        <div className="metric"><span>Vessels considered</span><strong>0</strong></div>
        <div className="metric"><span>Ranked candidates</span><strong>0</strong></div>
        <p className="micro-copy">No synthetic vessel tracks or attribution scores are displayed. This prevents the demo from presenting fabricated vessel evidence as real.</p>
      </div>

      <div className="section investigation-summary">
        <div className="section-heading"><h3>Current Pipeline</h3><span>SIH flow</span></div>
        <div className="summary-step"><span className="summary-number">01</span><div><strong>DETECT</strong><p>Real Radar_data → U-Net spill candidate</p></div></div>
        <div className="summary-step"><span className="summary-number">02</span><div><strong>FILTER</strong><p>Radiometric and connected-component filtering</p></div></div>
        <div className="summary-step"><span className="summary-number">03</span><div><strong>CHARACTERIZE</strong><p>Geometry, centroid and AI confidence</p></div></div>
        <div className="summary-step"><span className="summary-number">04</span><div><strong>TRACE</strong><p>Real ocean forcing — pending</p></div></div>
        <div className="summary-step"><span className="summary-number">05</span><div><strong>ATTRIBUTE</strong><p>Real historical AIS — pending</p></div></div>
      </div>

      <div className="disclaimer-card">
        <strong>Evidence boundary</strong>
        <p>This dashboard now displays only the real processed Radar_data outputs. No synthetic AIS, ocean-current or vessel-attribution evidence is presented as real.</p>
      </div>
    </aside>
  );
}
