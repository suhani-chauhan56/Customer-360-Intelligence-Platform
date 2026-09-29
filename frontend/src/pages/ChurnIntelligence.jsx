import React, { useState, useEffect } from 'react';
import { getChurnOverview, simulateChurn } from '../services/api';
import { formatBrl, formatPct, formatNum } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import CustomerTable from '../components/common/CustomerTable';
import MethodologyPanel from '../components/common/MethodologyPanel';
import BarChartComponent from '../components/charts/BarChartComponent';
import { AlertTriangle, ShieldAlert, SlidersHorizontal, Activity } from 'lucide-react';

export default function ChurnIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulation Form State
  const [simForm, setSimForm] = useState({
    recency_days: 90,
    frequency: 2,
    monetary: 280,
    avg_order_value: 140,
    number_of_products: 2,
    customer_age_days: 45,
  });
  const [simResult, setSimResult] = useState(null);

  useEffect(() => {
    fetchChurnData();
    handleSimulate(simForm);
  }, []);

  const fetchChurnData = async () => {
    try {
      setLoading(true);
      const res = await getChurnOverview();
      if (res.data && res.data.success) {
        setData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching Churn overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulate = async (inputs) => {
    try {
      const res = await simulateChurn(inputs);
      if (res.data && res.data.success) {
        setSimResult(res.data.data);
      }
    } catch (err) {
      console.error('Error running Churn simulation:', err);
    }
  };

  if (loading || !data) {
    return <LoadingSpinner message="Quantifying churn risk & revenue exposure..." />;
  }

  const { risk_overview, quadrant_matrix, retention_queue, feature_importance } = data;

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Predictive & Risk AI
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">Customer Churn & Risk Intelligence</h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          At-risk revenue exposure, 4-quadrant value-risk matrix, XGBoost feature drivers, and prioritized retention queue.
        </p>
      </div>

      {/* Risk KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Total At-Risk Customers"
          value={formatNum(risk_overview.at_risk_count)}
          subtitle={`${formatPct(risk_overview.at_risk_pct)} of active base`}
          icon="⚠️"
        />
        <KpiCard
          label="At-Risk Revenue Exposure"
          value={formatBrl(risk_overview.at_risk_revenue)}
          subtitle={`${formatPct(risk_overview.at_risk_rev_pct)} of total GMV`}
          icon="💸"
        />
        <KpiCard
          label="High-Value At-Risk"
          value={formatNum(risk_overview.high_val_at_risk_count)}
          subtitle={formatBrl(risk_overview.high_val_at_risk_rev)}
          icon="🎯"
        />
        <KpiCard
          label="Average Churn Propensity"
          value={formatPct(risk_overview.avg_churn_prob)}
          subtitle="Calibrated risk score"
          icon="📉"
        />
      </div>

      {/* 4-Quadrant Prioritization Matrix */}
      <div>
        <SectionHeader
          title="High-Value + High-Risk Prioritization Matrix"
          subtitle="4-Quadrant Strategic Portfolio Framework"
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quadrant_matrix?.quadrants &&
            Object.entries(quadrant_matrix.quadrants).map(([qName, qInfo], idx) => (
              <div
                key={idx}
                className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col justify-between"
                style={{ borderTop: `4px solid ${qInfo.badge_color}` }}
              >
                <div>
                  <h4 className="text-xs font-bold text-slate-900 mb-1">{qName.split('(')[0]}</h4>
                  <div className="text-2xl font-extrabold mb-1" style={{ color: qInfo.badge_color }}>
                    {formatNum(qInfo.count)}
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mb-3">
                    {formatPct(qInfo.share)} of base ({formatBrl(qInfo.revenue)})
                  </div>
                </div>
                <div className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-100 font-medium">
                  {qInfo.action}
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Actionable Customer Retention Queue */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="Actionable Customer Retention Prioritization Queue"
          subtitle="Ranked by Commercial Risk Exposure: Priority = (Churn Prob) × (Normalized Predicted CLV) × 100"
        />
        <CustomerTable customers={retention_queue || []} pageSize={10} />
      </div>

      {/* Live Churn Propensity Simulator */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <SectionHeader
          title="Live Customer Churn What-If Simulator"
          subtitle="Real-Time Propensity Scoring & Automated Playbook Trigger"
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-6 bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <SlidersHorizontal className="w-4 h-4 text-indigo-600" />
              <span>Simulate Scenario Parameters</span>
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
                <label className="font-semibold text-slate-600 block mb-1">Total Orders (Frequency)</label>
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
                <label className="font-semibold text-slate-600 block mb-1">Total Spend (BRL)</label>
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

          <div className="lg:col-span-6 bg-rose-50/40 border border-rose-200 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-bold text-rose-900 uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-rose-600" />
              <span>Live Scenario Prediction Output</span>
            </h4>

            {simResult && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <KpiCard
                    label="Predicted Churn Risk"
                    value={formatPct(simResult.churn_probability)}
                    subtitle="Propensity score"
                  />
                  <KpiCard
                    label="Risk Classification"
                    value={simResult.risk_classification}
                    subtitle="Portfolio tier"
                  />
                </div>

                <div className="bg-white p-3.5 rounded-lg border border-rose-100 text-xs text-rose-950 flex items-start gap-2">
                  <span>🛠️</span>
                  <div>
                    <strong className="block font-bold mb-0.5">Automated Retention Playbook:</strong>
                    <span>{simResult.action}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Global Feature Importance Drivers */}
      {feature_importance && feature_importance.length > 0 && (
        <BarChartComponent
          title="Global Feature Drivers (XGBoost Churn Classifier)"
          data={feature_importance}
          xKey="feature"
          yKey="churn_importance"
          horizontal={true}
          color="#DC2626"
          height={260}
        />
      )}

      <MethodologyPanel domain="risk" />
    </div>
  );
}
