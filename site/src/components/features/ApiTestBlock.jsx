import React, { useEffect, useState } from "react";
import { fetchSports, fetchCurrentGames } from "../../services/api.jsx";

function ApiTestBlock() {
    const [sports, setSports] = useState([]);
    const [games, setGames] = useState([]);

    useEffect(() => {
        const getSports = async () => {
            try {
                const data = await fetchSports();
                setSports(data);
            } catch (error) {
                console.log(`Error fetching sports: ${error}`);
            }
        };

        getSports();
    }, []);

    const handleFetchGames = async (sport) => {
        try {
            const data = await fetchCurrentGames(sport);
            setGames(data);
        } catch (error) {
            console.log(`Error fetching games:, ${error}`);
        }
    };
    return (
        <div>
            <h1>Sports</h1>
            <ul>
                {sports.map((sport) => (
                    <li key={sport.id}>
                        <button onClick={() => handleFetchGames(sport.key)}>{sport.title}</button>
                    </li>
                ))}
            </ul>

            <h2>Current Games</h2>
            <ul>
                {games.map((game) => (
                    <li key={game.id}>
                        {game.home_team} vs {game.away_team} at {game.commence_time}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default ApiTestBlock;