import { useEffect, useMemo, useState } from "react";

import MapView from "./components/MapView";
import Sidebar from "./components/Sidebar";
import { getDatasetScenes, getInvestigation, type DatasetScene, type Investigation, type Vessel } from "./services/api";
import "./index.css";

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedVessel, setSelectedVessel] = useState<Vessel | null>(null);
  const [selectedScene, setSelectedScene] = useState("SP-001");
  const [scenes, setScenes] = useState<DatasetScene[]>([]);
  const [showDatasets, setShowDatasets] = useState(false);
  const [datasetQuery, setDatasetQuery] = useState("");
  const [loading, setLoading] = useState(true);
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
        setSelectedVessel(data.vessels[0] ?? null);
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

  const selectScene = (scene: DatasetScene) => {
    // The inventory is now sourced from the actual Radar_data folder.
    // SP-001 remains the only completed end-to-end investigation until
    // its corresponding scene has been processed into an investigation record.
    const index = scenes.findIndex((item) => item.scene_id === scene.scene_id);
    setSelectedScene(`SP-${String(index + 1).padStart(3, "0")}`);
    setShowDatasets(false);
    setError(null);
  };

  if (loading) {
    return <div className="loading-screen"><div><div className="loading-mark">O</div><strong>Loading OCEANNOVA</strong><span>Connecting to investigation API…</span></div></div>;
  }

  if (error || !investigation) {
    return <div className="loading-screen"><div><div className="loading-mark">!</div><strong>{error ?? "No investigation data available."}</strong><span>Start the FastAPI backend and refresh the dashboard.</span></div></div>;
  }

  const isFullDemo = selectedScene === "SP-001";
  const datasetCount = scenes.length || 23;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-logo">O</div>
          <div><h1>OCEANNOVA</h1><span>Marine Oil Spill Intelligence Platform</span></div>
        </div>
        <div className="topbar-meta">
          <span className="live-dot" /><span>SYSTEM ONLINE</span>
          <button className="dataset-button" onClick={openDatasets}>DATASET <b>{datasetCount}</b></button>
          <span className="topbar-divider" /><span>SIH26143</span>
        </div>
      </header>

      {!isFullDemo && (
        <div className="scene-banner">
          <strong>{selectedScene}</strong>
          <span>Source scene selected • inventory verified from local Radar_data</span>
          <button onClick={() => setSelectedScene("SP-001")}>Return to SP-001 demo</button>
        </div>
      )}

      <main className="dashboard">
        <Sidebar investigation={investigation} onSelectVessel={setSelectedVessel} />
        <section className="map-container">
          <MapView investigation={investigation} selectedVessel={selectedVessel} />
          <div className="map-status-card">
            <strong>{selectedScene} • Investigation Map</strong>
            <span>{isFullDemo ? "DETECT → TRACE → CORRELATE → RANK" : "SCENE SELECTED → PROCESSING REQUIRED"}</span>
          </div>
        </section>
      </main>

      {showDatasets && (
        <div className="dataset-overlay" onClick={() => setShowDatasets(false)}>
          <section className="dataset-panel" onClick={(event) => event.stopPropagation()}>
            <div className="dataset-header">
              <div><span className="eyebrow">SATELLITE DATA INVENTORY</span><h2>Oil-Spill Scene Library</h2><p>{datasetLoading ? "Reading Radar_data from backend…" : `${scenes.length || 23} scenes discovered from the Radar_data folder.`}</p></div>
              <button className="dataset-close" onClick={() => setShowDatasets(false)}>×</button>
            </div>
            <div className="dataset-toolbar"><input value={datasetQuery} onChange={(event) => setDatasetQuery(event.target.value)} placeholder="Search scene or filename…" /><span>{filteredScenes.length} / {scenes.length || 23} scenes</span></div>
            <div className="dataset-grid">
              {filteredScenes.map((scene, index) => {
                const investigationId = `SP-${String(index + 1).padStart(3, "0")}`;
                const complete = investigationId === "SP-001";
                return (
                  <button key={`${scene.split}-${scene.scene_id}`} className={`dataset-card ${selectedScene === investigationId ? "selected" : ""} ${complete ? "active" : ""}`} onClick={() => selectScene(scene)}>
                    <div className="dataset-card-top"><strong>{investigationId}</strong><span>{complete ? "FULL DEMO" : scene.has_mask ? "RAW + MASK" : "IMAGE ONLY"}</span></div>
                    <div className="dataset-date">{scene.scene_id}</div><small>{scene.file}</small><small>{scene.split.toUpperCase()} • Sentinel-1A GRD VV</small>
                    <em>{complete ? "Open full investigation →" : "Select source scene →"}</em>
                  </button>
                );
              })}
              {!datasetLoading && scenes.length === 0 && <div className="dataset-empty">No Radar_data scenes are visible to the running backend. The local folder must be present in the backend runtime.</div>}
            </div>
            <footer className="dataset-footer">SOURCE: Zenodo Oil Spill Segmentation • Inventory is read from the actual backend Radar_data directory; only processed scenes expose a full investigation.</footer>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
