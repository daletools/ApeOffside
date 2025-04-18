import React from "react";

const GameCard = ({ game, isSelected, onClick }) => (
    <div
        style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '15px',
            cursor: 'pointer',
            backgroundColor: isSelected ? 'lightgreen' : 'darkgray',
            transition: 'all 0.2s',
        }}
        onClick={onClick}
    >
        <p style={{ fontWeight: 'bold', margin: '0 0 5px 0' }}>
            {game.home_team} vs {game.away_team}
        </p>
        <p style={{ color: '#666', fontSize: '0.9em', margin: 0 }}>
            {new Date(game.commence_time).toLocaleString(undefined, {
                timeZoneName: 'short',
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit'
            })}
        </p>
    </div>
);

export default GameCard;