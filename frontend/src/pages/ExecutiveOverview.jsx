import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { getDashboardOverview } from '../services/api';
import { formatBrl, formatPct, formatNum } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import InsightCard from '../components/common/InsightCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import PieChartComponent from '../components/charts/PieChartComponent';
import BarChartComponent from '../components/charts/BarChartComponent';
import LineChartComponent from '../components/charts/LineChartComponent';
import { Download } from 'lucide-react';

export default function ExecutiveOverview() {
  const { filters } = useOutletContext();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
  }, [filters]);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const res = await getDashboardOverview(filters);
      if (res.data && res.data.success) {
        setData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching dashboard overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCsv = () => {
    window.open(`/api/customers?limit=95000`, '_blank');
  };

  if (loading || !data) {
    return <LoadingSpinner message="Calculating dynamic executive KPIs & macro distributions..." />;
  }

  const { kpis, insights = [], audience_composition, monthly_trajectory, segment_revenue, state_revenue } = data;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
              Executive Overview
            </div>
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">Customer Intelligence Overview</h1>
            <p className="text-xs text-slate-500 font-medium mt-1">
              Understand customer value, retention, risk and engagement at a glance.
            </p>
          </div>
          <button
            onClick={handleDownloadCsv}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export Executive Dataset</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Rows */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Total Customers"
          value={formatNum(kpis.total_customers)}
          subtitle="Current dataset view"
          icon="👥"
        />
        <KpiCard
          label="Active Customers"
          value={formatNum(kpis.active_customers)}
          subtitle={`${formatPct(kpis.active_rate)} active (<=180d)`}
          icon="⚡"
        />
        <KpiCard
          label="Total Revenue (GMV)"
          value={formatBrl(kpis.total_gmv)}
          subtitle="Total gross spend"
          icon="💰"
        />
        <KpiCard
          label="Avg Customer Value"
          value={formatBrl(kpis.avg_customer_value)}
          subtitle="Lifetime spend / cust"
          icon="💎"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Average Order Value"
          value={formatBrl(kpis.avg_order_value)}
          subtitle="Per-order benchmark"
          icon="🛒"
        />
        <KpiCard
          label="Average 12M CLV"
          value={formatBrl(kpis.avg_clv)}
          subtitle="Forward value proxy"
          icon="📈"
        />
        <KpiCard
          label="Repeat Customer Rate"
          value={formatPct(kpis.repeat_customer_rate)}
          subtitle={`${formatNum(kpis.repeat_customers_count)} multi-order buyers`}
          icon="🔄"
        />
        <KpiCard
          label="At-Risk Customers"
          value={formatNum(kpis.at_risk_customers_count)}
          delta={formatBrl(kpis.at_risk_revenue_exposure)}
          deltaDirection="negative"
          subtitle="Revenue exposed to churn"
          icon="⚠️"
        />
      </div>

      {/* Dynamic Key Insights Grid */}
      <div>
        <SectionHeader
          title="Dynamic Key Insights & Commercial Signals"
          subtitle="100% Calculated on-the-fly from verified database features"
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((ins, idx) => (
            <InsightCard key={idx} {...ins} />
          ))}
        </div>
      </div>

      {/* Customer Health & Audience Composition */}
      <div>
        <SectionHeader
          title="Customer Health & Audience Composition Overview"
          subtitle="Portfolio Viability & Segment Breakdown"
        />
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7">
            <PieChartComponent
              title="Customer Audience Segment Composition"
              data={audience_composition?.pie || []}
              dataKey="count"
              nameKey="name"
              height={300}
            />
          </div>

          <div className="lg:col-span-5 flex flex-col justify-center gap-3">
            {audience_composition?.cohorts && (
              <>
                <div className="bg-white border border-slate-200 border-l-4 border-l-emerald-600 rounded-lg p-3.5 shadow-2xs">
                  <div className="flex justify-between items-center text-xs font-bold">
                    <span className="text-slate-900">Healthy & Loyal Base</span>
                    <span className="text-emerald-700 font-extrabold">
                      {formatPct(audience_composition.cohorts.healthy.share)} ({formatNum(audience_composition.cohorts.healthy.count)} profiles)
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Champions, Loyal & Potential Loyalists • {formatBrl(audience_composition.cohorts.healthy.revenue)} GMV
                  </p>
                </div>

                <div className="bg-white border border-slate-200 border-l-4 border-l-sky-600 rounded-lg p-3.5 shadow-2xs">
                  <div className="flex justify-between items-center text-xs font-bold">
                    <span className="text-slate-900">Regular Core Buyers</span>
                    <span className="text-sky-700 font-extrabold">
                      {formatPct(audience_composition.cohorts.regular.share)} ({formatNum(audience_composition.cohorts.regular.count)} profiles)
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Baseline active accounts • {formatBrl(audience_composition.cohorts.regular.revenue)} GMV
                  </p>
                </div>

                <div className="bg-white border border-slate-200 border-l-4 border-l-amber-500 rounded-lg p-3.5 shadow-2xs">
                  <div className="flex justify-between items-center text-xs font-bold">
                    <span className="text-slate-900">At-Risk Cohort</span>
                    <span className="text-amber-700 font-extrabold">
                      {formatPct(audience_composition.cohorts.at_risk.share)} ({formatNum(audience_composition.cohorts.at_risk.count)} profiles)
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Previously active repeat buyers lapsing • {formatBrl(audience_composition.cohorts.at_risk.revenue)} GMV
                  </p>
                </div>

                <div className="bg-white border border-slate-200 border-l-4 border-l-rose-600 rounded-lg p-3.5 shadow-2xs">
                  <div className="flex justify-between items-center text-xs font-bold">
                    <span className="text-slate-900">Lost Inactive Accounts</span>
                    <span className="text-rose-700 font-extrabold">
                      {formatPct(audience_composition.cohorts.lost.share)} ({formatNum(audience_composition.cohorts.lost.count)} profiles)
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Extended inactivity (>365d) • {formatBrl(audience_composition.cohorts.lost.revenue)} GMV
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Monthly Order Trajectory */}
      {monthly_trajectory && monthly_trajectory.length > 0 && (
        <div>
          <SectionHeader
            title="Macro Revenue Velocity & Order Trajectory"
            subtitle="Historical Monthly GMV & Completed Order Volume"
          />
          <LineChartComponent
            title="Monthly Merchandise GMV (BRL) and Completed Order Volume"
            data={monthly_trajectory}
            xKey="month"
            barKey="revenue"
            lineKey="orders"
            height={320}
          />
        </div>
      )}

      {/* Segment & Geographic Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarChartComponent
          title="Merchandise GMV Contribution by RFM Segment"
          data={segment_revenue || []}
          xKey="segment"
          yKey="revenue"
          horizontal={true}
          isCurrency={true}
          useMultiColor={true}
          height={300}
        />
        <BarChartComponent
          title="Top 10 Brazilian States by Merchandise GMV"
          data={state_revenue || []}
          xKey="state"
          yKey="revenue"
          horizontal={true}
          isCurrency={true}
          color="#0284C7"
          height={300}
        />
      </div>
    </div>
  );
}
