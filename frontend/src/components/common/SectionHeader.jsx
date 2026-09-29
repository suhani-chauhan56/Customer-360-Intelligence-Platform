import React from 'react';

export default function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 mb-4 border-b border-slate-200">
      <div>
        <h3 className="text-base font-bold text-slate-900 tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs text-slate-500 font-medium">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
