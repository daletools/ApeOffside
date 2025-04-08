// components/Navbar.js
import React from 'react';

function Navbar({ activeComponent, setActiveComponent }) {
    // If using React Router, you can remove the activeComponent and setActiveComponent props
    return (
        <nav style={{
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            width: '200px',
            backgroundColor: '#f0f0f0',
            padding: '20px',
            boxShadow: '2px 0 5px rgba(0,0,0,0.1)',
            overflowY: 'auto' // in case content is taller than screen
        }}>
            <h2>Navigation</h2>
            <ul style={{ listStyle: 'none', padding: 0 }}>
                <li style={{ margin: '10px 0' }}>
                    <button
                        onClick={() => setActiveComponent('welcome')}
                        style={{
                            background: activeComponent === 'welcome' ? '#ddd' : 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            textAlign: 'left',
                            width: '100%',
                            padding: '8px'
                        }}
                    >
                        Welcome
                    </button>
                </li>
                <li style={{ margin: '10px 0' }}>
                    <button
                        onClick={() => setActiveComponent('component1')}
                        style={{
                            background: activeComponent === 'component1' ? '#ddd' : 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            textAlign: 'left',
                            width: '100%',
                            padding: '8px'
                        }}
                    >
                        Component One
                    </button>
                </li>
                <li style={{ margin: '10px 0' }}>
                    <button
                        onClick={() => setActiveComponent('component2')}
                        style={{
                            background: activeComponent === 'component2' ? '#ddd' : 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            textAlign: 'left',
                            width: '100%',
                            padding: '8px'
                        }}
                    >
                        Component Two
                    </button>
                </li>
            </ul>
        </nav>
    );
}

export default Navbar;