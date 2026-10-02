import React from 'react';

export default function GaugeChart({
  value = 0, // 0 to 1
  label = 'Churn Propensity',
  actionInfo,
}) {
  const percentage = Math.min(100, Math.max(0, value * 100));

  let color = '#16A34A';
  let tier = 'Low Risk';
  if (percentage >= 65) {
    color = '#DC2626';
    tier = 'High Risk';
  } else if (percentage >= 35) {
    color = '#F59E0B';
    tier = 'Medium Risk';
  }

  // Semi-circle SVG gauge
  const radius = 60;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col items-center text-center">
      <span className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">{label}</span>
      <div className="relative w-40 h-24 flex items-end justify-center overflow-hidden">
        <svg className="w-40 h-40 transform -rotate-180" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke="#f1f5f9"
            strokeWidth="14"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset="0"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke={color}
            strokeWidth="14"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute bottom-1 flex flex-col items-center">
          <span className="text-2xl font-extrabold text-slate-900 font-mono tracking-tight">
            {percentage.toFixed(1)}%
          </span>
          <span
            className="text-[11px] font-bold px-2 py-0.5 rounded-full mt-0.5"
            style={{ color, backgroundColor: `${color}15` }}
          >
            {tier}
          </span>
        </div>
      </div>
      {actionInfo && (
        <div className="mt-3 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-left w-full">
          <span className="font-bold text-slate-800">Action: </span>
          <span>
            {typeof actionInfo === 'string'
              ? actionInfo
              : actionInfo.action || actionInfo.description || actionInfo.action_type || ''}
          </span>
        </div>
      )}
    </div>
  );
}
