import React from 'react';
import { CheckCircle2, Circle } from 'lucide-react';

export default function LifecycleJourney({ lifecycle = [] }) {
  if (!lifecycle || lifecycle.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm mb-6">
      <div className="pb-3 border-b border-slate-100 mb-4">
        <h4 className="text-sm font-bold text-slate-900">Verifiable Customer Lifecycle Progression Journey</h4>
        <p className="text-xs text-slate-500 font-medium">Chronological account development milestones</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 relative">
        {lifecycle.map((stage, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg border flex flex-col justify-between ${
              stage.reached
                ? 'bg-indigo-50/40 border-indigo-200 text-indigo-950'
                : 'bg-slate-50/50 border-slate-200 text-slate-400 opacity-60'
            }`}
          >
            <div>
              <div className="flex items-center gap-1.5 mb-1.5">
                {stage.reached ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-300 shrink-0" />
                )}
                <span className="text-xs font-bold">{stage.stage}</span>
              </div>
              <p className="text-[11px] leading-tight text-slate-600 mb-2">{stage.description}</p>
            </div>
            <div className="text-[10.5px] font-mono font-semibold text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200 inline-block w-fit">
              {stage.date}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
