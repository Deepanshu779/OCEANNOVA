import { useEffect, useMemo, useState } from "react";
import MapView from "./components/MapView";
import { getDatasetScenes, getInvestigation, type DatasetScene, type Investigation } from "./services/api";
import "./index.css";

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedScene, setSelectedScene] = useState("SP-001");
  const [scenes, setScenes] = useState<DatasetScene[]>([]);
  const [showLibrary, setShowLibrary] = useState(false);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [sceneLoading, setSceneLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [libraryLoading, setLibraryLoading] = useState(false);

  async function withRetry<T>(task: () => Promise<T>, attempts = 4, delay = 900): Promise<T> {
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

  if (loading) return <div className="loading-screen"><div className="loading-card"><div className="loading-orbit"><span /></div><strong>Loading OCEANNOVA</strong><p>Connecting to marine intelligence services…</p></div></div>;
  if (error || !investigation) return <div className="loading-screen"><div className="loading-card error-card"><div className="error-symbol">!</div><strong>{error ?? "No investigation available."}</strong><p>The system will recover automatically when the service is reachable. Please try again.</p><button onClick={() => window.location.reload()}>Try again</button></div></div>;

  const confidence = investigation.confidence * 100;
  const perimeter = investigation.characterization.perimeter_estimate_km;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <img src="/oceannova-mark.png" alt="OCEANNOVA" className="brand-logo-image" />
          <div><strong>OCEANNOVA</strong><span>Marine Intelligence Platform</span></div>
        </div>
        <div className="topbar-center"><span className="live-dot" /> Mission Control <b>•</b> Live workspace</div>
        <div className="top-actions"><button>Guide</button><button>About</button><div className="avatar">O</div></div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div>
            <p className="side-label">WORKSPACE</p>
            <button className="nav-item active"><span>⌂</span>Overview</button>
            <button className="nav-item" onClick={openLibrary}><span>◈</span>Scene Library</button>
            <button className="nav-item"><span>◎</span>Investigations</button>
            <button className="nav-item"><span>▤</span>Reports</button>
            <button className="nav-item"><span>⌖</span>Map</button>
          </div>
          <div className="sidebar-bottom">
            <div className="side-ocean-art"><div className="mini-globe" /><span>Protecting the blue<br />with better intelligence.</span></div>
            <button className="nav-item"><span>⚙</span>Settings</button>
            <button className="nav-item"><span>?</span>Help</button>
          </div>
        </aside>

        <main className="content">
          <section className="hero">
            <div className="hero-copy">
              <span className="kicker">OCEAN OBSERVATION • AI POWERED</span>
              <h1>See the ocean.<br /><em>Understand the signal.</em></h1>
              <p>Turn satellite radar observations into a clear, visual investigation of potential oil-spill footprints.</p>
              <div className="hero-actions"><button className="primary-cta" onClick={openLibrary}>Explore scenes <span>→</span></button><span className="hero-note"><i />Analysis workspace ready</span></div>
            </div>
            <div className="hero-visual" aria-hidden="true">
              <div className="glow glow-one" /><div className="glow glow-two" />
              <div className="ocean-globe"><div className="globe-grid" /><div className="globe-land land-one" /><div className="globe-land land-two" /><div className="globe-pulse" /></div>
              <div className="float-card float-top"><span>AI CONFIDENCE</span><strong>{confidence.toFixed(1)}%</strong><small>selected footprint</small></div>
              <div className="float-card float-bottom"><span>FOOTPRINT</span><strong>{investigation.area_km2.toFixed(2)} km²</strong><small>geo-referenced</small></div>
            </div>
          </section>

          <section className="stats-row">
            <div className="stat-card accent-cyan"><span className="stat-icon">◈</span><div><small>SELECTED SCENE</small><strong>{selectedScene}</strong><p>Processed Sentinel-1 result</p></div></div>
            <div className="stat-card accent-coral"><span className="stat-icon">●</span><div><small>DETECTED FOOTPRINT</small><strong>{investigation.area_km2.toFixed(2)} km²</strong><p>Model-predicted area</p></div></div>
            <div className="stat-card accent-purple"><span className="stat-icon">⌁</span><div><small>MODEL CONFIDENCE</small><strong>{confidence.toFixed(1)}%</strong><p>Mean confidence on mask</p></div></div>
            <div className="stat-card accent-green"><span className="stat-icon">✓</span><div><small>PIPELINE STATUS</small><strong>{sceneLoading ? "Loading" : "Ready"}</strong><p>Detection & characterization</p></div></div>
          </section>

          <section className="workspace-grid">
            <div className="map-panel card">
              <div className="card-header"><div><span className="section-kicker">LIVE VIEW</span><h2>Investigation map</h2></div><button className="scene-pill" onClick={openLibrary}>{selectedScene}<span>⌄</span></button></div>
              <div className="map-frame"><MapView investigation={investigation} /></div>
            </div>
            <div className="insight-column">
              <section className="card insight-card">
                <div className="card-header"><div><span className="section-kicker">AI RESULT</span><h2>What we found</h2></div><span className="risk-badge">Potential spill</span></div>
                <div className="result-score"><div className="score-ring" style={{ "--score": `${confidence * 3.6}deg` } as React.CSSProperties}><span>{confidence.toFixed(0)}<small>%</small></span></div><div><strong>High-confidence signal</strong><p>AI segmentation identified a potential slick footprint in the selected radar observation.</p></div></div>
                <div className="data-list"><div><span>Center</span><strong>{investigation.centroid.lat.toFixed(4)}° N, {Math.abs(investigation.centroid.lon).toFixed(4)}° W</strong></div><div><span>Area</span><strong>{investigation.area_km2.toFixed(4)} km²</strong></div><div><span>Perimeter</span><strong>{perimeter != null ? `${perimeter.toFixed(2)} km` : "N/A"}</strong></div><div><span>Age</span><strong>Not available</strong></div></div>
                <div className="evidence-note"><span>i</span><p>Measurements are derived from the processed radar mask. Age requires additional temporal observations.</p></div>
                <div className="button-row"><button className="primary-small" onClick={openLibrary}>Choose another</button><button className="secondary-small" onClick={() => window.open(`/data/${selectedScene}_spill.geojson`, "_blank")}>GeoJSON ↗</button></div>
              </section>

              <section className="card signal-card"><div className="card-header"><div><span className="section-kicker">EVIDENCE LAYERS</span><h2>Analysis status</h2></div></div><div className="signal-row"><i className="signal-green" /><div><strong>Radar segmentation</strong><span>Available</span></div><b>✓</b></div><div className="signal-row"><i className="signal-blue" /><div><strong>Geometric characterization</strong><span>Available</span></div><b>✓</b></div><div className="signal-row muted"><i /><div><strong>Historical vessel evidence</strong><span>Not loaded</span></div><b>—</b></div></section>
            </div>
          </section>

          <section className="bottom-banner"><div className="banner-icon">✦</div><div><span className="section-kicker">NEXT STEP</span><h3>Start with a different observation</h3><p>Browse the processed library and open another scene without leaving the workspace.</p></div><button onClick={openLibrary}>Open library <span>→</span></button></section>
        </main>
      </div>

      {showLibrary && <div className="modal-backdrop" onClick={() => setShowLibrary(false)}><section className="library-modal" onClick={(event) => event.stopPropagation()}><div className="library-head"><div><span className="section-kicker">PROCESSED OBSERVATIONS</span><h2>Scene Library</h2><p>{libraryLoading ? "Loading observations…" : "Choose an observation to open its investigation."}</p></div><button className="close-btn" onClick={() => setShowLibrary(false)}>×</button></div><div className="library-toolbar"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by scene or filename" /><span>{filteredScenes.length} available</span></div><div className="library-grid">{filteredScenes.map((scene) => { const id = investigationId(scene); return <button key={`${scene.split}-${scene.scene_id}`} className={`library-card ${selectedScene === id ? "selected" : ""}`} onClick={() => selectScene(scene)}><div className="scene-thumb"><span>◎</span><small>SAR</small></div><div className="library-info"><div><strong>{scene.scene_id}</strong><span>{scene.has_mask ? "IMAGE + MASK" : "IMAGE"}</span></div><p>{scene.file}</p><small>{scene.split.toUpperCase()} • Sentinel-1A GRD VV</small><em>Open investigation →</em></div></button>; })}</div><div className="library-foot"><span>OCEANNOVA</span> • Processed Radar_data • U-Net segmentation & characterization</div></section></div>}
    </div>
  );
}

export default App;
