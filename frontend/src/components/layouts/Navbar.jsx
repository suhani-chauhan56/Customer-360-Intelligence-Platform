import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Compass, Sparkles, Activity } from 'lucide-react';

export default function Navbar({ totalProfiles = 94983 }) {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2.5 font-extrabold text-slate-900 tracking-tight text-base hover:opacity-90">
            <span className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm shadow-indigo-200">
              <Compass className="w-5 h-5" />
            </span>
            <span>CustomerAtlas <span className="text-indigo-600 font-bold">AI</span></span>
          </Link>
          <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
            Enterprise MERN v2.0
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500 font-medium bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Canonical Feature Store: <strong>{totalProfiles.toLocaleString()} Profiles</strong></span>
          </div>

          <Link
            to="/ask"
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg shadow-sm transition-all ${
              location.pathname === '/ask'
                ? 'bg-indigo-700 text-white shadow-indigo-300'
                : 'bg-indigo-600 hover:bg-indigo-700 text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ask CustomerAtlas</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
