import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UserCheck,
  Users,
  TrendingUp,
  AlertTriangle,
  Smile,
  Lightbulb,
  Search,
  ShieldCheck,
  BookOpen,
  Sparkles,
} from 'lucide-react';

export default function Sidebar({ filters, onFilterChange, onResetFilters }) {
  const navSections = [
    {
      title: 'Macro Analytics',
      items: [
        { path: '/', label: 'Executive Overview', icon: LayoutDashboard },
        { path: '/customers', label: 'Customer 360 Dossier', icon: UserCheck },
        { path: '/segmentation', label: 'RFM Segmentation', icon: Users },
        { path: '/clv', label: 'Customer Value / CLV', icon: TrendingUp },
      ],
    },
    {
      title: 'Predictive & Risk AI',
      items: [
        { path: '/churn', label: 'Churn Intelligence', icon: AlertTriangle },
        { path: '/sentiment', label: 'Sentiment & CSAT', icon: Smile },
        { path: '/recommendations', label: 'Action Engine', icon: Lightbulb },
      ],
    },
    {
      title: 'Exploration & Governance',
      items: [
        { path: '/explorer', label: 'Analytics Explorer', icon: Search },
        { path: '/data-quality', label: 'Data Quality & MLOps', icon: ShieldCheck },
        { path: '/methodology', label: 'Methodology & Standards', icon: BookOpen },
        { path: '/ask', label: 'Ask CustomerAtlas AI', icon: Sparkles },
      ],
    },
  ];

  return (
    <aside className="w-64 shrink-0 bg-white border-r border-slate-200 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-3.5rem)]">
      <div className="space-y-6">
        {navSections.map((section, idx) => (
          <div key={idx}>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2 px-2.5">
              {section.title}
            </div>
            <nav className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/'}
                    className={({ isActive }) =>
                      `flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${
                        isActive
                          ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {filters && onFilterChange && (
        <div className="pt-4 border-t border-slate-200 mt-6 space-y-3">
          <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-slate-500">
            <span>Global Audience Filter</span>
            <button
              onClick={onResetFilters}
              className="text-indigo-600 hover:text-indigo-700 font-semibold"
            >
              Reset
            </button>
          </div>
          <div>
            <label className="text-[11px] font-semibold text-slate-600 block mb-1">RFM Segment</label>
            <select
              value={filters.segment}
              onChange={(e) => onFilterChange('segment', e.target.value)}
              className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-md p-1.5 text-slate-700 focus:outline-none focus:border-indigo-500"
            >
              <option value="All">All Segments</option>
              <option value="Champions">Champions</option>
              <option value="Loyal Customers">Loyal Customers</option>
              <option value="Potential Loyalists">Potential Loyalists</option>
              <option value="Regular Customers">Regular Customers</option>
              <option value="At Risk">At Risk</option>
              <option value="Lost Customers">Lost Customers</option>
            </select>
          </div>
          <div>
            <label className="text-[11px] font-semibold text-slate-600 block mb-1">Risk Tier</label>
            <select
              value={filters.risk_level}
              onChange={(e) => onFilterChange('risk_level', e.target.value)}
              className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-md p-1.5 text-slate-700 focus:outline-none focus:border-indigo-500"
            >
              <option value="All">All Risk Levels</option>
              <option value="High Risk (>=65%)">High Risk (&gt;=65%)</option>
              <option value="Medium Risk (35-65%)">Medium Risk (35-65%)</option>
              <option value="Low Risk (<35%)">Low Risk (&lt;35%)</option>
            </select>
          </div>
        </div>
      )}
    </aside>
  );
}
