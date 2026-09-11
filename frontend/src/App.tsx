import { useEffect, useMemo, useState, type CSSProperties } from "react";
import MapView from "./components/MapView";
import {
  getDatasetScenes,
  getInvestigation,
  type DatasetScene,
  type Investigation,
} from "./services/api";
import "./index.css";
import "./command-center.css";
import "./map-polish.css";

const evidenceLayers = [
  { key: "satellite", label: "Satellite evidence", status: "REAL", detail: "Sentinel-1 SAR observation", tone: "real" },
  { key: "ai", label: "AI segmentation", status: "REAL", detail: "U-Net + radiometric filtering", tone: "real" },
  { key: "geometry", label: "Spill geometry", status: "DERIVED", detail: "Area, perimeter and footprint", tone: "derived" },
  { key: "drift", label: "Origin / drift", status: "READY", detail: "External forcing can be attached", tone: "ready" },
  { key: "ais", label: "Vessel attribution", status: "DEMO", detail: "Representative candidates only", tone: "demo" },
];

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedScene, setSelectedScene] = useState("SP-001");
  const [scenes, setScenes] = useState<DatasetScene[]>([]);
  const [showLibrary, setShowLibrary] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [sceneLoading, setSceneLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [libraryLoading, setLibraryLoading] = useState(false);
  const [briefCopied, setBriefCopied] = useState(false);

  async function withRetry<T>(task: () => Promise<T>, attempts = 4, delay = 800): Promise<T> {
    let lastError: unknown;
    for (let i = 0; i < attempts; i += 1) {
      try { return await task(); }
      catch (err) { lastError = err; if (i < attempts - 1) await new Promise((resolve) => setTimeout(resolve, delay * (i + 1))); }
    }
    throw lastError;
  }

  useEffect(() => {
    async function load() {
      try {
        setError(null);
        const [data, inventory] = await Promise.all([
          withRetry(() => getInvestigation("SP-001")),
          withRetry(() => getDatasetScenes()).catch(() => [] as DatasetScene[]),
        ]);
        setInvestigation(data);
        setScenes(inventory);
      } catch (err) {
        console.error(err);
        setError("The investigation service is temporarily unavailable.");
      } finally { setLoading(false); }
    }
    load();
  }, []);

  const filteredScenes = useMemo(
    () => scenes.filter((scene) => `${scene.scene_id} ${scene.file} ${scene.split}`.toLowerCase().includes(query.toLowerCase())),
    [scenes, query]
  );

  const investigationId = (scene: DatasetScene) => {
    const index = scenes.findIndex((item) => item.split === scene.split && item.scene_id === scene.scene_id);
    return index >= 0 ? `SP-${String(index + 1).padStart(3, "0")}` : "SP-001";
  };

  const openLibrary = async () => {
    setShowLibrary(true);
    if (scenes.length) return;
    setLibraryLoading(true);
    try { setScenes(await withRetry(() => getDatasetScenes())); }
    catch (err) { console.error(err); }
    finally { setLibraryLoading(false); }
  };

  const selectScene = async (scene: DatasetScene) => {
    const id = investigationId(scene);
    setSelectedScene(id);
    setShowLibrary(false);
    setSceneLoading(true);
    setError(null);
    try { setInvestigation(await withRetry(() => getInvestigation(id))); }
    catch (err) { console.error(err); setError(`Processed result ${id} could not be loaded.`); }
    finally { setSceneLoading(false); }
  };

  const copyBrief = async () => {
    if (!investigation) return;
    const text = [
      `OCEANNOVA INVESTIGATION BRIEF — ${selectedScene}`,
      `Satellite: Sentinel-1 SAR | AI: Lightweight U-Net + look-alike filtering`,
      `Footprint: ${investigation.area_km2.toFixed(2)} km² | Mean AI confidence: ${(investigation.confidence * 100).toFixed(1)}%`,
      `Centroid: ${investigation.centroid.lat.toFixed(5)}°, ${investigation.centroid.lon.toFixed(5)}°`,
      `Perimeter estimate: ${investigation.characterization.perimeter_estimate_km?.toFixed(2) ?? "N/A"} km`,
      `Evidence status: real satellite + derived AI geometry; historical AIS and environmental forcing are not loaded.`,
      `Decision note: candidate attribution requires independent corroboration and is not legal proof.`,
    ].join("\n");
    try { await navigator.clipboard.writeText(text); setBriefCopied(true); setTimeout(() => setBriefCopied(false), 1800); }
    catch { setBriefCopied(false); }
  };

  if (loading) return <div className="loading-screen"><div className="loading-card"><div className="loading-orbit"><span /></div><strong>Loading OCEANNOVA</strong><p>Building the evidence workspace…</p></div></div>;
  if (error || !investigation) return <div className="loading-screen"><div className="loading-card error-card"><div className="error-symbol">!</div><strong>{error ?? "No investigation available."}</strong><p>The system will recover automatically when the service is reachable.</p><button onClick={() => window.location.reload()}>Try again</button></div></div>;

  const confidence = investigation.confidence * 100;
  const perimeter = investigation.characterization.perimeter_estimate_km;
  const source = "Sentinel-1 SAR";
  const crs = "EPSG:32616";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block"><img src="/oceannova-mark.png" alt="OCEANNOVA" className="brand-logo-image" /><div><strong>OCEANNOVA</strong><span>Marine Intelligence Platform</span></div></div>
        <div className="topbar-center"><span className="live-dot" /> Evidence Command Center <b>•</b> {sceneLoading ? "Loading observation" : "Workspace ready"}</div>
        <div className="top-actions"><button onClick={() => setShowEvidence(true)}>Evidence</button><button onClick={copyBrief}>{briefCopied ? "Copied" : "Brief"}</button><div className="avatar">O</div></div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div><p className="side-label">MISSION CONTROL</p><button className="nav-item active"><span>⌂</span>Overview</button><button className="nav-item" onClick={openLibrary}><span>◈</span>Scene Library</button><button className="nav-item" onClick={() => setShowEvidence(true)}><span>◉</span>Evidence Chain</button><button className="nav-item" onClick={copyBrief}><span>▤</span>Investigation Brief</button><button className="nav-item"><span>⌖</span>Map Workspace</button></div>
          <div className="sidebar-bottom"><div className="side-ocean-art"><div className="mini-globe" /><span>Evidence first.<br />Decisions with context.</span></div><button className="nav-item"><span>⚙</span>Settings</button><button className="nav-item"><span>?</span>Help</button></div>
        </aside>

        <main className="content">
          <section className="hero competition-hero"><div className="hero-copy"><span className="kicker">MARITIME FORENSICS • EVIDENCE-FIRST AI</span><h1>From radar signal<br /><em>to an investigation.</em></h1><p>OCEANNOVA converts a satellite observation into an explainable evidence chain — showing what is real, what is AI-derived, and what still needs external corroboration.</p><div className="hero-actions"><button className="primary-cta" onClick={openLibrary}>Explore observations <span>→</span></button><button className="hero-secondary" onClick={() => setShowEvidence(true)}>See evidence chain</button></div><div className="hero-trust"><span>✓ REAL SAR</span><span>✓ AI-DERIVED GEOMETRY</span><span>◌ EXTERNAL DATA READY</span></div></div><div className="hero-visual" aria-hidden="true"><div className="glow glow-one" /><div className="glow glow-two" /><div className="ocean-globe"><div className="globe-grid" /><div className="globe-land land-one" /><div className="globe-land land-two" /><div className="globe-pulse" /></div><div className="float-card float-top"><span>AI CONFIDENCE</span><strong>{confidence.toFixed(1)}%</strong><small>selected footprint</small></div><div className="float-card float-bottom"><span>DETECTED FOOTPRINT</span><strong>{investigation.area_km2.toFixed(2)} km²</strong><small>geo-referenced prediction</small></div><div className="orbit-label">EVIDENCE<br /><b>01</b></div></div></section>

          <section className="stats-row"><div className="stat-card accent-cyan"><span className="stat-icon">◈</span><div><small>SATELLITE EVIDENCE</small><strong>REAL SAR</strong><p>{source} observation</p></div></div><div className="stat-card accent-coral"><span className="stat-icon">●</span><div><small>DETECTED FOOTPRINT</small><strong>{investigation.area_km2.toFixed(2)} km²</strong><p>AI-predicted area</p></div></div><div className="stat-card accent-purple"><span className="stat-icon">⌁</span><div><small>MODEL SIGNAL</small><strong>{confidence.toFixed(1)}%</strong><p>Mean confidence on mask</p></div></div><div className="stat-card accent-green"><span className="stat-icon">✓</span><div><small>PROVENANCE</small><strong>{crs}</strong><p>Geo-referenced output</p></div></div></section>

          <section className="evidence-strip"><div className="evidence-strip-head"><div><span className="section-kicker">THE DIFFERENTIATOR</span><h2>We show the evidence — not just the answer.</h2></div><button onClick={() => setShowEvidence(true)}>Open full chain ↗</button></div><div className="evidence-chain">{evidenceLayers.map((layer, index) => <div className="chain-node" key={layer.key}><div className={`chain-dot ${layer.tone}`}>{String(index + 1).padStart(2, "0")}</div><div><strong>{layer.label}</strong><span>{layer.detail}</span></div><b className={`status-chip ${layer.tone}`}>{layer.status}</b>{index < evidenceLayers.length - 1 && <i className="chain-line" />}</div>)}</div></section>

          <section className="workspace-grid"><div className="map-panel card"><div className="card-header"><div><span className="section-kicker">GEOSPATIAL EVIDENCE</span><h2>Investigation map</h2></div><button className="scene-pill" onClick={openLibrary}>{selectedScene}<span>⌄</span></button></div><div className="map-frame"><MapView investigation={investigation} /></div></div><div className="insight-column"><section className="card insight-card"><div className="card-header"><div><span className="section-kicker">AI FINDING</span><h2>What the model found</h2></div><span className="risk-badge">Potential spill</span></div><div className="result-score"><div className="score-ring" style={{ "--score": `${confidence * 3.6}deg` } as CSSProperties}><span>{confidence.toFixed(0)}<small>%</small></span></div><div><strong>High-confidence radar signal</strong><p>Segmentation identified a potential slick footprint in the selected observation.</p></div></div><div className="data-list"><div><span>Center</span><strong>{investigation.centroid.lat.toFixed(4)}° N, {Math.abs(investigation.centroid.lon).toFixed(4)}° W</strong></div><div><span>Area</span><strong>{investigation.area_km2.toFixed(4)} km²</strong></div><div><span>Perimeter</span><strong>{perimeter != null ? `${perimeter.toFixed(2)} km` : "N/A"}</strong></div><div><span>Coordinate system</span><strong>{crs}</strong></div></div><div className="evidence-note"><span>i</span><p>These measurements come from the processed AI mask. They describe the prediction, not ground-truth area.</p></div><div className="button-row"><button className="primary-small" onClick={openLibrary}>Choose another</button><button className="secondary-small" onClick={() => setShowEvidence(true)}>Audit evidence ↗</button></div></section><section className="card signal-card"><div className="card-header"><div><span className="section-kicker">TRANSPARENCY</span><h2>Evidence readiness</h2></div></div><div className="readiness-meter"><div><span>Core satellite investigation</span><b>READY</b></div><div className="meter"><i style={{ width: "100%" }} /></div></div><div className="signal-row"><i className="signal-green" /><div><strong>Radar segmentation</strong><span>Real Sentinel-1 evidence</span></div><b>✓</b></div><div className="signal-row"><i className="signal-blue" /><div><strong>Geometry & GeoJSON</strong><span>Derived from prediction mask</span></div><b>✓</b></div><div className="signal-row muted"><i /><div><strong>Historical AIS</strong><span>Not loaded for this case</span></div><b>—</b></div><div className="signal-row muted"><i /><div><strong>Ocean forcing</strong><span>Not loaded for this case</span></div><b>—</b></div></section></div></section>

          <section className="forensic-panel"><div className="forensic-copy"><span className="section-kicker">FORENSIC WORKFLOW</span><h2>Every conclusion has a trace.</h2><p>Open the evidence chain to show a judge exactly how OCEANNOVA moves from pixels to a defensible investigation — without hiding the limits of the current demo.</p></div><div className="forensic-steps"><div><b>01</b><strong>Observe</strong><span>Satellite SAR</span></div><div><b>02</b><strong>Segment</strong><span>U-Net inference</span></div><div><b>03</b><strong>Characterize</strong><span>Geometry</span></div><div><b>04</b><strong>Correlate</strong><span>AIS + drift ready</span></div></div><button className="forensic-button" onClick={() => setShowEvidence(true)}>Inspect chain <span>→</span></button></section>

          <section className="bottom-banner"><div className="banner-icon">✦</div><div><span className="section-kicker">COMPETITION MODE</span><h3>Bring the evidence into the room.</h3><p>Use the Scene Library for another observation or copy a one-page investigation brief for your presentation.</p></div><button onClick={copyBrief}>{briefCopied ? "Brief copied ✓" : "Copy brief →"}</button></section>
        </main>
      </div>

      {showEvidence && <div className="modal-backdrop" onClick={() => setShowEvidence(false)}><section className="evidence-modal" onClick={(event) => event.stopPropagation()}><div className="library-head"><div><span className="section-kicker">AUDIT VIEW • {selectedScene}</span><h2>Evidence Chain</h2><p>One screen that separates measured evidence, AI-derived results and demo-ready integrations.</p></div><button className="close-btn" onClick={() => setShowEvidence(false)}>×</button></div><div className="audit-grid">{evidenceLayers.map((layer, index) => <article className="audit-card" key={layer.key}><div className={`audit-number ${layer.tone}`}>{String(index + 1).padStart(2, "0")}</div><div><span className={`status-chip ${layer.tone}`}>{layer.status}</span><h3>{layer.label}</h3><p>{layer.detail}</p>{layer.key === "satellite" && <small>Source: {source}<br />CRS: {crs}</small>}{layer.key === "ai" && <small>Method: Lightweight U-Net<br />Output: predicted spill mask</small>}{layer.key === "geometry" && <small>Area: {investigation.area_km2.toFixed(2)} km²<br />Perimeter: {perimeter?.toFixed(2) ?? "N/A"} km</small>}{layer.key === "drift" && <small>Real environmental forcing is not loaded in this case.</small>}{layer.key === "ais" && <small>No historical vessel evidence is claimed here. Candidate layers must be corroborated with authoritative AIS.</small>}</div></article>)}</div><div className="audit-footer"><strong>Integrity rule</strong><span>OCEANNOVA never presents representative AIS or prototype forcing as historical evidence.</span><button onClick={copyBrief}>{briefCopied ? "Copied" : "Copy investigation brief"}</button></div></section></div>}

      {showLibrary && <div className="modal-backdrop" onClick={() => setShowLibrary(false)}><section className="library-modal" onClick={(event) => event.stopPropagation()}><div className="library-head"><div><span className="section-kicker">PROCESSED RADAR OBSERVATIONS</span><h2>Scene Library</h2><p>{libraryLoading ? "Loading observations…" : "Choose an observation to open its investigation."}</p></div><button className="close-btn" onClick={() => setShowLibrary(false)}>×</button></div><div className="library-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by scene or filename" /><span>Processed evidence</span></div><div className="library-grid">{filteredScenes.map((scene) => { const id = investigationId(scene); return <button key={`${scene.split}-${scene.scene_id}`} className={`library-card ${selectedScene === id ? "selected" : ""}`} onClick={() => selectScene(scene)}><div className="scene-thumb"><span>◎</span><small>SAR</small></div><div className="library-info"><div><strong>{scene.scene_id}</strong><span>{scene.has_mask ? "IMAGE + MASK" : "IMAGE"}</span></div><p>{scene.file}</p><small>{scene.split.toUpperCase()} • Sentinel-1A GRD VV</small><em>Open investigation →</em></div></button>; })}</div><div className="library-foot"><span>OCEANNOVA</span> • Radar_data • U-Net segmentation & characterization • Evidence-first presentation</div></section></div>}
    </div>
  );
}

export default App;
