import React, { useState, useEffect } from 'react';
import { getClvOverview, simulateClv } from '../services/api';
import { formatBrl, formatPct, formatNum } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import CustomerTable from '../components/common/CustomerTable';
import MethodologyPanel from '../components/common/MethodologyPanel';
import BarChartComponent from '../components/charts/BarChartComponent';
import { TrendingUp, Calculator, Sparkles } from 'lucide-react';

export default function CustomerValue() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulation Form State
  const [simForm, setSimForm] = useState({
    recency_days: 30,
    frequency: 3,
    monetary: 450,
    avg_order_value: 150,
    number_of_products: 3,
    customer_age_days: 90,
  });
  const [simResult, setSimResult] = useState(null);

  useEffect(() => {
    fetchClvData();
    handleSimulate(simForm);
  }, []);

  const fetchClvData = async () => {
    try {
      setLoading(true);
      const res = await getClvOverview();
      if (res.data && res.data.success) {
        setData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching CLV data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async (inputs) => {
    try {
      const res = await simulateClv(inputs);
      if (res.data && res.data.success) {
        setSimResult(res.data.data);
      }
    } catch (err) {
      console.error('Error running CLV simulation:', err);
    }
  };

  if (loading || !data) {
    return <LoadingSpinner message="Evaluating 12-Month Predictive CLV benchmarks..." />;
  }

  const { benchmarks, brackets, high_value_cohort } = data;

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Customer Intelligence
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Customer Value & Lifetime Value (CLV) Intelligence
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          12-month forward predictive CLV benchmarks, dynamic value banding, and high-value customer cohort analysis.
        </p>
      </div>

      {/* CLV Benchmarks KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Average 12M CLV"
          value={formatBrl(benchmarks.avg_clv)}
          subtitle={`Median: ${formatBrl(benchmarks.median_clv)}`}
          icon="📈"
        />
        <KpiCard
          label="Top 10% Customer CLV"
          value={formatBrl(benchmarks.top_10_pct_avg)}
          subtitle={`Threshold >= ${formatBrl(benchmarks.p90_clv)}`}
          icon="💎"
        />
        <KpiCard
          label="Forward 12M Pipeline"
          value={formatBrl(benchmarks.total_pipeline_clv)}
          subtitle="Total expected forward GMV"
          icon="💰"
        />
        <KpiCard
          label="Analyzed Profiles"
          value={formatNum(benchmarks.total_customers)}
          subtitle="Active customer population"
          icon="👥"
        />
      </div>

      {/* Dynamic Value Bands */}
      <div>
        <SectionHeader
          title="Dynamic Customer Lifetime Value Distribution"
          subtitle="Customer Count and Cumulative Spend across CLV Value Bands"
        />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BarChartComponent
            title="Customer Count by 12-Month CLV Band"
            data={brackets || []}
            xKey="clv_bracket"
            yKey="customers"
            useMultiColor={true}
            height={280}
          />
          <BarChartComponent
            title="Historical Spend Contribution by CLV Band"
            data={brackets || []}
            xKey="clv_bracket"
            yKey="total_historical_spend"
            isCurrency={true}
            color="#0284C7"
            height={280}
          />
        </div>
      </div>

      {/* High-Value Customer Cohort Analysis */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="High-Value Customer Cohort Analysis"
          subtitle="Top 10% Customer Decile by Predicted 12-Month Forward CLV"
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <KpiCard
            label="High-Value Cohort Size"
            value={`${formatNum(high_value_cohort.count)} Profiles`}
            subtitle={`${formatPct(high_value_cohort.pct_of_base)} of customer base`}
          />
          <KpiCard
            label="Historical GMV Share"
            value={formatPct(high_value_cohort.revenue_share)}
            subtitle={formatBrl(high_value_cohort.revenue_contribution)}
          />
          <KpiCard
            label="Average Cohort CLV"
            value={formatBrl(high_value_cohort.avg_clv)}
            subtitle={`Min Threshold: ${formatBrl(high_value_cohort.threshold)}`}
          />
          <KpiCard
            label="Average Order Count"
            value={`${high_value_cohort.avg_frequency.toFixed(2)} orders`}
            subtitle="Frequency"
          />
        </div>

        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider pt-2">
          Top High-Value Customer Records
        </h4>
        <CustomerTable customers={high_value_cohort.top_customers || []} pageSize={10} />
      </div>

      {/* 12-Month Forward CLV Scenario Estimator */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <SectionHeader
          title="Forward 12-Month CLV Scenario Estimator"
          subtitle="Machine Learning Scenario Simulation Engine"
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-6 bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <Calculator className="w-4 h-4 text-indigo-600" />
              <span>Simulate Customer Profile Inputs</span>
            </h4>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="font-semibold text-slate-600 block mb-1">Days Inactive (Recency)</label>
                <input
                  type="number"
                  min="0"
                  max="800"
                  value={simForm.recency_days}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 0;
                    const next = { ...simForm, recency_days: val };
                    setSimForm(next);
                    handleSimulate(next);
                  }}
                  className="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-600 block mb-1">Completed Orders (Frequency)</label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={simForm.frequency}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 1;
                    const next = { ...simForm, frequency: val };
                    setSimForm(next);
                    handleSimulate(next);
                  }}
                  className="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-600 block mb-1">Historical Spend (BRL)</label>
                <input
                  type="number"
                  min="5"
                  max="50000"
                  value={simForm.monetary}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 0;
                    const next = { ...simForm, monetary: val };
                    setSimForm(next);
                    handleSimulate(next);
                  }}
                  className="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-600 block mb-1">Average Order Value (BRL)</label>
                <input
                  type="number"
                  min="5"
                  max="25000"
                  value={simForm.avg_order_value}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 0;
                    const next = { ...simForm, avg_order_value: val };
                    setSimForm(next);
                    handleSimulate(next);
                  }}
                  className="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-600 block mb-1">Distinct Products</label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={simForm.number_of_products}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 1;
                    const next = { ...simForm, number_of_products: val };
                    setSimForm(next);
                    handleSimulate(next);
                  }}
                  className="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-600 block mb-1">Purchase Span (Days)</label>
                <input
                  type="number"
                  min="1"
                  max="800"
                  value={simForm.customer_age_days}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value) || 1;
                    const next = { ...simForm, customer_age_days: val };
                    setSimForm(next);
                    handleSimulate(next);
                  }}
                  className="w-full bg-white border border-slate-200 rounded-lg p-2 font-mono"
                />
              </div>
            </div>
          </div>

          <div className="lg:col-span-6 bg-indigo-50/40 border border-indigo-200 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span>12-Month Forward Value Forecast</span>
            </h4>

            {simResult && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <KpiCard
                    label="Predicted 12M CLV"
                    value={formatBrl(simResult.predicted_clv)}
                    subtitle="Forward value proxy"
                  />
                  <KpiCard
                    label="Customer Value Tier"
                    value={simResult.tier}
                    subtitle="Dynamic benchmark"
                  />
                </div>

                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-xs text-slate-700">
                  <span className="font-semibold text-slate-500 block text-[11px] mb-0.5">80% Planning Range:</span>
                  <span className="font-mono font-bold text-indigo-700">
                    {formatBrl(simResult.planning_range_low)} — {formatBrl(simResult.planning_range_high)}
                  </span>
                </div>

                <div className="bg-white p-3 rounded-lg border border-indigo-100 text-xs text-indigo-950 flex items-start gap-2">
                  <span>💡</span>
                  <div>
                    <strong className="block font-bold">Recommended Commercial Strategy:</strong>
                    <span>{simResult.strategy}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <MethodologyPanel domain="clv" />
    </div>
  );
}
