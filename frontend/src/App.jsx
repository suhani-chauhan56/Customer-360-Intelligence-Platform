import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layouts/AppLayout';
import ExecutiveOverview from './pages/ExecutiveOverview';
import Customer360 from './pages/Customer360';
import CustomerSegmentation from './pages/CustomerSegmentation';
import CustomerValue from './pages/CustomerValue';
import ChurnIntelligence from './pages/ChurnIntelligence';
import SentimentIntelligence from './pages/SentimentIntelligence';
import Recommendations from './pages/Recommendations';
import AnalyticsExplorer from './pages/AnalyticsExplorer';
import DataQuality from './pages/DataQuality';
import Methodology from './pages/Methodology';
import AskAtlas from './pages/AskAtlas';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<ExecutiveOverview />} />
          <Route path="dashboard" element={<Navigate to="/" replace />} />
          <Route path="customers" element={<Customer360 />} />
          <Route path="customers/:id" element={<Customer360 />} />
          <Route path="segmentation" element={<CustomerSegmentation />} />
          <Route path="rfm" element={<Navigate to="/segmentation" replace />} />
          <Route path="clv" element={<CustomerValue />} />
          <Route path="churn" element={<ChurnIntelligence />} />
          <Route path="sentiment" element={<SentimentIntelligence />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="explorer" element={<AnalyticsExplorer />} />
          <Route path="analytics" element={<Navigate to="/explorer" replace />} />
          <Route path="data-quality" element={<DataQuality />} />
          <Route path="methodology" element={<Methodology />} />
          <Route path="about" element={<Navigate to="/methodology" replace />} />
          <Route path="ask" element={<AskAtlas />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
