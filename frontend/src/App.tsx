import { useEffect, useMemo, useState } from "react";
import MapView from "./components/MapView";
import { getDatasetScenes, getInvestigation, type DatasetScene, type Investigation } from "./services/api";
import "./index.css";
import "./command-center.css";
import "./map-polish.css";

const demoVessels = [
  { name: "OCEAN STAR", score: 96.2, distance: 12.4, time: 2.1, anomaly: "Yes" },
  { name: "SEA HORIZON", score: 87.7, distance: 28.6, time: 3.4, anomaly: "Yes" },
  { name: "MARINE EXPRESS", score: 75.6, distance: 42.1, time: 5.2, anomaly: "Possible" },
  { name: "COASTAL TRADER", score: 54.3, distance: 67.8, time: 8.6, anomaly: "No" },
];

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [scenes, setScenes] = useState<DatasetScene[]>([]);
  const [selectedScene, setSelectedScene] = useState("SP-001");
  const [selectedFile, setSelectedFile] = useState("");
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [dark, setDark] = useState(true);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    Promise.all([getInvestigation("SP-001"), getDatasetScenes().catch(() => [])])
      .then(([data, inventory]) => {
        setInvestigation(data);
        setScenes(inventory);
        const first = inventory.find((s) => s.incident_id === "SP-001") ?? inventory[0];
        if (first) setSelectedFile(first.file);
      })
      .finally(() => setLoading(false));
  }, []);

  const vessels = useMemo(() => {
    if (investigation?.vessels?.length) return investigation.vessels;
    return demoVessels.map((v, i) => ({
      mmsi: `DEMO-${i + 1}`, vessel_name: v.name, latitude: null, longitude: null,
      attribution_score: v.score, distance_km: v.distance, time_difference_hours: v.time,
      proximity_score: v.score / 100, trajectory_match_score: v.score / 100,
      behavioral_anomaly_score: v.anomaly === "Yes" ? .82 : .3, relevance: "representative_demo_candidate"
    }));
  }, [investigation]);

  async function chooseScene(scene: DatasetScene) {
    const index = scenes.indexOf(scene);
    const id = scene.incident_id || `SP-${String(index + 1).padStart(3, "0")}`;
    setSelectedScene(id);
    setSelectedFile(scene.file);
    setLibraryOpen(false);
    setBusy(true);
    try { setInvestigation(await getInvestigation(id)); }
    catch (error) { console.error(error); }
    finally { setBusy(false); }
  }

  if (loading || !investigation) return <div className="loading-screen"><div className="loading-card"><span className="loader" /><strong>Loading OCEANNOVA</strong><p>Preparing the investigation workspace…</p></div></div>;

  const confidence = investigation.confidence * 100;
  const area = investigation.area_km2;

  return (
    <div className={`command-app ${dark ? "theme-dark" : "theme-light"}`}>
      <header className="command-topbar">
        <div className="command-brand"><img src="/oceannova-mark.png" alt="OCEANNOVA" /><div><strong>OCEANNOVA</strong><span>AI-Driven Ocean Spill Investigation</span></div></div>
        <div className="command-status"><i /> <span>Evidence Command Center</span><b>•</b><span>{busy ? "Loading scene" : "Workspace ready"}</span></div>
        <div className="command-actions"><button className="mode-badge" onClick={() => setDark(!dark)}><i>✓</i><span>{dark ? "Dark Mode" : "Light Mode"}<small>Theme</small></span></button><button className="icon-button" aria-label="Toggle theme" onClick={() => setDark(!dark)}>{dark ? "☀" : "☾"}</button></div>
      </header>

      <div className="command-body">
        <aside className="command-sidebar"><div><div className="mission-label">MISSION CONTROL</div><button className="command-nav active"><span>⌂</span>Overview</button><button className="command-nav" onClick={() => setLibraryOpen(true)}><span>▱</span>Scene Library</button></div><div className="sidebar-ocean"><div className="sidebar-wave">◒</div><strong>Protecting<br />Our Oceans<br />with AI</strong><small>OCEANNOVA<br />v1.0.0</small></div></aside>

        <main className="investigation-workspace">
          <div className="map-toolbar"><button onClick={() => setLibraryOpen(true)}>Scene: <strong>{selectedScene}</strong>{selectedFile ? <small className="scene-file-label">{selectedFile}</small> : null}<span className="scene-chevron">⌄</span></button><div><span>RADAR INVESTIGATION</span><b>{busy ? "Loading" : "Ready"}</b></div></div>
          <section className="map-stage"><MapView investigation={{ ...investigation, vessels }} darkMode={dark} /></section>

          <section className="bottom-evidence">
            <article className="evidence-card spill-card"><div className="evidence-card-title"><span className="card-icon red">◉</span><strong>Spill Detection</strong><b>High Confidence</b></div><div className="metric"><span>Area (approx.)</span><strong>{area.toFixed(2)} km²</strong></div><div className="metric"><span>Detection Method</span><strong>Sentinel-1 SAR (AI)</strong></div><div className="metric"><span>Confidence Score</span><strong>{confidence.toFixed(1)}%</strong></div></article>
            <article className="evidence-card"><div className="evidence-card-title"><span className="card-icon blue">♨</span><strong>Vessels Identified</strong></div><div className="vessel-summary"><div><i className="dot red" />High Attribution <b>{vessels.filter(v => v.attribution_score >= 90).length}</b></div><div><i className="dot orange" />Medium Attribution <b>{vessels.filter(v => v.attribution_score >= 75 && v.attribution_score < 90).length}</b></div><div><i className="dot green" />Lower Attribution <b>{vessels.filter(v => v.attribution_score < 75).length}</b></div></div></article>
            <article className="evidence-card"><div className="evidence-card-title"><span className="card-icon cyan">●</span><strong>Radar Analysis</strong><b className="complete">Complete</b></div><div className="status-list"><span>✓ Real SAR scene</span><span>✓ AI spill segmentation</span><span>✓ Spill footprint</span><span>✓ Vessel correlation view</span></div></article>
          </section>
        </main>
      </div>

      {libraryOpen && <div className="scene-modal" onClick={() => setLibraryOpen(false)}><div className="scene-dialog" onClick={(e) => e.stopPropagation()}><div className="scene-dialog-head"><div><small>PROCESSED RADAR_DATA</small><h2>Scene Library</h2><p>Every processed Sentinel-1 observation is available for investigation.</p></div><button onClick={() => setLibraryOpen(false)}>×</button></div><div className="scene-grid">{scenes.map((scene, index) => { const id = scene.incident_id || `SP-${String(index + 1).padStart(3, "0")}`; return <button key={`${id}-${scene.scene_id}-${scene.split}`} onClick={() => chooseScene(scene)}><span>{scene.split.toUpperCase()} • {scene.has_mask ? "GROUND TRUTH" : "NO MASK"}</span><strong>{id}</strong><small>{scene.file}</small><i>Open investigation →</i></button>; })}</div></div></div>}
    </div>
  );
}

export default App;
