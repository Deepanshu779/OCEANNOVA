import { useEffect, useMemo, useState } from "react";

import MapView from "./components/MapView";
import { getDatasetScenes, getInvestigation, type DatasetScene, type Investigation } from "./services/api";
import "./index.css";

const visualPolish = `
  .app { background: #f4f7f8 !important; }
  .topbar { height: 72px !important; padding: 0 30px !important; box-shadow: 0 1px 0 rgba(17,40,55,.05); }
  .brand-logo-image { width: 46px !important; height: 46px !important; }
  .brand-copy h1 { font-size: 18px !important; letter-spacing: .06em !important; }
  .product-title { color: #163f55 !important; font-size: 13px !important; }
  .workspace { min-height: calc(100vh - 72px); }
  .app-nav { width: 218px !important; flex-basis: 218px !important; background: #102b3a !important; padding-top: 24px !important; }
  .nav-item { min-height: 44px !important; border-radius: 8px !important; border-left: 0 !important; margin: 1px 0 !important; }
  .nav-item.active { background: #1d536b !important; box-shadow: inset 0 0 0 1px rgba(125,205,232,.16); }
  .content { padding: 30px 34px 38px !important; }
  .content-header { margin-bottom: 24px !important; }
  .content-header h2 { font-size: 31px !important; letter-spacing: -.035em !important; }
  .content-header > div:first-child > p:last-child { font-size: 13px !important; max-width: 600px; }
  .metric-grid { gap: 14px !important; margin-bottom: 18px !important; }
  .metric-card { min-height: 100px !important; border-radius: 10px !important; border-color: #dce6ea !important; box-shadow: 0 3px 14px rgba(24,53,68,.055); transition: transform .18s ease, box-shadow .18s ease; }
  .metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(24,53,68,.09); }
  .metric-icon { width: 38px !important; height: 38px !important; border-radius: 9px !important; background: #e8f4f7 !important; color: #1c7898 !important; }
  .metric-card strong { font-size: 21px !important; }
  .main-grid { gap: 18px !important; grid-template-columns: minmax(0, 1.85fr) minmax(320px, .78fr) !important; }
  .panel { border-radius: 10px !important; border-color: #dbe4e8 !important; box-shadow: 0 4px 18px rgba(24,53,68,.045); }
  .panel-heading { min-height: 62px !important; padding: 0 19px !important; }
  .panel-heading h3 { font-size: 15px !important; }
  .map-frame { height: 515px !important; }
  .scene-select { border-radius: 7px !important; padding: 8px 11px !important; }
  .status-pill { border-radius: 999px !important; padding: 6px 10px !important; }
  .details-note { border-radius: 7px; border-left-width: 0 !important; background: #edf7f8 !important; color: #54707d !important; }
  .primary-button, .secondary-button { border-radius: 7px !important; }
  .bottom-grid { gap: 14px !important; margin-top: 18px !important; }
  .compact-panel { border-radius: 10px !important; }
  .quick-button, .detection-row { border-radius: 7px !important; }
  .dataset-panel { border-radius: 12px !important; }
  .dataset-card { border-radius: 9px !important; }
  @media (max-width: 1050px) { .product-title { display: none; } .content { padding: 24px !important; } .main-grid { grid-template-columns: 1fr !important; } .map-frame { height: 430px !important; } }
  @media (max-width: 760px) { .app-nav { display: none; } .topbar { padding: 0 18px !important; } .top-links button { display: none; } .metric-grid { grid-template-columns: repeat(2, 1fr) !important; } .bottom-grid { grid-template-columns: 1fr !important; } }
`;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function retryRequest<T>(request: () => Promise<T>, attempts = 8): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      return await request();
    } catch (error) {
      lastError = error;
      if (attempt === attempts - 1) break;
      await sleep(Math.min(3000 + attempt * 1000, 8000));
    }
  }
  throw lastError instanceof Error ? lastError : new Error("Backend request failed");
}

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
    let cancelled = false;
    async function loadDashboard() {
      try {
        setError(null);
        const data = await retryRequest(() => getInvestigation("SP-001"));
        const inventory = await retryRequest(() => getDatasetScenes()).catch(() => [] as DatasetScene[]);
        if (cancelled) return;
        setInvestigation(data);
        setScenes(inventory);
      } catch (err) {
        console.error(err);
        if (!cancelled) setError("The investigation service is taking longer than expected. Please refresh once.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadDashboard();
    return () => { cancelled = true; };
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
    try { setScenes(await retryRequest(() => getDatasetScenes())); }
    catch (err) { console.error(err); }
    finally { setDatasetLoading(false); }
  };

  const selectScene = async (scene: DatasetScene) => {
    const investigationId = getInvestigationId(scene);
    setSelectedScene(investigationId);
    setShowDatasets(false);
    setError(null);
    setSceneLoading(true);
    try { setInvestigation(await retryRequest(() => getInvestigation(investigationId))); }
    catch (err) { console.error(err); setError(`Unable to load processed Radar_data result for ${investigationId}.`); }
    finally { setSceneLoading(false); }
  };

  if (loading) {
    return <div className="loading-screen"><div><div className="loading-mark">O</div><strong>Loading OCEANNOVA</strong><span>Connecting to the investigation service…</span></div></div>;
  }

  if (error || !investigation) {
    return <div className="loading-screen"><div><div className="loading-mark">!</div><strong>{error ?? "No investigation data available."}</strong><span>The service may be waking up. Refresh if this screen remains for more than a minute.</span></div></div>;
  }

  const confidence = investigation.confidence * 100;
  const perimeter = investigation.characterization.perimeter_estimate_km;
  const compactness = investigation.characterization.compactness_estimate;

  return (
    <div className="app">
      <style>{visualPolish}</style>
      <header className="topbar">
        <div className="brand-block">
          <img className="brand-logo-image" src="/oceannova-mark.png" alt="OCEANNOVA" />
          <div className="brand-copy"><h1>OCEANNOVA</h1><span>Cleaner Oceans, Safer Tomorrow</span></div>
        </div>
        <div className="product-title">Oil Spill Detection &amp; Investigation</div>
        <nav className="top-links"><button type="button">About</button><button type="button">Guide</button><button type="button">Contact</button></nav>
      </header>

      <div className="workspace">
        <aside className="app-nav">
          <div className="nav-group">
            <button type="button" className="nav-item active"><span>⌂</span>Overview</button>
            <button type="button" className="nav-item" onClick={openDatasets}><span>⌁</span>Radar Scenes</button>
            <button type="button" className="nav-item" onClick={openDatasets}><span>⌕</span>Investigations</button>
            <button type="button" className="nav-item"><span>▤</span>Reports</button>
            <button type="button" className="nav-item"><span>◫</span>Map</button>
          </div>
          <div className="nav-bottom">
            <button type="button" className="nav-item"><span>⚙</span>Settings</button>
            <button type="button" className="nav-item"><span>?</span>Help</button>
            <div className="nav-brand-note"><div className="wave-mark">〰</div><strong>Cleaner Oceans</strong><span>Safer Tomorrow</span></div>
            <small>OCEANNOVA</small>
          </div>
        </aside>

        <main className="content">
          <div className="content-header">
            <div><p className="eyebrow">MARINE MONITORING</p><h2>Good to see you.</h2><p>Choose a radar scene and inspect what the model finds. Everything you see below comes from the selected investigation.</p></div>
            <div className="header-status"><span className="online-dot" />System Online</div>
          </div>

          <div className="metric-grid">
            <div className="metric-card"><span className="metric-icon">⌁</span><div><span>Radar analysis</span><strong>Ready</strong><small>Open a scene to begin</small></div></div>
            <div className="metric-card"><span className="metric-icon">◉</span><div><span>Selected scene</span><strong>{selectedScene}</strong><small>Current investigation</small></div></div>
            <div className="metric-card"><span className="metric-icon">⌖</span><div><span>Spill footprint</span><strong>Mapped</strong><small>Geo-referenced result</small></div></div>
            <div className="metric-card"><span className="metric-icon">✓</span><div><span>Analysis</span><strong>{sceneLoading ? "Loading" : "Complete"}</strong><small>Processed model output</small></div></div>
          </div>

          <div className="main-grid">
            <section className="panel map-panel">
              <div className="panel-heading"><div><p className="eyebrow">WHERE</p><h3>Investigation Map</h3></div><button type="button" className="scene-select" onClick={openDatasets}>{selectedScene} <span>⌄</span></button></div>
              <div className="map-frame"><MapView investigation={investigation} /></div>
            </section>

            <section className="panel details-panel">
              <div className="panel-heading"><div><p className="eyebrow">WHAT WE FOUND</p><h3>Detection Details</h3></div><span className="status-pill">Potential spill</span></div>
              <div className="scene-title-row"><strong>{selectedScene}</strong><span>{sceneLoading ? "LOADING" : "RADAR RESULT"}</span></div>
              <dl className="detail-list">
                <div><dt>Center</dt><dd>{investigation.centroid.lat.toFixed(4)}° N, {Math.abs(investigation.centroid.lon).toFixed(4)}° W</dd></div>
                <div><dt>Detected area</dt><dd>{investigation.area_km2.toFixed(4)} km²</dd></div>
                <div><dt>Perimeter</dt><dd>{perimeter != null ? `${perimeter.toFixed(2)} km` : "N/A"}</dd></div>
                <div><dt>Model confidence</dt><dd>{confidence.toFixed(1)}%</dd></div>
                <div><dt>Shape index</dt><dd>{compactness != null ? compactness.toFixed(4) : "N/A"}</dd></div>
              </dl>
              <div className="details-note">The result above is derived from the selected Radar_data scene. Other evidence is added only when its supporting data is available.</div>
              <div className="detail-buttons"><button type="button" className="primary-button" onClick={openDatasets}>Choose another scene</button><button type="button" className="secondary-button" onClick={() => window.open(`/data/${selectedScene}_spill.geojson`, "_blank")}>Open GeoJSON</button></div>
            </section>
          </div>

          <div className="bottom-grid">
            <section className="panel compact-panel"><div className="panel-heading"><h3>Start an investigation</h3></div><button type="button" className="detection-row" onClick={openDatasets}><span className="detection-dot" /><div><strong>Choose a Radar scene</strong><small>Browse the processed satellite results</small><span>Open Scene Library</span></div><b>→</b></button></section>
            <section className="panel compact-panel"><div className="panel-heading"><h3>What is available</h3></div><div className="status-row"><i /><div><strong>Radar detection</strong><span>Segmentation and spill footprint</span></div></div><div className="status-row"><i /><div><strong>Scene measurements</strong><span>Area, perimeter and shape</span></div></div></section>
            <section className="panel compact-panel"><div className="panel-heading"><h3>Need another scene?</h3></div><button type="button" className="quick-button" onClick={openDatasets}>Browse Radar Scenes →</button><button type="button" className="quick-button" onClick={openDatasets}>Open Investigation →</button></section>
          </div>
        </main>
      </div>

      {showDatasets && (
        <div className="dataset-overlay" onClick={() => setShowDatasets(false)}>
          <section className="dataset-panel" onClick={(event) => event.stopPropagation()}>
            <div className="dataset-header"><div><span className="eyebrow">RADAR DATA</span><h2>Scene Library</h2><p>{datasetLoading ? "Reading processed scenes…" : "Select a processed radar scene to begin an investigation."}</p></div><button type="button" className="dataset-close" onClick={() => setShowDatasets(false)}>×</button></div>
            <div className="dataset-toolbar"><input value={datasetQuery} onChange={(event) => setDatasetQuery(event.target.value)} placeholder="Search scene or filename…" /><span>Select a scene</span></div>
            <div className="dataset-grid">{filteredScenes.map((scene) => { const id = getInvestigationId(scene); return <button type="button" key={`${scene.split}-${scene.scene_id}`} className={`dataset-card ${selectedScene === id ? "selected" : ""}`} onClick={() => selectScene(scene)}><div className="dataset-card-top"><strong>{scene.scene_id}</strong><span>{scene.has_mask ? "IMAGE + MASK" : "IMAGE"}</span></div><div className="dataset-date">{scene.scene_id}</div><small>{scene.file}</small><small>{scene.split.toUpperCase()} • Sentinel-1A GRD VV</small><em>Open processed investigation →</em></button>; })}</div>
            <footer className="dataset-footer">SOURCE: processed Radar_data • U-Net segmentation, filtering, characterization and GeoJSON outputs.</footer>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
