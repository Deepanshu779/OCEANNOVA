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

            {investigation.vessels.slice(0, 3).map((vessel, index) => {

              const score = vessel.attribution_score * 100;

              return (
                <div
                  className={`suspect-card ${index === 0 ? "top-suspect" : ""}`}
                  key={vessel.mmsi}
                >

                  <div className="suspect-header">

                    <div>
                      <span className="rank">
                        #{index + 1}
                      </span>

                      <strong>
                        {vessel.vessel_name ?? vessel.mmsi}
                      </strong>
                    </div>

                    <strong className="suspect-score">
                      {score.toFixed(0)}%
                    </strong>

                  </div>


                  <div className="score-bar">

                    <div
                      className="score-fill"
                      style={{
                        width: `${score}%`,
                      }}
                    />

                  </div>


                  <div className="suspect-details">

                    <div>
                      <span>Distance</span>
                      <strong>
                        {vessel.distance_km !== null &&
                          vessel.distance_km !== undefined
                          ? `${vessel.distance_km} km`
                          : "N/A"}
                      </strong>
                    </div>


                    <div>
                      <span>Time Δ</span>
                      <strong>
                        {vessel.time_difference_hours !== null &&
                          vessel.time_difference_hours !== undefined
                          ? `${vessel.time_difference_hours} h`
                          : "N/A"}
                      </strong>
                    </div>


                    <div>
                      <span>Trajectory</span>
                      <strong>
                        {vessel.trajectory_match_score !== null &&
                          vessel.trajectory_match_score !== undefined
                          ? `${(
                            vessel.trajectory_match_score * 100
                          ).toFixed(0)}%`
                          : "N/A"}
                      </strong>
                    </div>


                    <div>
                      <span>Behavior</span>
                      <strong>
                        {vessel.behavioral_anomaly_score !== null &&
                          vessel.behavioral_anomaly_score !== undefined
                          ? `${(
                            vessel.behavioral_anomaly_score * 100
                          ).toFixed(0)}%`
                          : "N/A"}
                      </strong>
                    </div>

                  </div>

                </div>
              );
            })}

          </div>


          <div className="section">

            <h3>Drift Analysis</h3>

            <div className="metric">
              <span>Drift points</span>

              <strong>
                {investigation.drift.length}
              </strong>
            </div>

            <div className="section investigation-summary">

              <h3>Investigation Summary</h3>

              <div className="summary-step">
                <span className="summary-number">01</span>
                <div>
                  <strong>Spill Detected</strong>
                  <p>
                    {investigation.confidence * 100 >= 90
                      ? "High-confidence satellite detection"
                      : "Satellite-based spill detection"}
                  </p>
                </div>
              </div>

              <div className="summary-step">
                <span className="summary-number">02</span>
                <div>
                  <strong>Origin Reconstructed</strong>
                  <p>
                    {investigation.origin
                      ? `±${investigation.origin.uncertainty_km} km uncertainty`
                      : "Origin unavailable"}
                  </p>
                </div>
              </div>

              <div className="summary-step">
                <span className="summary-number">03</span>
                <div>
                  <strong>Drift Analysed</strong>
                  <p>
                    {investigation.drift.length} trajectory observations
                  </p>
                </div>
              </div>

              <div className="summary-step">
                <span className="summary-number">04</span>
                <div>
                  <strong>Vessels Ranked</strong>
                  <p>
                    {investigation.vessels.length} AIS candidates evaluated
                  </p>
                </div>
              </div>

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