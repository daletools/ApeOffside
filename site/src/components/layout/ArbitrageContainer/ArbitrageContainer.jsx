import React, {useState, useEffect} from "react";
import {fetchPlayerPropArbitrage} from "../../../services/api";

function ArbitrageContainer() {
    const [selectedSport, setSelectedSport] = useState(null);
    const [category, setCategory] = useState(null);
    const [playerPropType, setPlayerPropType] = useState(null); // e.g., "player_points"
    const [opportunities, setOpportunities] = useState([]);

    // Mock data for demonstration
    const mockOpportunities = [
        {
            type: "player_points",
            event: "Los Angeles Lakers vs Golden State Warriors",
            player: "LeBron James",
            line: 25.5,
            side_1: {name: "Over", bookmaker: "FanDuel", price: 2.1},
            side_2: {name: "Under", bookmaker: "DraftKings", price: 2.2},
            profit_percent: 7.8,
        },
    ];

    // Fetch arbitrage data when player prop type changes
    useEffect(() => {
        if (category === "player_props" && playerPropType) {
            setOpportunities([]); // ✅ clear old data before fetching new
            fetchPlayerPropArbitrage(playerPropType).then(setOpportunities);
        }
    }, [category, playerPropType]);
    useEffect(() => {
        setPlayerPropType(null);
        setOpportunities([]);
    }, [category]);


    const handleMockLoad = () => {
        setOpportunities(mockOpportunities);
    };

    return (
        <div>
            <h2>Arbitrage Finder</h2>

            {/* Sport  */}
            <div>
                <h4>Select Sport</h4>
                <button onClick={() => setSelectedSport("basketball_nba")}>NBA</button>
                <button disabled>NHL</button>
                <button disabled>MLB</button>
                <button disabled>UFC</button>
            </div>

            {/* Category  */}
            {selectedSport === "basketball_nba" && (
                <div>
                    <h4>Choose Prop Type</h4>
                    <button onClick={() => {
                        setCategory("player_props");
                        setPlayerPropType(null);
                        setOpportunities([]);
                    }}>
                        🧍‍♂️ Player Props
                    </button>
                    <button onClick={() => {
                        setCategory("team_props");
                        setPlayerPropType(null);
                        setOpportunities([]);
                    }}>
                        🏀 Team Props
                    </button>
                    <button onClick={() => {
                        setCategory("game_props");
                        setPlayerPropType(null);
                        setOpportunities([]);
                    }}>
                        🎯 Game Props
                    </button>
                </div>
            )}

            {/* Sub-options */}
            {category === "player_props" && (
                <div style={{marginTop: "1rem"}}>
                    <h4>Select Player Stat Market</h4>
                    <button onClick={() => setPlayerPropType("player_points")}>Points</button>
                    <button onClick={() => setPlayerPropType("player_assists")}>Assists</button>
                    <button onClick={() => setPlayerPropType("player_rebounds")}>Rebounds</button>
                    <button onClick={() => setPlayerPropType("player_threes")}>Threes Made</button>
                    <button onClick={() => setPlayerPropType("player_steals")}>Steals</button>
                    <button onClick={() => setPlayerPropType("player_blocks")}>Blocks</button>
                    <button onClick={() => setPlayerPropType("player_turnovers")}>Turnovers</button>
                    <button onClick={() => setPlayerPropType("player_free_throws_made")}>FT Made</button>
                </div>
            )}

            {/*  Display Results */}
            {playerPropType && (
                <div style={{marginTop: "2rem"}}>
                    <h4>Arbitrage Opportunities
                        for: {playerPropType.replace("player_", "").replace(/_/g, " ").toUpperCase()}</h4>
                    {opportunities.length === 0 ? (
                        <div>
                            <p>No arbitrage opportunities available right now. Try checking back later — these change
                                often!</p>
                            <button onClick={handleMockLoad}>Show Example with Mock Data</button>
                        </div>
                    ) : (
                        <ul>
                            {opportunities.map((opp, idx) => (
                                <li key={idx} style={{marginBottom: '1rem'}}>
                                    <strong>{opp.type.replace(/_/g, ' ').toUpperCase()}</strong><br/>
                                    <em>{opp.player || "N/A"} — Line: {opp.line ?? "?"} pts</em><br/>
                                    {opp.event}<br/>
                                    {opp.side_1.name} ({opp.side_1.bookmaker} @ {opp.side_1.price}) vs{" "}
                                    {opp.side_2.name} ({opp.side_2.bookmaker} @ {opp.side_2.price})<br/>
                                    <strong>Arbitrage: {opp.profit_percent}%</strong>
                                </li>
                            ))}
                        </ul>
                    )}

                </div>
            )}
        </div>
    );
}

export default ArbitrageContainer;
