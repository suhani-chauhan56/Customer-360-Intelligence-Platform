import React from 'react';

export default function Footer() {
  return (
    <footer className="mt-12 py-6 border-t border-slate-200 bg-white text-center text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div>
          <span className="font-bold text-slate-700">CustomerAtlas AI</span> — Unified Customer Intelligence & MLOps Decision Support Platform
        </div>
        <div className="flex items-center gap-4 text-[11px] font-medium text-slate-400">
          <span>Enterprise MERN Architecture</span>
          <span>•</span>
          <span>Zero Streamlit Dependency</span>
          <span>•</span>
          <span>Vercel Production Deployment</span>
        </div>
      </div>
    </footer>
  );
}
