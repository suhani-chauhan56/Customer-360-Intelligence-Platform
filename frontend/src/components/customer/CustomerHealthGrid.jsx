import React from 'react';

export default function CustomerHealthGrid({ health }) {
  if (!health) return null;

  const vitals = health.vitals || [];

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm mb-6">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <div>
          <h4 className="text-sm font-bold text-slate-900">Customer Vital Health Signs & Composite Score</h4>
          <p className="text-xs text-slate-500 font-medium">6-dimension normalized health indicator framework</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">Composite Score:</span>
          <span
            className="text-sm font-extrabold px-2.5 py-1 rounded-lg text-white"
            style={{ backgroundColor: health.badge_color || '#16A34A' }}
          >
            {health.total_score} / 100 ({health.health_tier})
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {vitals.map((v, i) => (
          <div
            key={i}
            className="bg-slate-50/70 border border-slate-200/80 rounded-lg p-3 flex items-start gap-3"
          >
            <div className="text-2xl pt-0.5">{v.icon}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-1">
                <span className="text-xs font-bold text-slate-800">{v.dimension}</span>
                <span
                  className="text-[11px] font-bold px-1.5 py-0.5 rounded"
                  style={{ color: v.color, backgroundColor: `${v.color}15` }}
                >
                  {v.rating}
                </span>
              </div>
              <p className="text-[11.5px] text-slate-500 font-medium mt-0.5 line-clamp-1">{v.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
