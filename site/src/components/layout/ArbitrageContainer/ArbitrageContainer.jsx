import React, {useState, useEffect} from "react";
import {fetchPlayerPropArbitrage} from "../../../services/api";

function ArbitrageContainer() {
    const [selectedSport, setSelectedSport] = useState(null);
    const [category, setCategory] = useState(null);
    const [playerPropType, setPlayerPropType] = useState(null); // e.g., "player_points"
    const [opportunities, setOpportunities] = useState({arbitrage: [], near_arbitrage: []});

    const [useMock, setUseMock] = useState(false);

    // Mock Data
    const mockOpportunities = {
        player_points: {
            arbitrage: [
                {
                    type: "player_points",
                    event: "Lakers vs Warriors",
                    player: "LeBron James",
                    line: 25.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.1},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 2.2},
                    profit_percent: 7.8,
                }
            ],
            near_arbitrage: []
        },
        player_assists: {
            arbitrage: [
                {
                    type: "player_assists",
                    event: "Bulls vs Heat",
                    player: "Coby White",
                    line: 4.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.24},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 1.6},
                    profit_percent: 6.9,
                }
            ],
            near_arbitrage: []
        },
        player_rebounds: {
            arbitrage: [
                {
                    type: "player_rebounds",
                    event: "Nuggets vs Timberwolves",
                    player: "Nikola Jokic",
                    line: 12.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.05},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 2.1},
                    profit_percent: 8.3,
                }
            ],
            near_arbitrage: []
        },
        player_threes: {
            arbitrage: [
                {
                    type: "player_threes",
                    event: "Celtics vs Knicks",
                    player: "Jayson Tatum",
                    line: 3.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.05},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 1.75},
                    profit_percent: 6.7,
                }
            ],
            near_arbitrage: []
        },
        player_steals: {
            arbitrage: [
                {
                    type: "player_steals",
                    event: "Nets vs Raptors",
                    player: "Mikal Bridges",
                    line: 2.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.12},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 1.72},
                    profit_percent: 6.1,
                }
            ],
            near_arbitrage: []
        },
        player_blocks: {
            arbitrage: [
                {
                    type: "player_blocks",
                    event: "Bucks vs Cavaliers",
                    player: "Brook Lopez",
                    line: 2.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.08},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 1.74},
                    profit_percent: 5.9,
                }
            ],
            near_arbitrage: []
        },
        player_turnovers: {
            arbitrage: [
                {
                    type: "player_turnovers",
                    event: "Grizzlies vs Suns",
                    player: "Devin Booker",
                    line: 3.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.1},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 1.76},
                    profit_percent: 6.5,
                }
            ],
            near_arbitrage: []
        },
        player_free_throws_made: {
            arbitrage: [
                {
                    type: "player_free_throws_made",
                    event: "Heat vs Bulls",
                    player: "Jimmy Butler",
                    line: 7.5,
                    side_1: {name: "Over", bookmaker: "FanDuel", price: 2.2},
                    side_2: {name: "Under", bookmaker: "DraftKings", price: 1.65},
                    profit_percent: 7.1,
                }
            ],
            near_arbitrage: []
        },
    };


    useEffect(() => {
        if (playerPropType) {
            if (useMock) {
                const mock = mockOpportunities[playerPropType] || {arbitrage: [], near_arbitrage: []};
                setOpportunities(mock);
            } else if (category === "player_props") {
                setOpportunities({arbitrage: [], near_arbitrage: []});

                fetchPlayerPropArbitrage(playerPropType)
                    .then(data => {
                        console.log("Fetched Data:", data);

                        if (data && typeof data === "object" && Array.isArray(data.arbitrage)) {
                            setOpportunities({
                                arbitrage: data.arbitrage,
                                near_arbitrage: data.near_arbitrage || [],
                            });
                        } else {
                            console.error("Invalid API response", data);
                            setOpportunities({arbitrage: [], near_arbitrage: []});
                        }
                    })
                    .catch(err => {
                        console.error("API fetch failed:", err);
                        setOpportunities({arbitrage: [], near_arbitrage: []});
                    });
            }
        }
    }, [category, playerPropType, useMock]);


    const handleMockLoad = () => {
        const mock = mockOpportunities[playerPropType] || [];
        setUseMock(true);
        setOpportunities(mock); // ✅ Ensure immediate display
    };


    return (
        <div>
            <h2>Arbitrage Finder</h2>

            {/* Sport */}
            <div>
                <h4>Select Sport</h4>
                <button onClick={() => {
                    setSelectedSport("basketball_nba");
                    setCategory(null);
                    setPlayerPropType(null);
                    setOpportunities([]);
                    setUseMock(false);
                }}>
                    NBA
                </button>
                <button disabled>NHL</button>
                <button disabled>MLB</button>
                <button disabled>UFC</button>
            </div>

            {/* Category */}
            {selectedSport === "basketball_nba" && (
                <div>
                    <h4>Choose Prop Type</h4>
                    <button onClick={() => {
                        setCategory("player_props");
                        setPlayerPropType(null);
                        setOpportunities([]);
                        setUseMock(false);
                    }}>🧍‍♂️ Player Props
                    </button>
                    <button onClick={() => {
                        setCategory("team_props");
                        setPlayerPropType(null);
                        setOpportunities([]);
                        setUseMock(false);
                    }}>🏀 Team Props
                    </button>
                    <button onClick={() => {
                        setCategory("game_props");
                        setPlayerPropType(null);
                        setOpportunities([]);
                        setUseMock(false);
                    }}>🎯 Game Props
                    </button>
                </div>
            )}

            {/* Player Prop Types */}
            {category === "player_props" && (
                <div style={{marginTop: "1rem"}}>
                    <h4>Select Player Stat Market</h4>
                    <button onClick={() => {
                        setPlayerPropType("player_points");
                        setUseMock(false);
                    }}>Points
                    </button>
                    <button onClick={() => {
                        setPlayerPropType("player_assists");
                        setUseMock(false);
                    }}>Assists
                    </button>
                    <button onClick={() => {
                        setPlayerPropType("player_rebounds");
                        setUseMock(false);
                    }}>Rebounds
                    </button>
                    <button onClick={() => {
                        setPlayerPropType("player_threes");
                        setUseMock(false);
                    }}>Threes Made
                    </button>
                    <button onClick={() => {
                        setPlayerPropType("player_steals");
                        setUseMock(false);
                    }}>Steals
                    </button>
                    <button onClick={() => {
                        setPlayerPropType("player_blocks");
                        setUseMock(false);
                    }}>Blocks
                    </button>
                    <button onClick={() => {
                        setPlayerPropType("player_turnovers");
                        setUseMock(false);
                    }}>Turnovers
                    </button>
                    <button onClick={() => {
                        setPlayerPropType("player_free_throws_made");
                        setUseMock(false);
                    }}>FT Made
                    </button>
                </div>
            )}

            {/* Opportunities Display */}
            {playerPropType && (
                <div style={{marginTop: "2rem"}}>
                    <h4>
                        Arbitrage Opportunities for:{" "}
                        {playerPropType.replace("player_", "").replace(/_/g, " ").toUpperCase()}
                    </h4>

                    {(opportunities?.arbitrage?.length === 0 && opportunities?.near_arbitrage?.length === 0) ? (

                        <div>
                            <p>No arbitrage opportunities available right now. Try checking back later — these change
                                often!</p>
                            <button onClick={handleMockLoad}>Show Example with Mock Data</button>
                        </div>
                    ) : (
                        <>
                            {opportunities?.arbitrage?.length > 0 && (
                                <div>
                                    <h5>🔥 True Arbitrage</h5>
                                    <ul>
                                        {opportunities.arbitrage.map((opp, idx) => (
                                            <li key={`arb-${idx}`} style={{marginBottom: '1rem'}}>
                                                <strong>{opp.type.replace(/_/g, ' ').toUpperCase()}</strong><br/>
                                                <em>{opp.player || "N/A"} — Line: {opp.line ?? "?"} pts</em><br/>
                                                {opp.event}<br/>
                                                {opp.side_1.name} ({opp.side_1.bookmaker} @ {opp.side_1.price}) vs{" "}
                                                {opp.side_2.name} ({opp.side_2.bookmaker} @ {opp.side_2.price})<br/>
                                                <strong>Arbitrage: {opp.profit_percent}%</strong>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Near-Arbitrage Section */}
                            {opportunities?.near_arbitrage?.length > 0 && (
                                <div>
                                    <h5>🔍 Near-Arbitrage Opportunities</h5>
                                    <ul>
                                        {opportunities.near_arbitrage.map((opp, idx) => (
                                            <li key={`near-${idx}`} style={{marginBottom: '1rem', opacity: 0.8}}>
                                                <strong>{opp.type.replace(/_/g, ' ').toUpperCase()}</strong><br/>
                                                <em>{opp.player || "N/A"} — Line: {opp.line ?? "?"} pts</em><br/>
                                                {opp.event}<br/>
                                                {opp.side_1.name} ({opp.side_1.bookmaker} @ {opp.side_1.price}) vs{" "}
                                                {opp.side_2.name} ({opp.side_2.bookmaker} @ {opp.side_2.price})<br/>
                                                <strong>
                                                    Combined Implied Probability: {opp.implied_total.toFixed(3)}
                                                </strong><br/>
                                                <span style={{fontStyle: "italic", color: "#777"}}>
                        Edge: {(100 - opp.implied_total * 100).toFixed(2)}%
                    </span>
                                            </li>
                                        ))}
                                    </ul>

                                    <div style={{marginTop: "1rem"}}>
                                        <button onClick={handleMockLoad}>Show Example with Mock Data</button>
                                    </div>
                                </div>
                            )}


                            {/* No Opportunities */}
                            {opportunities?.arbitrage?.length === 0 && opportunities?.near_arbitrage?.length === 0 && (
                                <div>
                                    <p>No arbitrage opportunities available right now. Try checking back later — these
                                        change often!</p>
                                    <button onClick={handleMockLoad}>Show Example with Mock Data</button>
                                </div>
                            )}

                        </>
                    )}
                </div>
            )}
        </div>
    );
}

export default ArbitrageContainer;
