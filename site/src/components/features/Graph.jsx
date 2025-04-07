import React, { useState, useEffect } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import {fetchGameOdds} from "../../services/api.jsx";

function LiveOddsGraph() {
    const [data, setData] = useState(null);
    console.log("data", data);

    useEffect(() => {
        const fetchData = async () => {
            const result = await fetchGameOdds('basketball_nba', 'player_points');
            setData(result);
        };
        fetchData();

        const intervalId = setInterval(fetchData, 60000);

        return () => clearInterval(intervalId);
    }, []);


    console.log("data", data);

    return (
        <div>
            <h2>NBA Player Points Odds</h2>
            {data ? (
                <pre>{JSON.stringify(data, null, 2)}</pre>
            ) : (
                <p>Loading data...</p>
            )}
        </div>
    )
}

export default LiveOddsGraph;