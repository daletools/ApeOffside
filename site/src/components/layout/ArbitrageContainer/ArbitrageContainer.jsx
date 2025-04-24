import React, {useState, useEffect} from "react";
import {fetchPlayerPropArbitrage} from "../../../services/api";
import {getCachedData, setCachedData} from "../../features/cache/useApiCache";
import './ArbitrageContainer.css';


function ArbitrageContainer() {
    const [selectedSport, setSelectedSport] = useState(null);
    const [category, setCategory] = useState(null);
    const [playerPropType, setPlayerPropType] = useState(null); // e.g., "player_points"
    const [opportunities, setOpportunities] = useState({arbitrage: [], near_arbitrage: []});

    const [useMock, setUseMock] = useState(false);
    const [loading, setLoading] = useState(false);

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
                },
                {
                    type: "player_points",
                    event: "Celtics vs Nets",
                    player: "Jayson Tatum",
                    line: 27.5,
                    side_1: {name: "Over", bookmaker: "BetMGM", price: 2.05},
                    side_2: {name: "Under", bookmaker: "Caesars", price: 2.1},
                    profit_percent: 7.2,
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
                },
                {
                    type: "player_assists",
                    event: "Knicks vs Hornets",
                    player: "Jalen Brunson",
                    line: 6.5,
                    side_1: {name: "Over", bookmaker: "BetRivers", price: 2.18},
                    side_2: {name: "Under", bookmaker: "PointsBet", price: 1.65},
                    profit_percent: 6.4,
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
                },
                {
                    type: "player_rebounds",
                    event: "76ers vs Magic",
                    player: "Joel Embiid",
                    line: 10.5,
                    side_1: {name: "Over", bookmaker: "Bet365", price: 2.15},
                    side_2: {name: "Under", bookmaker: "Unibet", price: 2.0},
                    profit_percent: 7.0,
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
                },
                {
                    type: "player_threes",
                    event: "Warriors vs Kings",
                    player: "Stephen Curry",
                    line: 5.5,
                    side_1: {name: "Over", bookmaker: "Betway", price: 2.2},
                    side_2: {name: "Under", bookmaker: "BetMGM", price: 1.68},
                    profit_percent: 6.3,
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
                },
                {
                    type: "player_steals",
                    event: "Lakers vs Suns",
                    player: "Anthony Davis",
                    line: 1.5,
                    side_1: {name: "Over", bookmaker: "Caesars", price: 2.1},
                    side_2: {name: "Under", bookmaker: "Bet365", price: 1.74},
                    profit_percent: 5.8,
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
                },
                {
                    type: "player_blocks",
                    event: "Pacers vs Bulls",
                    player: "Myles Turner",
                    line: 2.0,
                    side_1: {name: "Over", bookmaker: "BetRivers", price: 2.0},
                    side_2: {name: "Under", bookmaker: "Caesars", price: 1.78},
                    profit_percent: 5.6,
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
                },
                {
                    type: "player_turnovers",
                    event: "Heat vs Knicks",
                    player: "Jimmy Butler",
                    line: 2.5,
                    side_1: {name: "Over", bookmaker: "PointsBet", price: 2.0},
                    side_2: {name: "Under", bookmaker: "BetMGM", price: 1.7},
                    profit_percent: 6.2,
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
                },
                {
                    type: "player_free_throws_made",
                    event: "Lakers vs Nuggets",
                    player: "Anthony Davis",
                    line: 6.0,
                    side_1: {name: "Over", bookmaker: "Caesars", price: 2.05},
                    side_2: {name: "Under", bookmaker: "PointsBet", price: 1.72},
                    profit_percent: 6.8,
                }
            ],
            near_arbitrage: []
        }
    };
    //NBA Logos
    const teamLogos = {
        "Atlanta Hawks": "https://cdn.nba.com/logos/nba/1610612737/primary/L/logo.svg",
        "Boston Celtics": "https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg",
        "Brooklyn Nets": "https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg",
        "Charlotte Hornets": "https://cdn.nba.com/logos/nba/1610612766/primary/L/logo.svg",
        "Chicago Bulls": "https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg",
        "Cleveland Cavaliers": "https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg",
        "Dallas Mavericks": "https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg",
        "Denver Nuggets": "https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg",
        "Detroit Pistons": "https://cdn.nba.com/logos/nba/1610612765/primary/L/logo.svg",
        "Golden State Warriors": "https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg",
        "Houston Rockets": "https://cdn.nba.com/logos/nba/1610612745/primary/L/logo.svg",
        "Indiana Pacers": "https://cdn.nba.com/logos/nba/1610612754/primary/L/logo.svg",
        "LA Clippers": "https://cdn.nba.com/logos/nba/1610612746/primary/L/logo.svg",
        "Los Angeles Lakers": "https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg",
        "Memphis Grizzlies": "https://cdn.nba.com/logos/nba/1610612763/primary/L/logo.svg",
        "Miami Heat": "https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg",
        "Milwaukee Bucks": "https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg",
        "Minnesota Timberwolves": "https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg",
        "New Orleans Pelicans": "https://cdn.nba.com/logos/nba/1610612740/primary/L/logo.svg",
        "New York Knicks": "https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg",
        "Oklahoma City Thunder": "https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg",
        "Orlando Magic": "https://cdn.nba.com/logos/nba/1610612753/primary/L/logo.svg",
        "Philadelphia 76ers": "https://cdn.nba.com/logos/nba/1610612755/primary/L/logo.svg",
        "Phoenix Suns": "https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg",
        "Portland Trail Blazers": "https://cdn.nba.com/logos/nba/1610612757/primary/L/logo.svg",
        "Sacramento Kings": "https://cdn.nba.com/logos/nba/1610612758/primary/L/logo.svg",
        "San Antonio Spurs": "https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg",
        "Toronto Raptors": "https://cdn.nba.com/logos/nba/1610612761/primary/L/logo.svg",
        "Utah Jazz": "https://cdn.nba.com/logos/nba/1610612762/primary/L/logo.svg",
        "Washington Wizards": "https://cdn.nba.com/logos/nba/1610612764/primary/L/logo.svg"
    };

    const getLogoFromEvent = (event) => {
        const teamsInEvent = event.split(" vs ").map(team => team.trim());
        for (const fullTeamName in teamLogos) {
            for (const short of teamsInEvent) {
                if (fullTeamName.toLowerCase().includes(short.toLowerCase())) {
                    return teamLogos[fullTeamName];
                }
            }
        }
        return null;
    };


    useEffect(() => {
        //  Prevent running if any of the dependencies are invalid
        if (!playerPropType || !category || !selectedSport || category !== "player_props") {
            //console.log("[DEBUG useEffect] Skipping due to invalid state");
            return;
        }

        const cacheKey = `${selectedSport}_${playerPropType}`;
        const cached = getCachedData(cacheKey);

        //  If we have recent cached data, use it
        if (cached) {
            //    console.log(`[CACHE] ✅ Returning cached data for "${cacheKey}"`);
            setOpportunities(cached);
            setLoading(false);
            return;
        }

        //  Otherwise, fetch new data
        //       console.log(`[CACHE] ❌ No cache entry for "${cacheKey}", fetching new data...`);
        setLoading(true);
        setOpportunities({arbitrage: [], near_arbitrage: []});

        fetchPlayerPropArbitrage(playerPropType)
            .then(data => {
                setLoading(false);
                console.log("Fetched Data:", data);

                if (data && typeof data === "object" && Array.isArray(data.arbitrage)) {
                    setOpportunities(data);
                    // console.log("[DEBUG] Received arbitrage data:", data.arbitrage);
                    setCachedData(cacheKey, data);
                } else {
                    console.error("Invalid API response", data);
                    setOpportunities({arbitrage: [], near_arbitrage: []});
                }
            })
            .catch(err => {
                setLoading(false);
                console.error("API fetch failed:", err);
                setOpportunities({arbitrage: [], near_arbitrage: []});
            });
    }, [category, playerPropType, selectedSport]);


    const handleMockLoad = () => {
        if (useMock) {
            setUseMock(false);
            setOpportunities({arbitrage: [], near_arbitrage: []}); // Optional: reset to real
        } else {
            const mock = mockOpportunities[playerPropType] || [];
            setUseMock(true);
            setOpportunities(mock);
        }
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
                        if (playerPropType !== "player_points") {
                            setPlayerPropType("player_points");
                            setUseMock(false);
                        }
                    }}>Points
                    </button>

                    <button onClick={() => {
                        if (playerPropType !== "player_assists") {
                            setPlayerPropType("player_assists");
                            setUseMock(false);
                        }
                    }}>Assists
                    </button>

                    <button onClick={() => {
                        if (playerPropType !== "player_rebounds") {
                            setPlayerPropType("player_rebounds");
                            setUseMock(false);
                        }
                    }}>Rebounds
                    </button>

                    <button onClick={() => {
                        if (playerPropType !== "player_threes") {
                            setPlayerPropType("player_threes");
                            setUseMock(false);
                        }
                    }}>Threes Made
                    </button>

                    <button onClick={() => {
                        if (playerPropType !== "player_steals") {
                            setPlayerPropType("player_steals");
                            setUseMock(false);
                        }
                    }}>Steals
                    </button>

                    <button onClick={() => {
                        if (playerPropType !== "player_blocks") {
                            setPlayerPropType("player_blocks");
                            setUseMock(false);
                        }
                    }}>Blocks
                    </button>

                    <button onClick={() => {
                        if (playerPropType !== "player_turnovers") {
                            setPlayerPropType("player_turnovers");
                            setUseMock(false);
                        }
                    }}>Turnovers
                    </button>

                    <button onClick={() => {
                        if (playerPropType !== "player_free_throws_made") {
                            setPlayerPropType("player_free_throws_made");
                            setUseMock(false);
                        }
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

                    {/* Spinner */}
                    {loading && (
                        <div className="spinner-container">
                            <div className="spinner"></div>
                            <p>Loading opportunities...</p>
                        </div>
                    )}


                    {/* Mock data */}
                    {useMock && (
                        <div className="mock-data-container">
                            <h5>🧪 Mock Arbitrage Example</h5>
                            <ul className="arb-list mock-data-grid">
                                {opportunities.arbitrage.map((opp, idx) => {
                                    const logo = getLogoFromEvent(opp.event);
                                    console.log(opp.event, "→", logo);
                                    return (
                                        <li
                                            key={`arb-${idx}`}
                                            className="arb-opportunity"
                                            style={{
                                                backgroundImage: logo ? `url(${logo})` : "none",
                                                backgroundRepeat: "no-repeat",
                                                backgroundPosition: "right bottom",
                                                backgroundSize: "80px",
                                            }}
                                        >
                                            <strong>{opp.type.replace(/_/g, ' ').toUpperCase()}</strong>
                                            <div style={{fontSize: "1rem", margin: "0.25rem 0"}}>
                                                <strong>{opp.player || "N/A"}</strong><br/>
                                                <span style={{fontStyle: "italic", color: "#444"}}>
                                Line: {opp.line ?? "?"} pts
                            </span>
                                            </div>
                                            {opp.event}<br/>
                                            {opp.side_1.name} (
                                            <a href={opp.side_1.site} target="_blank" rel="noopener noreferrer">
                                                {opp.side_1.bookmaker}
                                            </a> @ {opp.side_1.price}
                                            ) vs{" "}
                                            {opp.side_2.name} (
                                            <a href={opp.side_2.site} target="_blank" rel="noopener noreferrer">
                                                {opp.side_2.bookmaker}
                                            </a> @ {opp.side_2.price}
                                            )
                                            <br/>
                                            <strong>Arbitrage: {opp.profit_percent}%</strong>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    )}


                    {/* True arbitrage */}
                    {!useMock && opportunities?.arbitrage?.length > 0 && (
                        <div className="true-arbitrage-container">
                            <h5>🔥 True Arbitrage</h5>
                            <ul className="true-data-grid arb-list">
                                {opportunities.arbitrage.map((opp, idx) => {
                                    const logo = getLogoFromEvent(opp.event);
                                    return (
                                        <li
                                            key={`arb-${idx}`}
                                            className="arb-opportunity"
                                            style={{
                                                backgroundImage: logo ? `url(${logo})` : "none",
                                                backgroundRepeat: "no-repeat",
                                                backgroundPosition: "right bottom",
                                                backgroundSize: "80px",
                                            }}
                                        >
                                            <strong>{opp.type.replace(/_/g, ' ').toUpperCase()}</strong>
                                            <div style={{fontSize: "1rem", margin: "0.25rem 0"}}>
                                                <strong>{opp.player || "N/A"}</strong><br/>
                                                <span style={{fontStyle: "italic", color: "#444"}}>
                                Line: {opp.line ?? "?"} pts
                            </span>
                                            </div>
                                            {opp.event}<br/>
                                            {opp.side_1.name} (
                                            <a href={opp.side_1.site} target="_blank" rel="noopener noreferrer">
                                                {opp.side_1.bookmaker}
                                            </a> @ {opp.side_1.price}
                                            ) vs{" "}
                                            {opp.side_2.name} (
                                            <a href={opp.side_2.site} target="_blank" rel="noopener noreferrer">
                                                {opp.side_2.bookmaker}
                                            </a> @ {opp.side_2.price}
                                            )
                                            <br/>
                                            <strong>Arbitrage: {opp.profit_percent}%</strong>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    )}


                    {/* Near-arbitrage */}
                    {!useMock && opportunities?.near_arbitrage?.length > 0 && (
                        <div className="near-arbitrage-container">
                            <h5>Near-Arbitrage Opportunities</h5>
                            <ul className="near-data-grid arb-list">
                                {opportunities.near_arbitrage.map((opp, idx) => {
                                    const logo = getLogoFromEvent(opp.event);
                                    return (
                                        <li
                                            key={`near-${idx}`}
                                            className="arb-opportunity"
                                            style={{
                                                backgroundImage: logo ? `url(${logo})` : "none",
                                                backgroundRepeat: "no-repeat",
                                                backgroundPosition: "right bottom",
                                                backgroundSize: "80px",
                                            }}
                                        >
                                            <strong>{opp.type.replace(/_/g, ' ').toUpperCase()}</strong>
                                            <div style={{fontSize: "1rem", margin: "0.25rem 0"}}>
                                                <strong>{opp.player || "N/A"}</strong><br/>
                                                <span style={{fontStyle: "italic", color: "#444"}}>
                                Line: {opp.line ?? "?"} pts
                            </span>
                                            </div>
                                            {opp.event}<br/>
                                            {opp.side_1.name} (
                                            <a href={opp.side_1.site} target="_blank" rel="noopener noreferrer">
                                                {opp.side_1.bookmaker}
                                            </a> @ {opp.side_1.price}
                                            ) vs{" "}
                                            {opp.side_2.name} (
                                            <a href={opp.side_2.site} target="_blank" rel="noopener noreferrer">
                                                {opp.side_2.bookmaker}
                                            </a> @ {opp.side_2.price}
                                            )
                                            <br/>
                                            <strong>
                                                Combined Implied Probability: {opp.implied_total.toFixed(3)}
                                            </strong><br/>
                                            <span style={{fontStyle: "italic", color: "#777"}}>
                            Edge: {(100 - opp.implied_total * 100).toFixed(2)}%
                        </span>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    )}

                    {/* Mock button — shown if not loading and not already using mock */}
                    {!loading && !useMock && (
                        <div style={{textAlign: "center", margin: "1rem 0"}}>
                            <button onClick={handleMockLoad}>Show Example with Mock Data</button>
                        </div>
                    )}
                </div>
            )}

        </div>
    )
        ;

}

export default ArbitrageContainer;
