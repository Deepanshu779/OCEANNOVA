import { useEffect, useMemo, useState } from "react";

import MapView from "./components/MapView";
import { getDatasetScenes, getInvestigation, type DatasetScene, type Investigation } from "./services/api";
import "./index.css";

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedScene, setSelectedScene] = useState("SP-001");
  const [scenes, setScenes] = useState<DatasetScene[]>([]);
  const [showDatasets, setShowDatasets] = useState(false);
  const [datasetQuery, setDatasetQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [sceneLoading, setSceneLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [datasetLoading, setDatasetLoading] = useState(false);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setError(null);
        const [data, inventory] = await Promise.all([
          getInvestigation("SP-001"),
          getDatasetScenes().catch(() => []),
        ]);
        setInvestigation(data);
        setScenes(inventory);
      } catch (err) {
        console.error(err);
        setError("Unable to connect to OCEANNOVA backend.");
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  const filteredScenes = useMemo(
    () => scenes.filter((scene) => `${scene.scene_id} ${scene.file} ${scene.split}`.toLowerCase().includes(datasetQuery.toLowerCase())),
    [scenes, datasetQuery]
  );

  const getInvestigationId = (scene: DatasetScene) => {
    const index = scenes.findIndex((item) => item.split === scene.split && item.scene_id === scene.scene_id);
    return index >= 0 ? `SP-${String(index + 1).padStart(3, "0")}` : "SP-001";
  };

  const openDatasets = async () => {
    setShowDatasets(true);
    if (scenes.length) return;
    setDatasetLoading(true);
    try {
      setScenes(await getDatasetScenes());
    } catch (err) {
      console.error(err);
    } finally {
      setDatasetLoading(false);
    }
  };

  const selectScene = async (scene: DatasetScene) => {
    const investigationId = getInvestigationId(scene);
    setSelectedScene(investigationId);
    setShowDatasets(false);
    setError(null);
    setSceneLoading(true);
    try {
      setInvestigation(await getInvestigation(investigationId));
    } catch (err) {
      console.error(err);
      setError(`Unable to load processed Radar_data result for ${investigationId}.`);
    } finally {
      setSceneLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-screen"><div><div className="loading-mark">O</div><strong>Loading OCEANNOVA</strong><span>Connecting to the investigation service…</span></div></div>;
  }

  if (error || !investigation) {
    return <div className="loading-screen"><div><div className="loading-mark">!</div><strong>{error ?? "No investigation data available."}</strong><span>Check that the FastAPI service is running and refresh the dashboard.</span></div></div>;
  }

  const confidence = investigation.confidence * 100;
  const perimeter = investigation.characterization.perimeter_estimate_km;
  const compactness = investigation.characterization.compactness_estimate;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand-block">
          <img className="brand-logo-image" src="/oceannova-mark.png" alt="OCEANNOVA" />
          <div className="brand-copy"><h1>OCEANNOVA</h1><span>Cleaner Oceans, Safer Tomorrow</span></div>
        </div>
        <div className="product-title">Oil Spill Detection &amp; Investigation</div>
        <nav className="top-links"><button type="button">About</button><button type="button">Documentation</button><button type="button">Contact</button><span className="profile-chip">◯</span></nav>
      </header>

      <div className="workspace">
        <aside className="app-nav">
          <div className="nav-group">
            <button type="button" className="nav-item active"><span>⌂</span>Dashboard</button>
            <button type="button" className="nav-item"><span>⌁</span>Radar Analysis</button>
            <button type="button" className="nav-item"><span>⌕</span>Spill Investigation</button>
            <button type="button" className="nav-item"><span>▤</span>Data &amp; Reports</button>
            <button type="button" className="nav-item"><span>◫</span>Map Viewer</button>
          </div>
          <div className="nav-bottom">
            <button type="button" className="nav-item"><span>⚙</span>Settings</button>
            <button type="button" className="nav-item"><span>?</span>Help</button>
            <div className="nav-brand-note"><div className="wave-mark">〰</div><strong>Cleaner Oceans</strong><span>Safer Tomorrow</span></div>
            <small>© 2026 OCEANNOVA<br />All rights reserved.</small>
          </div>
        </aside>

        <main className="content">
          <div className="content-header">
            <div><p className="eyebrow">OCEAN MONITORING WORKSPACE</p><h2>Dashboard</h2><p>Select a radar scene to inspect its detection and processed evidence.</p></div>
            <div className="header-status"><span className="online-dot" />System Online</div>
          </div>

          <div className="metric-grid">
            <div className="metric-card"><span className="metric-icon">▱</span><div><span>Current Scene</span><strong>{selectedScene}</strong><small>Selected radar scene</small></div></div>
            <div className="metric-card"><span className="metric-icon">●</span><div><span>Detection</span><strong>{sceneLoading ? "Loading" : "Ready"}</strong><small>Processed model output</small></div></div>
            <div className="metric-card"><span className="metric-icon">⌖</span><div><span>Location</span><strong>Mapped</strong><small>Geo-referenced footprint</small></div></div>
            <div className="metric-card"><span className="metric-icon">▤</span><div><span>Evidence</span><strong>Available</strong><small>Characterization output</small></div></div>
          </div>

          <div className="main-grid">
            <section className="panel map-panel">
              <div className="panel-heading"><div><p className="eyebrow">SPATIAL ANALYSIS</p><h3>Map View</h3></div><button type="button" className="scene-select" onClick={openDatasets}>{selectedScene} <span>⌄</span></button></div>
              <div className="map-frame"><MapView investigation={investigation} /></div>
            </section>

            <section className="panel details-panel">
              <div className="panel-heading"><div><p className="eyebrow">SELECTED DETECTION</p><h3>Scene Details</h3></div><span className="status-pill">Potential Spill Detected</span></div>
              <div className="scene-title-row"><strong>{selectedScene}</strong><span>{sceneLoading ? "Loading…" : "REAL RADAR DATA"}</span></div>
              <dl className="detail-list">
                <div><dt>Scene</dt><dd>{investigation.spill_id}</dd></div>
                <div><dt>Location (Center)</dt><dd>{investigation.centroid.lat.toFixed(4)}° N, {Math.abs(investigation.centroid.lon).toFixed(4)}° W</dd></div>
                <div><dt>Detected Area</dt><dd>{investigation.area_km2.toFixed(4)} km²</dd></div>
                <div><dt>Perimeter</dt><dd>{perimeter != null ? `${perimeter.toFixed(2)} km` : "N/A"}</dd></div>
                <div><dt>AI Confidence</dt><dd>{confidence.toFixed(1)}%</dd></div>
                <div><dt>Compactness</dt><dd>{compactness != null ? compactness.toFixed(4) : "N/A"}</dd></div>
              </dl>
              <div className="details-note">Single-scene SAR output. Spill age, ocean drift and vessel attribution are not inferred here.</div>
              <div className="detail-buttons"><button type="button" className="primary-button">▤ View Full Report</button><button type="button" className="secondary-button" onClick={() => window.open(`/data/${selectedScene}_spill.geojson`, "_blank")}>⇩ Download GeoJSON</button></div>
            </section>
          </div>

          <div className="bottom-grid">
            <section className="panel compact-panel"><div className="panel-heading"><h3>Recent Detection</h3><button type="button" className="text-button" onClick={openDatasets}>Open Scene Library</button></div><button type="button" className="detection-row" onClick={openDatasets}><span className="detection-dot" /><div><strong>{selectedScene}</strong><small>Real processed Radar_data scene</small><span>Potential oil spill detected</span></div><b>›</b></button></section>
            <section className="panel compact-panel"><div className="panel-heading"><h3>System Status</h3></div><div className="status-row"><i /> <div><strong>Model Ready</strong><span>U-Net model pipeline configured</span></div></div><div className="status-row"><i /> <div><strong>Data Pipeline</strong><span>Processed scene output available</span></div></div></section>
            <section className="panel compact-panel"><div className="panel-heading"><h3>Quick Actions</h3></div><button type="button" className="quick-button" onClick={openDatasets}>↥ Open Scene Library</button><button type="button" className="quick-button" onClick={openDatasets}>▤ Browse Processed Results</button></section>
          </div>
        </main>
      </div>

      {showDatasets && (
        <div className="dataset-overlay" onClick={() => setShowDatasets(false)}>
          <section className="dataset-panel" onClick={(event) => event.stopPropagation()}>
            <div className="dataset-header"><div><span className="eyebrow">RADAR DATA</span><h2>Scene Library</h2><p>{datasetLoading ? "Reading processed scenes…" : "Select a processed radar scene to begin an investigation."}</p></div><button type="button" className="dataset-close" onClick={() => setShowDatasets(false)}>×</button></div>
            <div className="dataset-toolbar"><input value={datasetQuery} onChange={(event) => setDatasetQuery(event.target.value)} placeholder="Search scene or filename…" /><span>Select a scene</span></div>
            <div className="dataset-grid">{filteredScenes.map((scene) => { const id = getInvestigationId(scene); return <button type="button" key={`${scene.split}-${scene.scene_id}`} className={`dataset-card ${selectedScene === id ? "selected" : ""}`} onClick={() => selectScene(scene)}><div className="dataset-card-top"><strong>{id}</strong><span>{scene.has_mask ? "REAL + MASK" : "REAL IMAGE"}</span></div><div className="dataset-date">{scene.scene_id}</div><small>{scene.file}</small><small>{scene.split.toUpperCase()} • Sentinel-1A GRD VV</small><em>Open processed investigation →</em></button>; })}</div>
            <footer className="dataset-footer">SOURCE: processed Radar_data • U-Net segmentation, filtering, characterization and GeoJSON outputs.</footer>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
