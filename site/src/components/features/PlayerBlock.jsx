import React, { useState, useEffect } from 'react';

const PlayerBlock = ({ playerName, playerData, onRemove }) => {
    const [historicalData, setHistoricalData] = useState([]);

    // Update historical data when new props arrive
    useEffect(() => {
        if (playerData) {
            setHistoricalData(prev => {
                const newData = {
                    timestamp: new Date().toISOString(),
                    data: playerData
                };

                const updatedHistory = [...prev, newData].slice(-10);

                // Debug print to console
                console.log(`[DEBUG] ${playerName} data updated. Current history:`);
                console.log('Latest data:', newData);
                console.log('Historical data:', updatedHistory);

                const trends = calculateTrends(updatedHistory);
                console.log('Calculated trends:', trends);

                return updatedHistory;
            });
        }
    }, [playerData, playerName]);

    const calculateTrends = (history) => {
        if (history.length < 2) return null;

        const trends = {};
        const bookmakers = Object.keys(history[0].data || {});

        bookmakers.forEach(bookmaker => {
            trends[bookmaker] = {
                over: calculatePriceTrend(history, bookmaker, 'Over'),
                under: calculatePriceTrend(history, bookmaker, 'Under')
            };
        });

        return trends;
    };

    const calculatePriceTrend = (history, bookmaker, type) => {
        const prices = history.map(entry =>
            entry.data[bookmaker]?.[type]?.price || null
        ).filter(price => price !== null);

        if (prices.length < 2) return null;

        const firstPrice = prices[0];
        const lastPrice = prices[prices.length - 1];
        const change = lastPrice - firstPrice;
        const percentChange = (change / firstPrice) * 100;

        return {
            firstPrice,
            lastPrice,
            change,
            percentChange,
            direction: change >= 0 ? 'up' : 'down'
        };
    };

    const handleGetInsights = () => {
        const insightsData = {
            playerName,
            currentOdds: playerData,
            historicalData,
            trends: calculateTrends(historicalData)
        };
        console.log("Data ready for AI chatbot:", insightsData);
    };

    return (
        <div style={{
            border: '1px solid #ddd',
            padding: '10px',
            borderRadius: '5px',
            width: '250px'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <h3 style={{ margin: 0 }}>{playerName}</h3>
                <button
                    onClick={onRemove}
                    style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        fontSize: '1.2em'
                    }}
                >
                    ×
                </button>
            </div>

            {playerData && Object.entries(playerData).map(([bookmaker, odds]) => (
                <div key={bookmaker} style={{ marginTop: '10px' }}>
                    <h4 style={{ margin: '5px 0' }}>{bookmaker}</h4>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Over: {odds.Over?.price?.toFixed(2) || '-'}</span>
                        <span>Under: {odds.Under?.price?.toFixed(2) || '-'}</span>
                    </div>
                    <div>Point: {odds.Over?.point || odds.Under?.point || '-'}</div>
                </div>
            ))}

            <button
                onClick={handleGetInsights}
                style={{
                    marginTop: '10px',
                    padding: '5px 10px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    width: '100%'
                }}
            >
                Get Insights
            </button>

            {/* Hidden debug view (remove in production) */}
            {(
                <div style={{ display: 'none' }}>
                    <h4>Historical Data (last 10):</h4>
                    <pre>{JSON.stringify(historicalData, null, 2)}</pre>
                    <h4>Trends:</h4>
                    <pre>{JSON.stringify(calculateTrends(historicalData), null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default PlayerBlock;