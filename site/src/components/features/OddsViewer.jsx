import React, { useEffect, useState } from "react";
import { fetchOddsAPI } from "../../services/api"; // Adjusted path

const OddsViewer = () => {
  const [odds, setOdds] = useState([]);

 useEffect(() => {
  const fetchOdds = async () => {
    try {
      const data = await fetchOddsAPI("basketball_nba");

      // ✅ Only include games with odds
      const filtered = data.filter(game => game.bookmaker && game.bookmaker.h2h);
      setOdds(filtered);
    } catch (error) {
      console.error("Error fetching odds:", error);
    }
  };

  fetchOdds();
}, []);


  console.log("RENDERING ODDS:", odds); // ✅ Check re-renders

return (
  <div>
    <h2>NBA Odds</h2>
    {odds.length === 0 ? (
      <p>No odds available at this time.</p>
    ) : (
      <ul>
        {odds.map((game, index) => (
          <li key={index} style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '1rem' }}>
            <strong>{game.away_team} vs {game.home_team}</strong><br />
            <span>🕒 {new Date(game.commence_time).toLocaleString()}</span><br />
            <strong>💰 {game.bookmaker.title} Odds:</strong>
            <ul>
              {game.bookmaker.h2h.map((outcome, i) => (
                <li key={i}>{outcome.name}: {outcome.price}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    )}
  </div>
);

};

export default OddsViewer;
