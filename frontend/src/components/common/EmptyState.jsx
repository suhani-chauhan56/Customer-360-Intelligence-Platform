import React from 'react';

export default function EmptyState({ title = 'No Data Found', description, onReset, icon = '🔍' }) {
  return (
    <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center my-6">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-sm font-bold text-slate-900 mb-1">{title}</h3>
      {description && <p className="text-xs text-slate-500 max-w-md mx-auto mb-4">{description}</p>}
      {onReset && (
        <button
          onClick={onReset}
          className="inline-flex items-center px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm"
        >
          Reset Filters
        </button>
      )}
    </div>
  );
}
