import React from 'react';

function Navbar({ activeComponent, setActiveComponent }) {
    return (
        <nav style={{
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            width: '200px',
            backgroundColor: 'black',
            padding: '20px',
            boxShadow: '2px 0 5px rgba(0,0,0,0.1)',
            overflowY: 'auto'
        }}>
            {/*<h2>Navigation</h2>*/}
            <h2 style={{fontFamily: 'Copperplate, fantasy', letterSpacing: '2px'}}>NXVIGXTION</h2>
            <ul style={{listStyle: 'none', padding: 0}}>
                <li style={{margin: '10px 0'}}>
                    <button
                        onClick={() => setActiveComponent('welcome')}
                        style={{
                            background: activeComponent === 'welcome' ? 'darkgray' : 'transparent',
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
                <li style={{margin: '10px 0'}}>
                    <button
                        onClick={() => setActiveComponent('arbitrage')}
                        style={{
                            background: activeComponent === 'arbitrage' ? 'darkgray' : 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            textAlign: 'left',
                            width: '100%',
                            padding: '8px'
                        }}
                    >
                        Arbitrage
                </button>
                </li>
                <li style={{margin: '10px 0'}}>
                    <button
                        onClick={() => setActiveComponent('component2')}
                        style={{
                            background: activeComponent === 'component2' ? 'darkgray' : 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            textAlign: 'left',
                            width: '100%',
                            padding: '8px'
                        }}
                    >
                        Prop Bets
                    </button>
                </li>
            </ul>
        </nav>
    );

}

export default Navbar;

//function Navbar() {
//  return (
//    <nav className="navbar">
//      <div className="logo">ApeOffside 🦍</div>
//      <ul className="nav-links">
//        <li><Link to="/">Home</Link></li>
//        <li><Link to="/explore">Explore</Link></li>
//        <li><Link to="/insights">Insights</Link></li>
//        <li><Link to="/about">About</Link></li>
//      </ul>
//    </nav>
//  );