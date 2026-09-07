import { useEffect, useState } from "react";

import MapView from "./components/MapView";
import Sidebar from "./components/Sidebar";
import { getInvestigation, type Investigation, type Vessel } from "./services/api";
import "./index.css";

function App() {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedVessel, setSelectedVessel] = useState<Vessel | null>(null);
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
    </div>
  );
}

export default App;
