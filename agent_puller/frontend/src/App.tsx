import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Companies from './pages/Companies';
import Analysis from './pages/Analysis';
import Screening from './pages/Screening';
import Favorites from './pages/Favorites';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/screen" element={<Screening />} />
            <Route path="/favorites" element={<Favorites />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
