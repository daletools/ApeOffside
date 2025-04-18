import React, { useState, useEffect, useMemo } from 'react';
import { FaTimes, FaChartLine, FaExternalLinkAlt } from 'react-icons/fa';

const PlayerBlock = ({ playerName, playerData, onRemove, onGetInsights }) => {
    const [historicalData, setHistoricalData] = useState([]);
    const [showTrends, setShowTrends] = useState(false);

    // Update historical data when new props arrive
    useEffect(() => {
        if (playerData) {
            setHistoricalData(prev => {
                const newData = {
                    timestamp: new Date().toISOString(),
                    data: playerData
                };
                return [...prev, newData].slice(-10); // Keep the last 10 entries
            });
        }
    }, [playerData]);

    // Memoized trend calculations
    const trends = useMemo(() => {
        if (historicalData.length < 2) return null;

        const calculatedTrends = {};
        const bookmakers = Object.keys(historicalData[0].data || {});

        bookmakers.forEach(bookmaker => {
            calculatedTrends[bookmaker] = {
                over: calculatePriceTrend(historicalData, bookmaker, 'Over'),
                under: calculatePriceTrend(historicalData, bookmaker, 'Under')
            };
        });

        return calculatedTrends;
    }, [historicalData]);

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
            trends
        };
        if (typeof onGetInsights === 'function') {
            onGetInsights(insightsData);
            console.log("Data ready for AI chatbot:", insightsData);
        } else {
            console.error("onGetInsights is not a function");
        }
    };

    const renderTrendIndicator = (trend) => {
        if (!trend) return null;

        return (
            <span style={{
                color: trend.direction === 'up' ? '#4CAF50' : '#F44336',
                marginLeft: '5px',
                fontSize: '0.8em',
                display: 'inline-flex',
                alignItems: 'center'
            }}>
                {trend.direction === 'up' ? '↑' : '↓'}
                {Math.abs(trend.percentChange).toFixed(1)}%
            </span>
        );
    };

    const renderOddsValue = (value, link, type) => {
        const baseStyle = {
            fontWeight: '500',
            padding: '2px 4px',
            borderRadius: '3px'
        };

        if (!link) {
            return <span style={baseStyle}>{value?.toFixed(2) || '-'}</span>;
        }

        return (
            <a
                href={link}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                    ...baseStyle,
                    backgroundColor: '#f0f7ff',  // Light blue background
                    color: '#0066cc',             // Darker blue text
                    textDecoration: 'none',
                    border: '1px solid #cce0ff',
                    transition: 'all 0.2s',
                }}
                aria-label={`Bet ${type} on ${playerName}`}
            >
                {value?.toFixed(2) || '-'}
            </a>
        );
    };


    return (
        <div style={{
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            color: 'black',
            padding: '15px',
            width: '100%',
            maxWidth: '300px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            margin: '10px',
            position: 'relative',
            backgroundColor: 'darkgray'
        }}>
            {/* Header with remove button */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '10px'
            }}>
                <h3 style={{
                    margin: 0,
                    fontSize: '1.2rem',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    maxWidth: '200px'
                }}>
                    {playerName}
                </h3>
                <button
                    onClick={onRemove}
                    style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: 'white',
                        fontSize: '1.2em',
                        padding: '5px',
                        transition: 'color 0.2s',
                    }}
                    aria-label="Remove player"
                >
                    <FaTimes />
                </button>
            </div>

            {/* Odds by bookmaker */}
            <div style={{ marginTop: '10px' }}>
                {playerData && Object.entries(playerData).map(([bookmaker, odds]) => (
                    <div key={bookmaker} style={{
                        marginBottom: '15px',
                        paddingBottom: '15px',
                        borderBottom: '1px solid #f5f5f5'
                    }}>
                        {bookmaker}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            marginBottom: '5px',
                            gap: '10px'
                        }}>
                            <div style={{ flex: 1 }}>
                                <span style={{ fontWeight: '500' }}>Over: </span>
                                {renderOddsValue(odds.Over?.price, odds.Over?.link, 'Over')}
                                {showTrends && renderTrendIndicator(trends?.[bookmaker]?.over)}
                            </div>
                            <div style={{ flex: 1, textAlign: 'right' }}>
                                <span style={{ fontWeight: '500' }}>Under: </span>
                                {renderOddsValue(odds.Under?.price, odds.Under?.link, 'Under')}
                                {showTrends && renderTrendIndicator(trends?.[bookmaker]?.under)}
                            </div>
                        </div>

                        <div style={{
                            textAlign: 'center',
                            margin: '8px 0 4px',
                            padding: '4px',
                            backgroundColor: '#f8f9fa',
                            borderRadius: '4px',
                            fontSize: '0.9em'
                        }}>
                            <span style={{ fontWeight: '500' }}>Line: </span>
                            <span style={{ fontFamily: 'monospace' }}>
                                {odds.Over?.point || odds.Under?.point || '-'}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Insights button */}
            <button
                onClick={handleGetInsights}
                style={{
                    marginTop: '15px',
                    padding: '8px 12px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    fontSize: '0.9rem',
                    transition: 'background-color 0.2s',
                }}
            >
                <FaChartLine /> Get Insights
            </button>

            {/* Debug view - only visible in development and when showTrends is true */}
            {process.env.NODE_ENV === 'development' && showTrends && (
                <div style={{
                    marginTop: '15px',
                    fontSize: '0.8em',
                    color: '#666',
                    borderTop: '1px dashed #eee',
                    paddingTop: '10px'
                }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginBottom: '5px'
                    }}>
                        <span style={{ fontWeight: '500' }}>Last Updated:</span>
                        <span>{new Date().toLocaleTimeString()}</span>
                    </div>
                    <pre style={{
                        backgroundColor: 'lightgrey',
                        padding: '10px',
                        borderRadius: '4px',
                        overflowX: 'auto',
                        fontSize: '0.7em',
                        maxHeight: '150px'
                    }}>
                        {JSON.stringify({
                            historicalData,
                            trends
                        }, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
};

export default PlayerBlock;
