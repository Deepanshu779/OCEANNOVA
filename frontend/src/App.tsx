import { useEffect, useState } from "react";

import MapView from "./components/MapView";
import { getInvestigation, type Investigation } from "./services/api";

import "./index.css";


function App() {
  const [investigation, setInvestigation] =
    useState<Investigation | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    async function loadInvestigation() {
      try {
        const data = await getInvestigation("SP-001");

        setInvestigation(data);
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
    return (
      <div className="loading-screen">
        Loading OCEANNOVA investigation...
      </div>
    );
  }


  if (error || !investigation) {
    return (
      <div className="loading-screen">
        {error ?? "No investigation data available."}
      </div>
    );
  }


  return (
    <div className="app">

      <header className="topbar">

        <div>
          <h1>OCEANNOVA</h1>

          <span>
            Marine Oil Spill Intelligence Platform
          </span>
        </div>

        <div className="status">
          ● SYSTEM ONLINE
        </div>

      </header>


      <main className="dashboard">

        <aside className="sidebar">

          <h2>Investigation</h2>


          <div className="spill-card">

            <div className="label">
              DETECTED SPILL
            </div>

            <h3>
              {investigation.spill_id}
            </h3>


            <div className="metric">
              <span>Confidence</span>

              <strong>
                {(investigation.confidence * 100).toFixed(0)}%
              </strong>
            </div>


            <div className="metric">
              <span>Area</span>

              <strong>
                {investigation.area_km2} km²
              </strong>
            </div>


            {investigation.origin && (
              <div className="metric">
                <span>Origin uncertainty</span>

                <strong>
                  {investigation.origin.uncertainty_km} km
                </strong>
              </div>
            )}

          </div>


          <div className="section">

            <h3>Top Suspects</h3>


            {investigation.vessels.map((vessel) => (
              <div
                className="vessel"
                key={vessel.mmsi}
              >

                <strong>
                  {vessel.vessel_name ?? vessel.mmsi}
                </strong>

                <span>
                  {(vessel.attribution_score * 100).toFixed(0)}%
                </span>

              </div>
            ))}

          </div>


          <div className="section">

            <h3>Drift Analysis</h3>

            <div className="metric">
              <span>Drift points</span>

              <strong>
                {investigation.drift.length}
              </strong>
            </div>


            {investigation.origin && (
              <div className="metric">
                <span>Origin method</span>

                <strong>
                  {investigation.origin.method ?? "N/A"}
                </strong>
              </div>
            )}

          </div>

        </aside>


        <section className="map-container">

          <MapView investigation={investigation} />

        </section>

      </main>

    </div>
  );
}


export default App;