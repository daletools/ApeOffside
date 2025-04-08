import React from "react";
import "./Navbar.css";
import { Link } from "react-router-dom"; // if you're using React Router

function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">ApeOffside 🦍</div>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/explore">Explore</Link></li>
        <li><Link to="/insights">Insights</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>
    </nav>
  );
}

export default Navbar;
