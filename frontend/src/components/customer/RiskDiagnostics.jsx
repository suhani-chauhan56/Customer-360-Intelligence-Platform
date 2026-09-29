import React from 'react';
import { AlertCircle, ShieldCheck } from 'lucide-react';

export default function RiskDiagnostics({ riskDiagnostics, actionInfo }) {
  if (!riskDiagnostics) return null;

  const riskFactors = riskDiagnostics.risk_factors || [];
  const protectiveFactors = riskDiagnostics.protective_factors || [];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
      <div className="bg-rose-50/50 border border-rose-200 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-2 text-rose-800 font-bold text-xs">
          <AlertCircle className="w-4 h-4" />
          <span>Factual Risk Drivers ({riskFactors.length})</span>
        </div>
        {riskFactors.length > 0 ? (
          <ul className="space-y-1.5 text-xs text-rose-950 font-medium">
            {riskFactors.map((f, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="text-rose-500 font-bold">•</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-slate-500">No elevated risk indicators recorded.</p>
        )}
      </div>

      <div className="bg-emerald-50/50 border border-emerald-200 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-2 text-emerald-800 font-bold text-xs">
          <ShieldCheck className="w-4 h-4" />
          <span>Protective Account Anchors ({protectiveFactors.length})</span>
        </div>
        {protectiveFactors.length > 0 ? (
          <ul className="space-y-1.5 text-xs text-emerald-950 font-medium">
            {protectiveFactors.map((f, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="text-emerald-500 font-bold">•</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-xs text-slate-500">No strong protective factors identified.</p>
        )}
      </div>
    </div>
  );
}
