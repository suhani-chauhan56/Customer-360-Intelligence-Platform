import React, { useState, useEffect } from 'react';
import { getRfmOverview, getSegmentDetails, compareSegments, buildCohort } from '../services/api';
import { formatBrl, formatPct, formatNum } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import CustomerTable from '../components/common/CustomerTable';
import MethodologyPanel from '../components/common/MethodologyPanel';
import PieChartComponent from '../components/charts/PieChartComponent';
import BarChartComponent from '../components/charts/BarChartComponent';
import { Users, Download, Sliders, ArrowRight } from 'lucide-react';

export default function CustomerSegmentation() {
  const [rfmData, setRfmData] = useState(null);
  const [selectedSeg, setSelectedSeg] = useState('Champions');
  const [segDetails, setSegDetails] = useState(null);

  // Comparison State
  const [segA, setSegA] = useState('Champions');
  const [segB, setSegB] = useState('Loyal Customers');
  const [comparisonData, setComparisonData] = useState([]);

  // Cohort Builder State
  const [cohortParams, setCohortParams] = useState({
    segments: ['Champions', 'Loyal Customers'],
    min_spend: 100,
    max_churn: 0.7,
  });
  const [cohortResult, setCohortResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
  }, []);

  useEffect(() => {
    if (selectedSeg) fetchSegmentDetails(selectedSeg);
  }, [selectedSeg]);

  useEffect(() => {
    fetchComparison();
  }, [segA, segB]);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const res = await getRfmOverview();
      if (res.data && res.data.success) {
        setRfmData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching RFM overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSegmentDetails = async (seg) => {
    try {
      const res = await getSegmentDetails(seg);
      if (res.data && res.data.success) {
        setSegDetails(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching segment details:', err);
    }
  };

  const fetchComparison = async () => {
    try {
      const res = await compareSegments(segA, segB);
      if (res.data && res.data.success) {
        setComparisonData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching comparison:', err);
    }
  };

  const handleRunCohort = async () => {
    try {
      const res = await buildCohort(cohortParams);
      if (res.data && res.data.success) {
        setCohortResult(res.data.data);
      }
    } catch (err) {
      console.error('Error building cohort:', err);
    }
  };

  if (loading || !rfmData) {
    return <LoadingSpinner message="Calculating RFM segment matrices & playbooks..." />;
  }

  const distribution = rfmData.distribution || [];
  const allSegments = distribution.map((d) => d.rfm_segment);

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Customer Intelligence
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">Customer Segmentation & RFM Intelligence</h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          RFM segment distribution, granular audience drill-down, side-by-side comparison, and targeted cohort builder.
        </p>
      </div>

      {/* Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PieChartComponent
          title="Customer Base Share by RFM Segment"
          data={distribution.map((d) => ({ name: d.rfm_segment, count: d.customers }))}
          height={300}
        />
        <BarChartComponent
          title="Merchandise GMV Contribution by Segment"
          data={distribution}
          xKey="rfm_segment"
          yKey="total_revenue"
          horizontal={true}
          isCurrency={true}
          useMultiColor={true}
          height={300}
        />
      </div>

      {/* Benchmark Matrix Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <SectionHeader
          title="RFM Segment Performance Benchmark Matrix"
          subtitle="Portfolio Economic & Behavioral Metrics"
        />
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <th className="py-2.5 px-3">Segment</th>
                <th className="py-2.5 px-3 text-right">Customers</th>
                <th className="py-2.5 px-3 text-right">% of Base</th>
                <th className="py-2.5 px-3 text-right">Total GMV</th>
                <th className="py-2.5 px-3 text-right">% of GMV</th>
                <th className="py-2.5 px-3 text-right">Avg Spend</th>
                <th className="py-2.5 px-3 text-right">Avg 12M CLV</th>
                <th className="py-2.5 px-3 text-right">Avg Orders</th>
                <th className="py-2.5 px-3 text-right">Avg Recency</th>
                <th className="py-2.5 px-3 text-right">Churn Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {distribution.map((d) => (
                <tr key={d.rfm_segment} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-slate-900">{d.rfm_segment}</td>
                  <td className="py-2.5 px-3 text-right">{formatNum(d.customers)}</td>
                  <td className="py-2.5 px-3 text-right">{formatPct(d.customer_share)}</td>
                  <td className="py-2.5 px-3 text-right font-bold text-slate-900">{formatBrl(d.total_revenue)}</td>
                  <td className="py-2.5 px-3 text-right font-semibold text-indigo-700">{formatPct(d.revenue_share)}</td>
                  <td className="py-2.5 px-3 text-right">{formatBrl(d.avg_spend)}</td>
                  <td className="py-2.5 px-3 text-right text-indigo-600 font-semibold">{formatBrl(d.avg_clv)}</td>
                  <td className="py-2.5 px-3 text-right">{d.avg_orders}</td>
                  <td className="py-2.5 px-3 text-right">{d.avg_recency}d</td>
                  <td className="py-2.5 px-3 text-right font-bold text-rose-600">{formatPct(d.avg_churn_prob)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Segment Drill-Down & Playbook */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="Granular Segment Drill-Down & Strategic Action Playbook"
          subtitle="Deep Dive & Tactical Guidance"
          action={
            <select
              value={selectedSeg}
              onChange={(e) => setSelectedSeg(e.target.value)}
              className="text-xs font-bold bg-slate-50 border border-slate-200 rounded-lg p-2 text-indigo-700 focus:outline-none"
            >
              {allSegments.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          }
        />

        {segDetails && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-5 bg-slate-50/70 border border-slate-200 rounded-xl p-5">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                  Strategic Action Playbook
                </div>
                <h3 className="text-base font-extrabold text-slate-900 mb-2">{segDetails.playbook.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">{segDetails.playbook.summary}</p>
                <div className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                  Recommended Tactical Actions:
                </div>
                <ul className="space-y-2 text-xs text-slate-700">
                  {segDetails.playbook.actions.map((act, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-indigo-600 font-bold">•</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="lg:col-span-7 grid grid-cols-2 sm:grid-cols-3 gap-3 content-center">
                <KpiCard
                  label="Segment Size"
                  value={formatNum(segDetails.metrics.size)}
                  subtitle={`${formatPct(segDetails.metrics.share_of_base)} of base`}
                />
                <KpiCard
                  label="Total GMV"
                  value={formatBrl(segDetails.metrics.total_gmv)}
                  subtitle="Gross merchandise spend"
                />
                <KpiCard
                  label="Avg 12M CLV"
                  value={formatBrl(segDetails.metrics.avg_clv)}
                  subtitle="Forward value proxy"
                />
                <KpiCard
                  label="Avg Order Count"
                  value={`${segDetails.metrics.avg_orders} orders`}
                  subtitle="Frequency"
                />
                <KpiCard
                  label="Avg Inactivity"
                  value={`${segDetails.metrics.avg_recency} days`}
                  subtitle="Recency interval"
                />
                <KpiCard
                  label="Churn Propensity"
                  value={formatPct(segDetails.metrics.avg_churn_prob)}
                  subtitle="Calibrated risk"
                />
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
                Top Customer Profiles in '{selectedSeg}' Segment
              </h4>
              <CustomerTable customers={segDetails.top_customers || []} pageSize={10} />
            </div>
          </>
        )}
      </div>

      {/* Segment Comparison Matrix */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="Segment Comparison Matrix"
          subtitle="Analytical Side-by-Side Evaluation"
          action={
            <div className="flex items-center gap-2">
              <select
                value={segA}
                onChange={(e) => setSegA(e.target.value)}
                className="text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1.5"
              >
                {allSegments.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
              <span className="text-xs font-bold text-slate-400">vs</span>
              <select
                value={segB}
                onChange={(e) => setSegB(e.target.value)}
                className="text-xs font-bold bg-slate-50 border border-slate-200 rounded p-1.5"
              >
                {allSegments.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          }
        />

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <th className="py-2.5 px-3">Analytical Metric</th>
                <th className="py-2.5 px-3 text-indigo-700 font-bold">Segment A ({segA})</th>
                <th className="py-2.5 px-3 text-sky-700 font-bold">Segment B ({segB})</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {comparisonData.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{row.metric}</td>
                  <td className="py-2.5 px-3 font-bold text-indigo-900">{row.val_a}</td>
                  <td className="py-2.5 px-3 font-bold text-sky-900">{row.val_b}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Custom Targeted Marketing Cohort Builder */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="Targeted Marketing Cohort Builder"
          subtitle="Campaign Activation with Export"
        />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
          <div>
            <label className="font-bold text-slate-700 block mb-1.5">Target RFM Segments</label>
            <div className="flex flex-wrap gap-1.5">
              {allSegments.map((seg) => {
                const isSelected = cohortParams.segments.includes(seg);
                return (
                  <button
                    key={seg}
                    onClick={() => {
                      setCohortParams((prev) => ({
                        ...prev,
                        segments: isSelected
                          ? prev.segments.filter((s) => s !== seg)
                          : [...prev.segments, seg],
                      }));
                    }}
                    className={`px-2 py-1 rounded text-[11px] font-semibold border transition-colors ${
                      isSelected
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {seg}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1.5">
              Min Lifetime Spend: <span className="font-mono text-indigo-600">R$ {cohortParams.min_spend}</span>
            </label>
            <input
              type="range"
              min="0"
              max="2000"
              step="50"
              value={cohortParams.min_spend}
              onChange={(e) => setCohortParams((p) => ({ ...p, min_spend: parseFloat(e.target.value) }))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1.5">
              Max Churn Risk: <span className="font-mono text-indigo-600">{(cohortParams.max_churn * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={cohortParams.max_churn}
              onChange={(e) => setCohortParams((p) => ({ ...p, max_churn: parseFloat(e.target.value) }))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
          </div>
        </div>

        <button
          onClick={handleRunCohort}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors flex items-center gap-2"
        >
          <Sliders className="w-4 h-4" />
          <span>Execute Cohort Filtering</span>
        </button>

        {cohortResult && (
          <div className="pt-3 border-t border-slate-100 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <KpiCard
                label="Matching Audience"
                value={`${formatNum(cohortResult.matching_count)} Customers`}
                subtitle="Audience reach"
              />
              <KpiCard
                label="Total Cohort GMV"
                value={formatBrl(cohortResult.total_gmv)}
                subtitle="Gross spending"
              />
              <KpiCard
                label="Average Cohort CLV"
                value={formatBrl(cohortResult.avg_clv)}
                subtitle="Forward value"
              />
            </div>
            <CustomerTable customers={cohortResult.cohort || []} pageSize={10} />
          </div>
        )}
      </div>

      <MethodologyPanel domain="rfm" />
    </div>
  );
}
