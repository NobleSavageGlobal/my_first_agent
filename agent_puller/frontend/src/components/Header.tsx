import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-logo">
          <h1>Agent Puller</h1>
          <span className="tagline">SEC Edgar Narrative Shift Analyzer</span>
        </div>
        <nav className="header-nav">
          <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
            Dashboard
          </Link>
          <Link
            to="/companies"
            className={`nav-link ${isActive('/companies') ? 'active' : ''}`}
          >
            Companies
          </Link>
          <Link
            to="/analysis"
            className={`nav-link ${isActive('/analysis') ? 'active' : ''}`}
          >
            Analysis
          </Link>
          <Link
            to="/screen"
            className={`nav-link ${isActive('/screen') ? 'active' : ''}`}
          >
            Screen
          </Link>
          <Link
            to="/favorites"
            className={`nav-link ${isActive('/favorites') ? 'active' : ''}`}
          >
            Favorites
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
