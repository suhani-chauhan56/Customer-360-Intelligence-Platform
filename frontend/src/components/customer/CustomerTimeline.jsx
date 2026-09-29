import React from 'react';
import { formatDate, formatBrl } from '../../utils/formatting';
import { ShoppingBag, Star } from 'lucide-react';

export default function CustomerTimeline({ orders = [], reviews = [] }) {
  if (orders.length === 0) return null;

  const reviewMap = {};
  reviews.forEach((r) => {
    if (r.order_id) reviewMap[r.order_id] = r;
  });

  return (
    <div className="my-4">
      <h5 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
        Chronological Activity Timeline ({orders.length} events)
      </h5>
      <div className="relative pl-6 border-l-2 border-indigo-200 space-y-4">
        {orders.map((o, idx) => {
          const rev = reviewMap[o.order_id];
          return (
            <div key={o.order_id || idx} className="relative group">
              <span className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-indigo-600 border-2 border-white shadow-sm flex items-center justify-center text-[9px] text-white">
                <ShoppingBag className="w-2.5 h-2.5" />
              </span>
              <div className="bg-white border border-slate-200 rounded-lg p-3 shadow-2xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">Order #{o.order_id ? o.order_id.substring(0, 8) : 'N/A'}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 font-semibold text-slate-700">
                      {o.order_status || 'delivered'}
                    </span>
                  </div>
                  <span className="font-mono text-slate-500 font-semibold">{formatDate(o.purchase_date)}</span>
                </div>
                <div className="text-xs text-slate-600 flex items-center gap-3">
                  <span>Gross Value: <strong>{formatBrl(o.revenue)}</strong></span>
                  <span>•</span>
                  <span>Freight: <strong>{formatBrl(o.freight_value)}</strong></span>
                </div>
                {rev && (
                  <div className="mt-2 pt-2 border-t border-slate-100 flex items-start gap-2 text-xs bg-amber-50/50 p-2 rounded">
                    <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-400 mt-0.5 shrink-0" />
                    <div>
                      <div className="font-bold text-slate-800 flex items-center gap-1.5">
                        <span>{rev.review_score} / 5 Stars</span>
                        <span className="text-[10.5px] font-normal text-slate-500">({rev.sentiment_category})</span>
                      </div>
                      {rev.review_comment_message && (
                        <p className="text-slate-600 italic mt-0.5">"{rev.review_comment_message}"</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
