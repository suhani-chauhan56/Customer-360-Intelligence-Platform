import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Moon,
  Sun,
  Bell,
  Sparkles,
  ExternalLink,
  HelpCircle,
  Database,
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface HeaderProps {
  collapsed: boolean;
}

export const Header: React.FC<HeaderProps> = ({ collapsed }) => {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/explorer?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header
      className={`fixed top-0 right-0 z-20 h-16 bg-white/90 dark:bg-surface-900/90 backdrop-blur-md border-b border-surface-200 dark:border-surface-800 transition-all duration-300 flex items-center justify-between px-6 ${
        collapsed ? 'left-20' : 'left-64'
      }`}
    >
      {/* Search Input Bar */}
      <form onSubmit={handleSearchSubmit} className="relative w-full max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-surface-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Quick search Customer ID, City, or Segment (Press Enter)..."
          className="w-full pl-9 pr-4 py-1.5 text-xs rounded-xl bg-surface-100/80 dark:bg-surface-800/80 border border-surface-200 dark:border-surface-700 focus:outline-none focus:ring-2 focus:ring-brand-500 text-surface-800 dark:text-surface-100 placeholder-surface-400 dark:placeholder-surface-500 transition-all"
        />
      </form>

      {/* Right Utility Bar */}
      <div className="flex items-center space-x-3">
        {/* Grounded AI Quick Launch */}
        <button
          onClick={() => navigate('/ask-atlas')}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 text-white text-xs font-medium shadow-sm hover:opacity-95 transition-all"
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span>Ask Atlas AI</span>
        </button>

        {/* Dataset Status Pill */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-100 dark:bg-surface-800 text-[11px] text-surface-600 dark:text-surface-300 border border-surface-200 dark:border-surface-700">
          <Database className="h-3 w-3 text-brand-500" />
          <span>Feature Store v2.0</span>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-surface-600" />}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-xl text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors relative"
            title="Notifications"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-brand-500"></span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 rounded-2xl bg-white dark:bg-surface-900 shadow-xl border border-surface-200 dark:border-surface-800 p-4 space-y-3 z-50">
              <div className="flex items-center justify-between pb-2 border-b border-surface-100 dark:border-surface-800">
                <span className="text-xs font-bold text-surface-900 dark:text-white">Commercial Alerts</span>
                <span className="text-[10px] text-brand-600 dark:text-brand-400 font-semibold">3 Active</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50">
                  <div className="font-semibold text-amber-900 dark:text-amber-200">High Risk VIP Segment Alert</div>
                  <div className="text-amber-700 dark:text-amber-300 text-[11px] mt-0.5">342 Champion accounts have crossed the 65% churn risk boundary.</div>
                </div>
                <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900/50">
                  <div className="font-semibold text-indigo-900 dark:text-indigo-200">Model Stability Audit Passed</div>
                  <div className="text-indigo-700 dark:text-indigo-300 text-[11px] mt-0.5">All 6 monitored features exhibit PSI &lt; 0.02. Distributions are stable.</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
