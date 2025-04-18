import React, { useState, useEffect } from 'react';
import PlayerBlock from "../../features/PlayerBlock.jsx";
import { fetchCurrentGames, fetchGameOdds } from "../../../services/api.jsx";
import useWindowSize from '../../../hooks/useWindowSize';
import GameCard from "./GameCard.jsx";

function PropBetContainer() {
    const [games, setGames] = useState([]);
    const [selectedGame, setSelectedGame] = useState(null);
    const [data, setData] = useState(null);
    const [trackedPlayers, setTrackedPlayers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [oddsLoading, setOddsLoading] = useState(false);
    const [oddsError, setOddsError] = useState(null);
    const { width } = useWindowSize();

    const getColumns = () => {
        if (width < 600) return 1;
        if (width < 900) return 2;
        if (width < 1200) return 3;
        return 4;
    };

    // Load games on startup
    useEffect(() => {
        const loadGames = async () => {
            setLoading(true);
            try {
                const gamesData = await fetchCurrentGames('basketball_nba');
                setGames(gamesData);
                setError(null);
            } catch (err) {
                setError('Failed to load games. Please try again later.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        loadGames();
    }, []);

    // Fetch player odds when game is selected
    useEffect(() => {
        if (!selectedGame) return;

        const fetchOdds = async () => {
            setOddsLoading(true);
            setOddsError(null);
            try {
                const result = await fetchGameOdds(
                    'basketball_nba',
                    selectedGame.id,
                    'player_points'
                );

                if (!result?.data?.player || Object.keys(result.data.player).length === 0) {
                    throw new Error('No player data available for this game');
                }

                setData(result);
            } catch (err) {
                setOddsError(err.message.includes('No player data')
                    ? 'No odds currently available for this game'
                    : 'Failed to load player odds. Please try again.');
                setData(null); // Clear any previous data
                console.error(err);
            } finally {
                setOddsLoading(false);
            }
        };

        fetchOdds();
        const intervalId = setInterval(fetchOdds, 60000);
        return () => clearInterval(intervalId);
    }, [selectedGame]);

    const togglePlayerTracking = (playerName) => {
        setTrackedPlayers(prev =>
            prev.includes(playerName)
                ? prev.filter(name => name !== playerName)
                : [...prev, playerName]
        );
    };

    return (
        <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
            {error && (
                <div style={{
                    color: 'red',
                    padding: '10px',
                    marginBottom: '20px',
                    border: '1px solid red',
                    borderRadius: '4px'
                }}>
                    {error}
                </div>
            )}

            <div style={{ marginBottom: '30px' }}>
                <h2 style={{ marginBottom: '15px' }}>Select a Game</h2>
                {loading ? (
                    <p>Loading games...</p>
                ) : (
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: `repeat(${getColumns()}, minmax(280px, 1fr))`,
                        gap: '15px',
                        transition: 'grid-template-columns 0.3s ease'
                    }}>
                        {games.map(game => (
                            <GameCard
                                key={game.id}
                                game={game}
                                isSelected={selectedGame?.id === game.id}
                                onClick={() => {
                                    setSelectedGame(game);
                                    setTrackedPlayers([]);
                                }}
                            />
                        ))}
                    </div>
                )}
            </div>

            {selectedGame && (
                <div>
                    <h2 style={{ marginBottom: '20px' }}>
                        {selectedGame.home_team} vs {selectedGame.away_team}
                    </h2>

                    {oddsError ? (
                        <div style={{
                            padding: '20px',
                            backgroundColor: '#fff8e1',
                            border: '1px solid #ffe0b2',
                            borderRadius: '8px',
                            color: '#e65100',
                            marginBottom: '20px'
                        }}>
                            {oddsError}
                            <div style={{ marginTop: '10px', fontSize: '0.9em' }}>
                                Try selecting another game or check back later.
                            </div>
                        </div>
                    ) : oddsLoading ? (
                        <p>Loading player odds...</p>
                    ) : (
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: width < 900 ? '1fr' : '1fr 2fr',
                            gap: '30px',
                            marginBottom: '30px'
                        }}>
                            <div>
                                <h3 style={{ marginBottom: '15px' }}>Available Players</h3>
                                <div style={{
                                    maxHeight: '500px',
                                    overflowY: 'auto',
                                    border: '1px solid #eee',
                                    borderRadius: '8px',
                                    padding: '15px'
                                }}>
                                    {data ? (
                                        Object.keys(data.data?.player || {}).map(player => (
                                            <div
                                                key={player}
                                                style={{
                                                    padding: '8px 0',
                                                    borderBottom: '1px solid #f0f0f0',
                                                    display: 'flex',
                                                    alignItems: 'center'
                                                }}
                                            >
                                                <input
                                                    type="checkbox"
                                                    id={`player-${player}`}
                                                    checked={trackedPlayers.includes(player)}
                                                    onChange={() => togglePlayerTracking(player)}
                                                    style={{
                                                        marginRight: '10px',
                                                        transform: 'scale(1.2)'
                                                    }}
                                                />
                                                <label
                                                    htmlFor={`player-${player}`}
                                                    style={{ cursor: 'pointer' }}
                                                >
                                                    {player}
                                                </label>
                                            </div>
                                        ))
                                    ) : (
                                        <p>No players available</p>
                                    )}
                                </div>
                            </div>

                            <div>
                                <h3 style={{ marginBottom: '15px' }}>Tracked Players</h3>
                                {trackedPlayers.length > 0 ? (
                                    <div style={{
                                        display: 'grid',
                                        gridTemplateColumns: `repeat(auto-fill, minmax(${width < 600 ? '100%' : '300px'}, 1fr))`,
                                        gap: '20px'
                                    }}>
                                        {trackedPlayers.map(player => (
                                            <PlayerBlock
                                                key={player}
                                                playerName={player}
                                                playerData={data?.data?.player[player]}
                                                onRemove={() => togglePlayerTracking(player)}
                                            />
                                        ))}
                                    </div>
                                ) : (
                                    <div style={{
                                        padding: '20px',
                                        border: '1px dashed #ddd',
                                        borderRadius: '8px',
                                        textAlign: 'center',
                                        color: '#888'
                                    }}>
                                        No players tracked yet. Select players from the list.
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default PropBetContainer;