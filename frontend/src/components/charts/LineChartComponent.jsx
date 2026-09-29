import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { formatBrl, formatNum } from '../../utils/formatting';

export default function LineChartComponent({
  data = [],
  xKey = 'month',
  barKey = 'revenue',
  lineKey = 'orders',
  barLabel = 'Merchandise GMV (BRL)',
  lineLabel = 'Completed Orders',
  title,
  height = 320,
}) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 text-center text-slate-400 text-xs flex items-center justify-center" style={{ height }}>
        No trend data available
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 text-white text-xs rounded-lg p-3 shadow-lg border border-slate-800 space-y-1">
          <div className="font-bold text-slate-200">{label}</div>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center justify-between gap-4 font-medium" style={{ color: entry.color }}>
              <span>{entry.name}:</span>
              <span className="font-bold font-mono">
                {entry.dataKey === barKey ? formatBrl(entry.value) : formatNum(entry.value)}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      {title && <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-4">{title}</h4>}
      <div style={{ height, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 20, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 11, fill: '#64748B' }}
              angle={-20}
              textAnchor="end"
            />
            <YAxis
              yAxisId="left"
              tick={{ fontSize: 11, fill: '#64748B' }}
              tickFormatter={(v) => `R$${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              tick={{ fontSize: 11, fill: '#F59E0B' }}
              tickFormatter={(v) => formatNum(v)}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px' }} />
            <Bar yAxisId="left" dataKey={barKey} name={barLabel} fill="#4F46E5" radius={[4, 4, 0, 0]} opacity={0.85} />
            <Line yAxisId="right" type="monotone" dataKey={lineKey} name={lineLabel} stroke="#F59E0B" strokeWidth={3} dot={{ r: 3 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
