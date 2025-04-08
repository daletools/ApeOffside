import React, { useState, useEffect } from 'react';
import PlayerBlock from "../../features/PlayerBlock.jsx";
import { fetchCurrentGames, fetchGameOdds } from "../../../services/api.jsx";

function PropBetContainer() {
    const [games, setGames] = useState([]);
    const [selectedGame, setSelectedGame] = useState(null);
    const [data, setData] = useState(null);
    const [trackedPlayers, setTrackedPlayers] = useState([]);

    // Load games on startup
    useEffect(() => {
        fetchCurrentGames('basketball_nba').then(setGames);
    }, []);


    // Fetch player odds when game is selected, repeating every minute
    useEffect(() => {
        if (!selectedGame) return;

        const fetchOdds = async () => {
            const result = await fetchGameOdds(
                'basketball_nba',
                selectedGame.id,
                'player_points'
            );
            setData(result);
        };

        fetchOdds();
        const intervalId = setInterval(fetchOdds, 60000);
        return () => clearInterval(intervalId);
    }, [selectedGame]);

    // Toggle player tracking
    const togglePlayerTracking = (playerName) => {
        setTrackedPlayers(prev =>
            prev.includes(playerName)
                ? prev.filter(name => name !== playerName) // Remove if already tracked
                : [...prev, playerName] // Add if not tracked
        );
    };


    return (
        <div>
            <div id="games">
                {games.map(game => (
                    <div key={game.id}>
                        <p>{game.home_team} vs {game.away_team}</p>
                        <button onClick={() => {
                            setSelectedGame(game);
                            setTrackedPlayers([]); // Reset tracked players when game changes
                        }}>
                            Select
                        </button>
                    </div>
                ))}
            </div>
            {selectedGame && data && (
                <div id="players">
                    <h3>{selectedGame.home_team} vs {selectedGame.away_team}</h3>

                    <div>
                        <h4>Available Players:</h4>
                        {Object.keys(data.data?.player || {}).map(player => (
                            <div key={player}>
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={trackedPlayers.includes(player)}
                                        onChange={() => togglePlayerTracking(player)}
                                    />
                                    {player}
                                </label>
                            </div>
                        ))}
                    </div>

                    <div>
                        <h4>Tracked Players:</h4>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
                            {trackedPlayers.map(player => (
                                <PlayerBlock
                                    key={player}
                                    playerName={player}
                                    playerData={data.data?.player[player]}
                                    onRemove={() => togglePlayerTracking(player)}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}


export default PropBetContainer;