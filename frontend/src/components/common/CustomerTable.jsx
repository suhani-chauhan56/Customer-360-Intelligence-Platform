import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { formatBrl, formatPct } from '../../utils/formatting';
import Badge from './Badge';

export default function CustomerTable({
  customers = [],
  pageSize = 10,
  showPagination = true,
  onSelectCustomer,
}) {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);

  const total = customers.length;
  const totalPages = Math.ceil(total / pageSize) || 1;
  const startIdx = (currentPage - 1) * pageSize;
  const currentData = customers.slice(startIdx, startIdx + pageSize);

  const handleRowClick = (customerId) => {
    if (onSelectCustomer) {
      onSelectCustomer(customerId);
    } else {
      navigate(`/customers/${customerId}`);
    }
  };

  const getSegmentColor = (segment) => {
    switch (segment) {
      case 'Champions':
        return 'green';
      case 'Loyal Customers':
        return 'blue';
      case 'Potential Loyalists':
        return 'purple';
      case 'At Risk':
        return 'amber';
      case 'Lost Customers':
        return 'red';
      default:
        return 'indigo';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
              <th className="py-3 px-3.5">Customer ID</th>
              <th className="py-3 px-3.5">RFM Segment</th>
              <th className="py-3 px-3.5 text-right">Total Spend</th>
              <th className="py-3 px-3.5 text-right">Orders</th>
              <th className="py-3 px-3.5 text-right">Recency</th>
              <th className="py-3 px-3.5 text-right">12M CLV</th>
              <th className="py-3 px-3.5 text-right">Churn Risk</th>
              <th className="py-3 px-3.5 text-right">Priority Score</th>
              <th className="py-3 px-3.5">State</th>
              <th className="py-3 px-3.5 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-800">
            {currentData.map((c) => {
              const churnP = c.churn_probability || 0;
              const churnColor = churnP >= 0.65 ? 'text-rose-600 font-bold' : churnP >= 0.35 ? 'text-amber-600 font-bold' : 'text-emerald-600 font-bold';

              return (
                <tr
                  key={c.customer_id}
                  onClick={() => handleRowClick(c.customer_id)}
                  className="hover:bg-indigo-50/50 cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-3.5 font-mono text-indigo-600 font-semibold">
                    {c.customer_id ? `${c.customer_id.substring(0, 10)}...` : 'N/A'}
                  </td>
                  <td className="py-2.5 px-3.5">
                    <Badge color={getSegmentColor(c.rfm_segment)}>{c.rfm_segment}</Badge>
                  </td>
                  <td className="py-2.5 px-3.5 text-right font-semibold">{formatBrl(c.total_spend)}</td>
                  <td className="py-2.5 px-3.5 text-right">{c.total_orders}</td>
                  <td className="py-2.5 px-3.5 text-right">{Math.round(c.recency_days)}d</td>
                  <td className="py-2.5 px-3.5 text-right font-semibold text-indigo-700">{formatBrl(c.predicted_clv)}</td>
                  <td className={`py-2.5 px-3.5 text-right ${churnColor}`}>{formatPct(churnP)}</td>
                  <td className="py-2.5 px-3.5 text-right font-mono font-bold text-slate-900">{c.priority_score || '0.0'}</td>
                  <td className="py-2.5 px-3.5 font-bold text-slate-600">{c.state || 'SP'}</td>
                  <td className="py-2.5 px-3.5 text-center">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRowClick(c.customer_id);
                      }}
                      className="px-2 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-semibold rounded transition-colors"
                    >
                      View 360 →
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {showPagination && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-t border-slate-200 text-xs">
          <span className="text-slate-500 font-medium">
            Showing <span className="font-semibold text-slate-800">{startIdx + 1}</span> to{' '}
            <span className="font-semibold text-slate-800">{Math.min(startIdx + pageSize, total)}</span> of{' '}
            <span className="font-semibold text-slate-800">{total.toLocaleString()}</span> customers
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-2.5 py-1 bg-white border border-slate-200 rounded font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition-colors"
            >
              Prev
            </button>
            <span className="px-2.5 py-1 font-semibold text-slate-700">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-2.5 py-1 bg-white border border-slate-200 rounded font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
