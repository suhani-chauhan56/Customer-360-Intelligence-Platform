import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

export default function AppLayout() {
  const [filters, setFilters] = useState({
    segment: 'All',
    risk_level: 'All',
    state: 'All',
    clv_band: 'All',
    recency_filter: 'All',
  });

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleResetFilters = () => {
    setFilters({
      segment: 'All',
      risk_level: 'All',
      state: 'All',
      clv_band: 'All',
      recency_filter: 'All',
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar totalProfiles={94983} />
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar
          filters={filters}
          onFilterChange={handleFilterChange}
          onResetFilters={handleResetFilters}
        />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto max-w-full">
          <Outlet context={{ filters, handleFilterChange, handleResetFilters }} />
        </main>
      </div>
      <Footer />
    </div>
  );
}
