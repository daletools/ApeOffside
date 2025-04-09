import React, { useState, useEffect } from "react";
import { fetchArbitrageOpportunities, fetchValueBets } from "../../services/api";

function InsightsSelector() {
  const [sport, setSport] = useState("basketball_nba");
  const [mode, setMode] = useState("arbitrage"); // or 'value'
  const [opportunities, setOpportunities] = useState([]);

const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

useEffect(() => {
  setLoading(true);
  setError(null);

  const fetchData = mode === "arbitrage" ? fetchArbitrageOpportunities : fetchValueBets;

  fetchData()
    .then(setOpportunities)
    .catch(err => setError("Failed to load data"))
    .finally(() => setLoading(false));
}, [mode]);


  return (
    <div>
      <div>
        <label>Sport: </label>
        <select value={sport} onChange={(e) => setSport(e.target.value)} disabled>
          <option value="basketball_nba">Basketball (NBA)</option>
          {/* Expand later */}
        </select>
      </div>

      <div>
        <label>Mode: </label>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="arbitrage">Arbitrage</option>
          <option value="value">Value Bets</option>
        </select>
      </div>

      <div>
        <h3>Available Opportunities:</h3>
        <ul>
          {opportunities.map((opp, idx) => (
            <li key={idx}>
              {opp.home_team} vs {opp.away_team} — {mode === "arbitrage"
                ? `Profit: ${opp.profit_percent}%`
                : `Value: ${opp.value_percentage}% on ${opp.team} @ ${opp.bookmaker}`}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default InsightsSelector;
