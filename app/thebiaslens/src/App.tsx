import React from 'react';
import './App.css';

import { Routes, Route } from 'react-router-dom';
import AnalyzePage from './routes/AnalyzePage';
import AnalyzePageById from './routes/AnalyzePageById';
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
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/analyze/:id" element={<AnalyzePageById />} />
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
