import { useEffect, useMemo, useState } from "react";

import MapView from "./components/MapView";
import Sidebar from "./components/Sidebar";
import { getInvestigation, type Investigation, type Vessel } from "./services/api";
import "./index.css";

type DatasetScene = {
  id: string;
  date: string;
  satellite: string;
  region: string;
  status: "FULL DEMO" | "AVAILABLE";
};

const DATASET_SCENES: DatasetScene[] = [
  { id: "SP-001", date: "2018-09-26", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "FULL DEMO" },
  ...Array.from({ length: 22 }, (_, index) => ({
    id: `SP-${String(index + 2).padStart(3, "0")}`,
    date: "Dataset scene",
    satellite: "Sentinel-1A GRD VV",
    region: "Gulf of Mexico",
    status: "AVAILABLE" as const,
  })),
];

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedVessel, setSelectedVessel] = useState<Vessel | null>(null);
  const [selectedScene, setSelectedScene] = useState("SP-001");
  const [showDatasets, setShowDatasets] = useState(false);
  const [datasetQuery, setDatasetQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadInvestigation() {
      try {
        setError(null);
        const data = await getInvestigation("SP-001");
        setInvestigation(data);
        setSelectedVessel(data.vessels[0] ?? null);
      } catch (err) {
        console.error(err);
        setError("Unable to connect to OCEANNOVA backend.");
      } finally {
        setLoading(false);
      }
    }
    loadInvestigation();
  }, []);

  const filteredScenes = useMemo(
    () => DATASET_SCENES.filter((scene) => `${scene.id} ${scene.date}`.toLowerCase().includes(datasetQuery.toLowerCase())),
    [datasetQuery]
  );

  const selectScene = (scene: DatasetScene) => {
    setSelectedScene(scene.id);
    setShowDatasets(false);
    if (scene.id === "SP-001") return;
    setError(null);
  };

  if (loading) {
    return <div className="loading-screen"><div><div className="loading-mark">O</div><strong>Loading OCEANNOVA</strong><span>Connecting to investigation API…</span></div></div>;
  }

  if (error || !investigation) {
    return <div className="loading-screen"><div><div className="loading-mark">!</div><strong>{error ?? "No investigation data available."}</strong><span>Start the FastAPI backend and refresh the dashboard.</span></div></div>;
  }

  const isFullDemo = selectedScene === "SP-001";

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-logo">O</div>
          <div><h1>OCEANNOVA</h1><span>Marine Oil Spill Intelligence Platform</span></div>
        </div>
        <div className="topbar-meta">
          <span className="live-dot" /><span>SYSTEM ONLINE</span>
          <button className="dataset-button" onClick={() => setShowDatasets(true)}>DATASET <b>23</b></button>
          <span className="topbar-divider" /><span>SIH26143</span>
        </div>
      </header>

      {!isFullDemo && (
        <div className="scene-banner">
          <strong>{selectedScene}</strong>
          <span>Source scene selected • full AI investigation is not processed for this scene yet</span>
          <button onClick={() => { setSelectedScene("SP-001"); }}>Return to SP-001 demo</button>
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
              <div><span className="eyebrow">SATELLITE DATA INVENTORY</span><h2>Oil-Spill Scene Library</h2><p>23 Sentinel-1A GRD VV scenes available in the source dataset.</p></div>
              <button className="dataset-close" onClick={() => setShowDatasets(false)}>×</button>
            </div>
            <div className="dataset-toolbar"><input value={datasetQuery} onChange={(event) => setDatasetQuery(event.target.value)} placeholder="Search scene or date…" /><span>{filteredScenes.length} / 23 scenes</span></div>
            <div className="dataset-grid">
              {filteredScenes.map((scene) => (
                <button key={scene.id} className={`dataset-card ${selectedScene === scene.id ? "selected" : ""} ${scene.status === "FULL DEMO" ? "active" : ""}`} onClick={() => selectScene(scene)}>
                  <div className="dataset-card-top"><strong>{scene.id}</strong><span>{scene.status}</span></div>
                  <div className="dataset-date">{scene.date}</div><small>{scene.satellite}</small><small>{scene.region}</small>
                  <em>{scene.id === "SP-001" ? "Open full investigation →" : "Select scene →"}</em>
                </button>
              ))}
            </div>
            <footer className="dataset-footer">SOURCE: Zenodo Oil Spill Segmentation • Only SP-001 currently has the full end-to-end investigation pipeline.</footer>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
