import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from 'recharts';
import { formatBrl, formatNum } from '../../utils/formatting';

const DEFAULT_COLORS = ['#4F46E5', '#0284C7', '#16A34A', '#F59E0B', '#DC2626', '#8B5CF6', '#EC4899', '#14B8A6'];

export default function BarChartComponent({
  data = [],
  xKey,
  yKey,
  title,
  height = 300,
  horizontal = false,
  isCurrency = false,
  color = '#4F46E5',
  colors = DEFAULT_COLORS,
  useMultiColor = false,
}) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 text-center text-slate-400 text-xs flex items-center justify-center" style={{ height }}>
        No chart data available
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const val = payload[0].value;
      return (
        <div className="bg-slate-900 text-white text-xs rounded-lg p-2.5 shadow-lg border border-slate-800">
          <div className="font-semibold text-slate-200">{label}</div>
          <div className="font-bold text-indigo-300 mt-0.5">
            {isCurrency ? formatBrl(val) : formatNum(val)}
          </div>
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
          {horizontal ? (
            <BarChart layout="vertical" data={data} margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis
                type="number"
                tick={{ fontSize: 11, fill: '#64748B' }}
                tickFormatter={(v) => (isCurrency ? `R$${v > 1000 ? `${(v / 1000).toFixed(0)}k` : v}` : formatNum(v))}
              />
              <YAxis
                type="category"
                dataKey={xKey}
                tick={{ fontSize: 11, fill: '#334155', fontWeight: 500 }}
                width={120}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey={yKey} radius={[0, 4, 4, 0]} fill={color}>
                {useMultiColor &&
                  data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
              </Bar>
            </BarChart>
          ) : (
            <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fontSize: 11, fill: '#64748B', fontWeight: 500 }}
                interval={0}
                angle={-20}
                textAnchor="end"
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#64748B' }}
                tickFormatter={(v) => (isCurrency ? `R$${v > 1000 ? `${(v / 1000).toFixed(0)}k` : v}` : formatNum(v))}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey={yKey} radius={[4, 4, 0, 0]} fill={color}>
                {useMultiColor &&
                  data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
