import React, { useState, useEffect } from 'react';
import { getAnalyticsExplorer } from '../services/api';
import { formatBrl, formatPct, formatNum } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import CustomerTable from '../components/common/CustomerTable';
import BarChartComponent from '../components/charts/BarChartComponent';
import { Search, RotateCcw, Download } from 'lucide-react';

export default function AnalyticsExplorer() {
  const [filters, setFilters] = useState({
    search_query: '',
    segment: 'All',
    risk_level: 'All',
    state: 'All',
    clv_band: 'All',
    recency_filter: 'All',
  });

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchExplorerData();
  }, [filters]);

  const fetchExplorerData = async () => {
    try {
      setLoading(true);
      const res = await getAnalyticsExplorer(filters);
      if (res.data && res.data.success) {
        setData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching explorer analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFilters({
      search_query: '',
      segment: 'All',
      risk_level: 'All',
      state: 'All',
      clv_band: 'All',
      recency_filter: 'All',
    });
  };

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Exploration & Governance
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Analytics Explorer & Multi-Criteria Discovery Hub
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Filter, search, slice, and drill down into customer records with multi-dimensional criteria and instant profile opening.
        </p>
      </div>

      {/* Filter & Search Panel */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <Search className="w-4 h-4 text-indigo-600" />
            <span>Multi-Criteria Filtering Controls</span>
          </h4>
          <button
            onClick={handleReset}
            className="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset All Filters</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="font-semibold text-slate-600 block mb-1">Search Keywords</label>
            <input
              type="text"
              placeholder="Customer ID, city, or category..."
              value={filters.search_query}
              onChange={(e) => setFilters((p) => ({ ...p, search_query: e.target.value }))}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="font-semibold text-slate-600 block mb-1">RFM Segment</label>
            <select
              value={filters.segment}
              onChange={(e) => setFilters((p) => ({ ...p, segment: e.target.value }))}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
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

          <div>
            <label className="font-semibold text-slate-600 block mb-1">Risk Level</label>
            <select
              value={filters.risk_level}
              onChange={(e) => setFilters((p) => ({ ...p, risk_level: e.target.value }))}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
            >
              <option value="All">All Risk Levels</option>
              <option value="High Risk (>=65%)">High Risk (>=65%)</option>
              <option value="Medium Risk (35-65%)">Medium Risk (35-65%)</option>
              <option value="Low Risk (<35%)">Low Risk (&lt;35%)</option>
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-600 block mb-1">State / Region</label>
            <select
              value={filters.state}
              onChange={(e) => setFilters((p) => ({ ...p, state: e.target.value }))}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
            >
              <option value="All">All States</option>
              {['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'DF', 'GO', 'ES', 'PE', 'CE'].map((st) => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-600 block mb-1">CLV Value Band</label>
            <select
              value={filters.clv_band}
              onChange={(e) => setFilters((p) => ({ ...p, clv_band: e.target.value }))}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
            >
              <option value="All">All Bands</option>
              <option value="Platinum">Platinum (VIP)</option>
              <option value="Gold">Gold</option>
              <option value="Silver">Silver</option>
              <option value="Bronze">Bronze</option>
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-600 block mb-1">Recency Window</label>
            <select
              value={filters.recency_filter}
              onChange={(e) => setFilters((p) => ({ ...p, recency_filter: e.target.value }))}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
            >
              <option value="All">All Windows</option>
              <option value="Recent (<90 days)">Recent (&lt;90 days)</option>
              <option value="Active (90-180 days)">Active (90-180 days)</option>
              <option value="Lapsed (181-365 days)">Lapsed (181-365 days)</option>
              <option value="Inactive (>365 days)">Inactive (&gt;365 days)</option>
            </select>
          </div>
        </div>
      </div>

      {loading || !data ? (
        <LoadingSpinner message="Filtering cohort analytics..." />
      ) : data.customers.length === 0 ? (
        <EmptyState
          title="No Matching Customer Profiles"
          description="No customer records match your active search filters. Try clearing your search keyword or broadening criteria."
          onReset={handleReset}
        />
      ) : (
        <>
          {/* Sliced Cohort Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard
              label="Matching Profiles"
              value={formatNum(data.kpis.matching_profiles)}
              subtitle="Customer records"
              icon="👥"
            />
            <KpiCard
              label="Total Filtered GMV"
              value={formatBrl(data.kpis.total_gmv)}
              subtitle="Gross spending"
              icon="💰"
            />
            <KpiCard
              label="Average 12M CLV"
              value={formatBrl(data.kpis.avg_clv)}
              subtitle="Forward value"
              icon="📈"
            />
            <KpiCard
              label="Average Churn Risk"
              value={formatPct(data.kpis.avg_churn_risk)}
              subtitle="Risk propensity"
              icon="🎯"
            />
          </div>

          {/* Sliced Distribution Histograms */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <BarChartComponent
              title="Spend Distribution of Filtered Cohort (BRL)"
              data={data.spend_distribution || []}
              xKey="range"
              yKey="count"
              color="#4F46E5"
              height={260}
            />
            <BarChartComponent
              title="Inactivity Recency Distribution (Days)"
              data={data.recency_distribution || []}
              xKey="range"
              yKey="count"
              color="#0284C7"
              height={260}
            />
          </div>

          {/* Paginated Customer Table */}
          <div className="space-y-3">
            <SectionHeader
              title={`Filtered Customer Cohort (${data.pagination.total.toLocaleString()} Profiles)`}
              subtitle="Click on any customer to inspect full 360 dossier"
            />
            <CustomerTable customers={data.customers} pageSize={25} />
          </div>
        </>
      )}
    </div>
  );
}
