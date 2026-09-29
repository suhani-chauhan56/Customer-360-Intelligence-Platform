import React from 'react';

export default function InsightCard({ title, observation, evidence, implication, badge, kind = 'info' }) {
  const borderColors = {
    info: 'border-l-indigo-500',
    success: 'border-l-emerald-500',
    warning: 'border-l-amber-500',
    alert: 'border-l-rose-500',
  };

  const badgeColors = {
    info: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    alert: 'bg-rose-50 text-rose-700 border-rose-200',
  };

  return (
    <div className={`bg-white rounded-xl border border-slate-200 border-l-4 ${borderColors[kind] || borderColors.info} p-5 shadow-sm mb-4`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-bold text-slate-900">{title}</h4>
        {badge && (
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${badgeColors[kind] || badgeColors.info}`}>
            {badge}
          </span>
        )}
      </div>
      {observation && <p className="text-xs text-slate-700 font-medium mb-2">{observation}</p>}
      {evidence && (
        <div className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 mb-2.5 font-mono leading-relaxed">
          <span className="font-semibold text-slate-700 font-sans mr-1">Evidence:</span> {evidence}
        </div>
      )}
      {implication && (
        <p className="text-xs text-indigo-700 font-semibold flex items-center gap-1.5">
          <span>💡</span> <span>{implication}</span>
        </p>
      )}
    </div>
  );
}
