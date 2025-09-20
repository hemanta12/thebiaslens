import React from 'react';
import './App.css';

import { Routes, Route } from 'react-router-dom';
import Analyze from './routes/Analyze';
import Recents from './routes/Recents';
import Settings from './routes/Settings';
import Details from './routes/Details';
import Search from './routes/Search';
import Layout from './components/Layout';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Search />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/recents" element={<Recents />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
          <Route path="/details/:id" element={<Details />} />
        </Routes>
      </header>
    </div>
  );
}

export default App;
