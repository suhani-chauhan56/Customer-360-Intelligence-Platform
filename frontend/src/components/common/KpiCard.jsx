import React from 'react';

export default function KpiCard({ label, value, subtitle, delta, deltaDirection = 'positive', icon }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow transition-shadow">
      <div className="flex items-center justify-between text-slate-500 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</span>
        {icon && <span className="text-lg">{icon}</span>}
      </div>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
        {delta && (
          <span
            className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
              deltaDirection === 'positive'
                ? 'bg-emerald-50 text-emerald-700'
                : deltaDirection === 'negative'
                ? 'bg-rose-50 text-rose-700'
                : 'bg-slate-100 text-slate-700'
            }`}
          >
            {delta}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-slate-500 line-clamp-1">{subtitle}</p>}
    </div>
  );
}
