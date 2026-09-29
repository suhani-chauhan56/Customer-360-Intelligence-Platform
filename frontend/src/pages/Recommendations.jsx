import React, { useState, useEffect } from 'react';
import { getRecommendations } from '../services/api';
import { formatBrl, formatPct, formatNum } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Badge from '../components/common/Badge';
import BarChartComponent from '../components/charts/BarChartComponent';
import { Lightbulb, Download, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Recommendations() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [actionFilter, setActionFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [segmentFilter, setSegmentFilter] = useState('All');
  const [showRules, setShowRules] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, [actionFilter, priorityFilter, segmentFilter]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const res = await getRecommendations({
        action_type: actionFilter,
        priority: priorityFilter,
        segment: segmentFilter,
      });
      if (res.data && res.data.success) {
        setData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <LoadingSpinner message="Evaluating multi-signal action recommendations..." />;
  }

  const { kpis, summary = [], rules = [], queue = [], category_catalog_sample = [] } = data;

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Predictive & Risk AI
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">Customer Action Recommendation Engine</h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Transparent, multi-signal customer action recommendation engine with documented decision rules and priority queues.
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Actionable Profiles"
          value={formatNum(kpis.actionable_profiles)}
          subtitle="Evaluated cohort records"
          icon="🎯"
        />
        <KpiCard
          label="Urgent Action Required"
          value={formatNum(kpis.urgent_count)}
          delta={`${formatNum(kpis.high_count)} High Priority`}
          deltaDirection="negative"
          subtitle="Service recovery / VIP retention"
          icon="🚨"
        />
        <KpiCard
          label="Top Recommended Strategy"
          value={kpis.top_action}
          subtitle="Largest action volume"
          icon="💡"
        />
        <KpiCard
          label="Covered Revenue"
          value={formatBrl(kpis.covered_revenue)}
          subtitle="Total gross merchandise spend"
          icon="💰"
        />
      </div>

      {/* Action Allocation Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5">
          <BarChartComponent
            title="Customer Count by Recommended Action"
            data={summary}
            xKey="action_type"
            yKey="customer_count"
            horizontal={true}
            useMultiColor={true}
            height={280}
          />
        </div>

        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col justify-between">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
            Strategy Allocation Summary Matrix
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                  <th className="py-2.5 px-3">Action Strategy</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3 text-right">Customers</th>
                  <th className="py-2.5 px-3 text-right">Total GMV</th>
                  <th className="py-2.5 px-3 text-right">Avg 12M CLV</th>
                  <th className="py-2.5 px-3 text-right">Churn Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {summary.map((s, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-2 px-3 font-bold text-slate-900">{s.action_type}</td>
                    <td className="py-2 px-3">
                      <span
                        className="px-2 py-0.5 rounded text-[10.5px] font-bold text-white"
                        style={{ backgroundColor: s.badge_color }}
                      >
                        {s.priority}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">{formatNum(s.customer_count)}</td>
                    <td className="py-2 px-3 text-right font-bold">{formatBrl(s.total_gmv)}</td>
                    <td className="py-2 px-3 text-right text-indigo-700 font-semibold">{formatBrl(s.avg_clv)}</td>
                    <td className="py-2 px-3 text-right font-bold text-rose-600">{formatPct(s.avg_churn_risk)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Documented Decision Rules Matrix */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <button
          onClick={() => setShowRules(!showRules)}
          className="w-full flex items-center justify-between p-4 text-left font-bold text-xs text-slate-800 hover:bg-slate-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
            <span>Documented Recommendation Decision Rules & Commercial Targeting Matrix ({rules.length} Rules)</span>
          </div>
          {showRules ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </button>

        {showRules && (
          <div className="p-5 border-t border-slate-100 overflow-x-auto bg-slate-50/50">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                  <th className="py-2.5 px-3">Strategy / Action</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3">Target Audience Criteria</th>
                  <th className="py-2.5 px-3">Execution Channel</th>
                  <th className="py-2.5 px-3">Commercial Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-medium">
                {rules.map((r, idx) => (
                  <tr key={idx} className="hover:bg-white transition-colors">
                    <td className="py-2.5 px-3 font-bold text-slate-900">{r.action_type}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className="px-2 py-0.5 rounded text-[10.5px] font-bold text-white"
                        style={{ backgroundColor: r.badge_color }}
                      >
                        {r.priority}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-700">{r.target_audience}</td>
                    <td className="py-2.5 px-3 text-indigo-700 font-semibold">{r.channel}</td>
                    <td className="py-2.5 px-3 text-slate-600">{r.rationale}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Actionable Customer Recommendation Queue */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="Actionable Customer Recommendation Queue"
          subtitle={`Displaying ${queue.length} prioritized commercial actions`}
        />

        {/* Filter Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
          <div>
            <label className="font-bold text-slate-600 block mb-1">Filter by Action Type</label>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded p-1.5"
            >
              <option value="All">All Actions</option>
              {rules.map((r) => (
                <option key={r.action_type} value={r.action_type}>{r.action_type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="font-bold text-slate-600 block mb-1">Filter by Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded p-1.5"
            >
              <option value="All">All Priorities</option>
              <option value="Urgent">Urgent</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Standard">Standard</option>
            </select>
          </div>

          <div>
            <label className="font-bold text-slate-600 block mb-1">Filter by RFM Segment</label>
            <select
              value={segmentFilter}
              onChange={(e) => setSegmentFilter(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded p-1.5"
            >
              <option value="All">All Segments</option>
              <option value="Champions">Champions</option>
              <option value="Loyal Customers">Loyal Customers</option>
              <option value="Potential Loyalists">Potential Loyalists</option>
              <option value="Regular Customers">Regular Customers</option>
              <option value="At Risk">At Risk</option>
              <option value="Lost Customers">Lost Customers</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <th className="py-2.5 px-3">Customer ID</th>
                <th className="py-2.5 px-3">Recommended Action</th>
                <th className="py-2.5 px-3">Priority</th>
                <th className="py-2.5 px-3">RFM Segment</th>
                <th className="py-2.5 px-3">Decision Rationale</th>
                <th className="py-2.5 px-3 text-right">12M CLV</th>
                <th className="py-2.5 px-3 text-right">Churn Risk</th>
                <th className="py-2.5 px-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {queue.map((q) => (
                <tr
                  key={q.customer_id}
                  onClick={() => navigate(`/customers/${q.customer_id}`)}
                  className="hover:bg-indigo-50/40 cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-3 font-mono text-indigo-600 font-bold">{q.customer_id ? `${q.customer_id.substring(0, 10)}...` : 'N/A'}</td>
                  <td className="py-2.5 px-3 font-bold text-slate-900">{q.action_type}</td>
                  <td className="py-2.5 px-3">
                    <span
                      className="px-2 py-0.5 rounded text-[10.5px] font-bold text-white"
                      style={{ backgroundColor: q.badge_color }}
                    >
                      {q.priority}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-semibold text-slate-700">{q.rfm_segment}</td>
                  <td className="py-2.5 px-3 text-slate-600 max-w-xs truncate">{q.reason}</td>
                  <td className="py-2.5 px-3 text-right font-bold text-indigo-700">{formatBrl(q.predicted_clv)}</td>
                  <td className="py-2.5 px-3 text-right font-bold text-rose-600">{formatPct(q.churn_probability)}</td>
                  <td className="py-2.5 px-3 text-center">
                    <button className="px-2 py-1 bg-indigo-50 text-indigo-700 font-bold rounded text-[11px]">
                      View 360 →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Next-Best-Category Cross-Sell Catalog Sample */}
      {category_catalog_sample.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3">
          <SectionHeader
            title="Next-Best-Category Cross-Sell Catalog"
            subtitle="Market Basket Co-Occurrence Recommendations Sample"
          />
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                  <th className="py-2.5 px-3">Customer ID</th>
                  <th className="py-2.5 px-3 text-center">Rank</th>
                  <th className="py-2.5 px-3">Recommended Category</th>
                  <th className="py-2.5 px-3">Recommendation Reason</th>
                  <th className="py-2.5 px-3">Method</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {category_catalog_sample.slice(0, 15).map((rec, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-2 px-3 font-mono text-indigo-600 font-semibold">{rec.customer_id}</td>
                    <td className="py-2 px-3 text-center font-bold">#{rec.rank}</td>
                    <td className="py-2 px-3 font-bold capitalize text-slate-800">{rec.recommended_category.replace(/_/g, ' ')}</td>
                    <td className="py-2 px-3 text-slate-600">{rec.reason}</td>
                    <td className="py-2 px-3">
                      <Badge color="indigo">{rec.method}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
