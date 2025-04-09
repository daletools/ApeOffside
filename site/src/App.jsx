import './App.css'
// App.js
import React, { useState } from 'react';
import ArbitrageContainer from "./components/layout/ArbitrageContainer/ArbitrageContainer.jsx";
import PropBetContainer from "./components/layout/PropBetContainer/PropBetContainer.jsx";
import Navbar from "./components/layout/Navbar/Navbar.jsx";
import WelcomeScreen from "./components/layout/WelcomeScreen/WelcomeScreen.jsx";

function App() {
    const [activeComponent, setActiveComponent] = useState('welcome');

    const renderComponent = () => {
        switch (activeComponent) {
            case 'arbitrage':
                return <ArbitrageContainer />;
            case 'component2':
                return <PropBetContainer />;
            default:
                return <WelcomeScreen />;
        }
    };

    return (
        <div className="app-container" style={{ display: 'flex', height: '100vh' }}>
            <Navbar
                activeComponent={activeComponent}
                setActiveComponent={setActiveComponent}
            />
            <main className="content-panel" style={{
                flex: 1,
                padding: '20px',
                overflow: 'auto'
            }}>
                {renderComponent()}
            </main>
        </div>
    );
}

export default App;