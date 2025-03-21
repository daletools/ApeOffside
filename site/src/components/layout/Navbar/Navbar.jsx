import React from "react";
import "./Navbar.css"

function Navbar() {
    return (
        <nav className="navbar">
            <div className="nav-left">
                <a href="/public" className="logo">
                    SmartPlayer
                </a>
            </div>
            <div className="nav-center">
                <a href="/public" className="link">
                    Home
                </a>
            </div>
            <div className="nav-right">

            </div>
        </nav>
    )
}

export default Navbar;