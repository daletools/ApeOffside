// PlayerBlock.jsx
import React from 'react';

const PlayerBlock = ({ playerName, playerData, onRemove }) => {
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
        </div>
    );
};

export default PlayerBlock;