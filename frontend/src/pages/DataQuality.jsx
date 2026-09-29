import React, { useState, useEffect } from 'react';
import { getDataQuality } from '../services/api';
import { formatPct, formatNum } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Badge from '../components/common/Badge';
import { ShieldCheck, CheckCircle2, GitBranch, Activity, Cpu, FileText } from 'lucide-react';

export default function DataQuality() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('integrity');

  useEffect(() => {
    fetchQualityData();
  }, []);

  const fetchQualityData = async () => {
    try {
      setLoading(true);
      const res = await getDataQuality();
      if (res.data && res.data.success) {
        setData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching data quality:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <LoadingSpinner message="Auditing schema contracts & model registries..." />;
  }

  const {
    quality_kpis,
    integrity_checks = [],
    field_completeness = [],
    data_lineage = [],
    drift_monitoring,
    model_registry = [],
    compliance_audit_logs = [],
  } = data;

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Exploration & Governance
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Data Quality, Integrity & MLOps Governance
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Automated data completeness audits, raw vs processed data lineage, PSI feature drift monitoring, and compliance logs.
        </p>
      </div>

      {/* Top Quality KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Data Quality Score"
          value={`${quality_kpis.data_quality_score}%`}
          delta="100% Target"
          deltaDirection={quality_kpis.is_healthy ? 'positive' : 'negative'}
          subtitle="Schema & range integrity"
          icon="🛡️"
        />
        <KpiCard
          label="Canonical Profiles"
          value={formatNum(quality_kpis.canonical_profiles)}
          subtitle="Validated entity records"
          icon="👥"
        />
        <KpiCard
          label="Validated Attributes"
          value={`${quality_kpis.total_attributes} Features`}
          subtitle="Feature store schema"
          icon="📊"
        />
        <KpiCard
          label="ML Models Ready"
          value={quality_kpis.models_ready}
          subtitle="XGBoost, CLV, Sentiment, K-Means"
          icon="🤖"
        />
      </div>

      {/* Governance Tabs */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="flex border-b border-slate-200 overflow-x-auto bg-slate-50/70">
          {[
            { id: 'integrity', label: 'Schema & Quality Integrity', icon: CheckCircle2 },
            { id: 'lineage', label: 'Data Lineage & ETL Pipeline', icon: GitBranch },
            { id: 'drift', label: 'PSI Feature Drift Monitoring', icon: Activity },
            { id: 'models', label: 'ML Model Artifact Registry', icon: Cpu },
            { id: 'audit', label: 'Compliance Audit Event Log', icon: FileText },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-700 bg-white'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="p-6">
          {activeTab === 'integrity' && (
            <div className="space-y-6">
              <div>
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
                  Automated Data Integrity Test Suite
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                        <th className="py-2.5 px-3">Test Name</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3">Observed Detail</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium">
                      {integrity_checks.map((chk, idx) => (
                        <tr key={idx} className="hover:bg-slate-50">
                          <td className="py-2.5 px-3 font-bold text-slate-900">{chk.Test}</td>
                          <td className="py-2.5 px-3 font-bold">{chk.Status}</td>
                          <td className="py-2.5 px-3 text-slate-600">{chk.Detail}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
                  Field-by-Field Completeness & Null Distribution
                </h4>
                <div className="overflow-x-auto max-h-80 overflow-y-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 sticky top-0">
                        <th className="py-2.5 px-3">Attribute Field</th>
                        <th className="py-2.5 px-3">Type</th>
                        <th className="py-2.5 px-3 text-right">Non-Null Records</th>
                        <th className="py-2.5 px-3 text-right">Completeness %</th>
                        <th className="py-2.5 px-3 text-right">Null Count</th>
                        <th className="py-2.5 px-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium">
                      {field_completeness.map((f, idx) => (
                        <tr key={idx} className="hover:bg-slate-50">
                          <td className="py-2 px-3 font-mono text-indigo-700 font-semibold">{f['Attribute Field']}</td>
                          <td className="py-2 px-3 text-slate-500">{f['Data Type']}</td>
                          <td className="py-2 px-3 text-right">{f['Non-Null Records']}</td>
                          <td className="py-2 px-3 text-right font-bold text-slate-900">{f['Completeness %']}</td>
                          <td className="py-2 px-3 text-right text-slate-500">{f['Missing / Null Count']}</td>
                          <td className="py-2 px-3">{f.Status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'lineage' && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                Data Lineage & Transformation Summary (Raw Ingestion → Feature Store)
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                      <th className="py-2.5 px-3">ETL Stage</th>
                      <th className="py-2.5 px-3">Dataset Source</th>
                      <th className="py-2.5 px-3">Volume</th>
                      <th className="py-2.5 px-3">Engineering Transformation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {data_lineage.map((l, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-bold text-slate-900">{l.Stage}</td>
                        <td className="py-2.5 px-3 font-mono text-indigo-600 font-semibold">{l['Source File']}</td>
                        <td className="py-2.5 px-3 font-bold text-slate-700">{l['Raw Volume'] || l['Processed Volume']}</td>
                        <td className="py-2.5 px-3 text-slate-600">{l.Processing}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'drift' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Longitudinal Population Stability Index (PSI) Feature Drift
                  </h4>
                  <p className="text-[11.5px] text-slate-500 font-medium mt-0.5">
                    Baseline (&gt;180d inactive cohort) vs Target (&le;180d active cohort)
                  </p>
                </div>
                <Badge color={drift_monitoring.drift_detected ? 'amber' : 'green'}>
                  {drift_monitoring.overall_status}
                </Badge>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                      <th className="py-2.5 px-3">Feature Attribute</th>
                      <th className="py-2.5 px-3 text-right">PSI Score</th>
                      <th className="py-2.5 px-3">Drift Status</th>
                      <th className="py-2.5 px-3">Alert Tier</th>
                      <th className="py-2.5 px-3 text-right">Baseline Mean</th>
                      <th className="py-2.5 px-3 text-right">Current Mean</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {drift_monitoring.features.map((f, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{f.Feature}</td>
                        <td className="py-2.5 px-3 text-right font-mono font-bold text-indigo-700">{f['PSI Score']}</td>
                        <td className="py-2.5 px-3">{f.Status}</td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10.5px] font-bold ${
                              f['Alert Tier'] === 'Normal'
                                ? 'bg-emerald-50 text-emerald-700'
                                : f['Alert Tier'] === 'Monitor'
                                ? 'bg-amber-50 text-amber-700'
                                : 'bg-rose-50 text-rose-700'
                            }`}
                          >
                            {f['Alert Tier']}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right">{f['Baseline Mean']}</td>
                        <td className="py-2.5 px-3 text-right font-semibold text-slate-900">{f['Current Mean']}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="text-[11.5px] text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100">
                <strong>MLOps Governance Rule: </strong>{drift_monitoring.governance_policy}
              </div>
            </div>
          )}

          {activeTab === 'models' && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                Registered Machine Learning Inference Models
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                      <th className="py-2.5 px-3">Model Name</th>
                      <th className="py-2.5 px-3">Artifact File</th>
                      <th className="py-2.5 px-3">Version</th>
                      <th className="py-2.5 px-3">Algorithm</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Size (KB)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium">
                    {model_registry.map((m, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-bold text-slate-900">{m['Model Name']}</td>
                        <td className="py-2.5 px-3 font-mono text-indigo-600 font-semibold">{m.Artifact}</td>
                        <td className="py-2.5 px-3">{m.Version}</td>
                        <td className="py-2.5 px-3 text-slate-700">{m.Algorithm}</td>
                        <td className="py-2.5 px-3 font-bold text-emerald-700">{m.Status}</td>
                        <td className="py-2.5 px-3 text-right font-mono">{m['File Size (KB)']}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'audit' && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
                Real-Time Enterprise Compliance Event Stream
              </h4>
              {compliance_audit_logs.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                        <th className="py-2.5 px-3">Timestamp</th>
                        <th className="py-2.5 px-3">Action</th>
                        <th className="py-2.5 px-3">Resource Type</th>
                        <th className="py-2.5 px-3">User ID</th>
                        <th className="py-2.5 px-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium">
                      {compliance_audit_logs.map((log, idx) => (
                        <tr key={idx} className="hover:bg-slate-50">
                          <td className="py-2 px-3 font-mono text-slate-500">{log.timestamp}</td>
                          <td className="py-2 px-3 font-bold text-slate-900">{log.action}</td>
                          <td className="py-2 px-3 text-indigo-700 font-semibold">{log.resource_type}</td>
                          <td className="py-2 px-3 font-mono text-slate-600">{log.user_id}</td>
                          <td className="py-2 px-3 font-bold text-emerald-700">{log.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">No audit events recorded in active session.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
