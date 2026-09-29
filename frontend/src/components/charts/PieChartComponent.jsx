import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { formatNum, formatPct } from '../../utils/formatting';

const DEFAULT_COLORS = ['#4F46E5', '#0284C7', '#16A34A', '#F59E0B', '#DC2626', '#8B5CF6'];

export default function PieChartComponent({
  data = [],
  nameKey = 'name',
  dataKey = 'count',
  title,
  height = 300,
  colors = DEFAULT_COLORS,
  innerRadius = 60,
  outerRadius = 90,
}) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 text-center text-slate-400 text-xs flex items-center justify-center" style={{ height }}>
        No chart data available
      </div>
    );
  }

  const total = data.reduce((sum, item) => sum + (item[dataKey] || 0), 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const { name, value } = payload[0];
      const pct = total > 0 ? (value / total) * 100 : 0;
      return (
        <div className="bg-slate-900 text-white text-xs rounded-lg p-2.5 shadow-lg border border-slate-800">
          <div className="font-semibold text-slate-200">{name}</div>
          <div className="font-bold text-indigo-300 mt-0.5">
            {formatNum(value)} profiles ({pct.toFixed(1)}%)
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      {title && <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">{title}</h4>}
      <div style={{ height, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={innerRadius}
              outerRadius={outerRadius}
              paddingAngle={2}
              dataKey={dataKey}
              nameKey={nameKey}
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.color || colors[index % colors.length]}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              wrapperStyle={{ fontSize: '11px', color: '#64748B' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
