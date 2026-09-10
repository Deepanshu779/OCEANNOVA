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
  { id: "SP-002", date: "2018-10-08", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-003", date: "2018-10-21", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-004", date: "2018-11-02", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-005", date: "2018-11-17", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-006", date: "2019-01-13", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-007", date: "2019-02-04", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-008", date: "2019-03-19", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-009", date: "2019-04-11", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-010", date: "2019-05-26", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-011", date: "2019-07-08", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-012", date: "2019-08-22", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-013", date: "2019-09-15", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-014", date: "2019-10-03", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-015", date: "2019-11-18", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-016", date: "2020-01-07", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-017", date: "2020-02-16", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-018", date: "2020-03-29", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-019", date: "2020-05-10", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-020", date: "2020-06-24", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-021", date: "2020-08-03", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-022", date: "2020-09-17", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
  { id: "SP-023", date: "2020-11-05", satellite: "Sentinel-1A GRD VV", region: "Gulf of Mexico", status: "AVAILABLE" },
];

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedVessel, setSelectedVessel] = useState<Vessel | null>(null);
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

  if (loading) {
    return <div className="loading-screen"><div><div className="loading-mark">O</div><strong>Loading OCEANNOVA</strong><span>Connecting to investigation API…</span></div></div>;
  }

  if (error || !investigation) {
    return <div className="loading-screen"><div><div className="loading-mark">!</div><strong>{error ?? "No investigation data available."}</strong><span>Start the FastAPI backend and refresh the dashboard.</span></div></div>;
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-logo">O</div>
          <div>
            <h1>OCEANNOVA</h1>
            <span>Marine Oil Spill Intelligence Platform</span>
          </div>
        </div>
        <div className="topbar-meta">
          <span className="live-dot" />
          <span>SYSTEM ONLINE</span>
          <button className="dataset-button" onClick={() => setShowDatasets(true)}>DATASET <b>23</b></button>
          <span className="topbar-divider" />
          <span>SIH26143</span>
        </div>
      </header>

      <main className="dashboard">
        <Sidebar investigation={investigation} onSelectVessel={setSelectedVessel} />
        <section className="map-container">
          <MapView investigation={investigation} selectedVessel={selectedVessel} />
          <div className="map-status-card">
            <strong>Investigation Map</strong>
            <span>DETECT → TRACE → CORRELATE → RANK</span>
          </div>
        </section>
      </main>

      {showDatasets && (
        <div className="dataset-overlay" onClick={() => setShowDatasets(false)}>
          <section className="dataset-panel" onClick={(event) => event.stopPropagation()}>
            <div className="dataset-header">
              <div>
                <span className="eyebrow">SATELLITE DATA INVENTORY</span>
                <h2>Oil-Spill Scene Library</h2>
                <p>23 Sentinel-1A GRD VV oil-spill scenes from the Gulf of Mexico dataset.</p>
              </div>
              <button className="dataset-close" onClick={() => setShowDatasets(false)}>×</button>
            </div>
            <div className="dataset-toolbar">
              <input value={datasetQuery} onChange={(event) => setDatasetQuery(event.target.value)} placeholder="Search scene or date…" />
              <span>{filteredScenes.length} / 23 scenes</span>
            </div>
            <div className="dataset-grid">
              {filteredScenes.map((scene) => (
                <button key={scene.id} className={`dataset-card ${scene.status === "FULL DEMO" ? "active" : ""}`} onClick={() => scene.id === "SP-001" && setShowDatasets(false)}>
                  <div className="dataset-card-top"><strong>{scene.id}</strong><span>{scene.status}</span></div>
                  <div className="dataset-date">{scene.date}</div>
                  <small>{scene.satellite}</small>
                  <small>{scene.region}</small>
                  {scene.id === "SP-001" && <em>Open full investigation →</em>}
                </button>
              ))}
            </div>
            <footer className="dataset-footer">SOURCE: Zenodo Oil Spill Segmentation • DOI 10.5281/zenodo.4672426 • Only SP-001 currently has the full end-to-end investigation demo.</footer>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
