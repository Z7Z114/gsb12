import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import MeetingList from './pages/MeetingList';
import MeetingDetail from './pages/MeetingDetail';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<MeetingList />} />
          <Route path="/meetings/:id" element={<MeetingDetail />} />
        </Routes>
      </main>
    </div>
  );
};

export default App;
