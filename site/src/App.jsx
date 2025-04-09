import './App.css';
import React, {useState} from 'react';
import ArbitrageContainer from "./components/layout/ArbitrageContainer/ArbitrageContainer.jsx";
import PropBetContainer from "./components/layout/PropBetContainer/PropBetContainer.jsx";
import Navbar from "./components/layout/Navbar/Navbar.jsx";
import WelcomeScreen from "./components/layout/WelcomeScreen/WelcomeScreen.jsx";
import Chatbot from "./components/features/Gemini.jsx";

function App() {
    const [activeComponent, setActiveComponent] = useState('welcome');

    const renderComponent = () => {
        switch (activeComponent) {
            case 'component1':
                return <ArbitrageContainer/>;
            case 'component2':
                return <PropBetContainer/>;
            default:
                return <WelcomeScreen/>;
        }
    };

    return (
        <div style={{
            display: 'flex',
            height: '100vh',
            width: '100vw',
            overflow: 'hidden'
        }}>
            <Navbar
                activeComponent={activeComponent}
                setActiveComponent={setActiveComponent}
            />
            <main style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '20px',
                overflow: 'auto',
                marginLeft: 'auto',
                maxWidth: 'calc(100vw - var(--navbar-width, 250px))'
            }}>
                <div style={{
                    width: '100%',
                    maxWidth: '1200px',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column'
                }}>
                    {renderComponent()}
                </div>
            </main>
            <Chatbot/>
        </div>
    );
}

export default App;