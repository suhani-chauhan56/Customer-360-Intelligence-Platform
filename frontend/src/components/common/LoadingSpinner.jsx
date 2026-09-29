import React from 'react';

export default function LoadingSpinner({ message = 'Computing analytics...' }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-3">
      <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      <p className="text-xs font-semibold text-slate-600 animate-pulse">{message}</p>
    </div>
  );
}
