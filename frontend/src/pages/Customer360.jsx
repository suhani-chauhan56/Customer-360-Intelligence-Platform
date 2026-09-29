import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCustomers, getCustomerDetails, getCustomerDossier } from '../services/api';
import { formatBrl, formatPct, formatNum, formatDate } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import Badge from '../components/common/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import CustomerHealthGrid from '../components/customer/CustomerHealthGrid';
import LifecycleJourney from '../components/customer/LifecycleJourney';
import RiskDiagnostics from '../components/customer/RiskDiagnostics';
import CustomerTimeline from '../components/customer/CustomerTimeline';
import PieChartComponent from '../components/charts/PieChartComponent';
import GaugeChart from '../components/charts/GaugeChart';
import { Download, User, MapPin, Calendar, Award, Sparkles, ShoppingBag, CreditCard, Gift, Search } from 'lucide-react';

export default function Customer360() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [preset, setPreset] = useState('All Filtered Customers');
  const [customerOptions, setCustomerOptions] = useState([]);
  const [selectedCid, setSelectedCid] = useState(id || '');
  const [customerData, setCustomerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchOptions();
  }, [preset]);

  useEffect(() => {
    if (id) {
      setSelectedCid(id);
      fetchCustomer(id);
    } else if (customerOptions.length > 0) {
      const defaultId = customerOptions[0].customer_id;
      setSelectedCid(defaultId);
      fetchCustomer(defaultId);
    }
  }, [id, customerOptions]);

  const fetchOptions = async () => {
    try {
      const res = await getCustomers({ preset, limit: 100 });
      if (res.data && res.data.success) {
        setCustomerOptions(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching customer options:', err);
    }
  };

  const fetchCustomer = async (cid) => {
    try {
      setLoading(true);
      const res = await getCustomerDetails(cid);
      if (res.data && res.data.success) {
        setCustomerData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching customer dossier:', err);
      setCustomerData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCustomer = (cid) => {
    setSelectedCid(cid);
    navigate(`/customers/${cid}`);
  };

  const handleDownloadDossier = async () => {
    if (!selectedCid) return;
    try {
      const res = await getCustomerDossier(selectedCid);
      if (res.data && res.data.success) {
        const jsonStr = JSON.stringify(res.data.data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `customer_360_${selectedCid}.json`;
        a.click();
      }
    } catch (err) {
      console.error('Error downloading dossier:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Customer Lookup Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
              Customer Intelligence
            </div>
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">Customer 360 Unified Profile Dossier</h1>
            <p className="text-xs text-slate-500 font-medium mt-1">
              Complete customer dossier, 6-dimension vital health signs, verifiable lifecycle journey, and transaction ledger.
            </p>
          </div>
        </div>

        {/* Quick Search & Select Controls */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mt-4">
          <div className="md:col-span-4">
            <label className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-1.5">
              Lookup Filter Preset
            </label>
            <select
              value={preset}
              onChange={(e) => setPreset(e.target.value)}
              className="w-full text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-slate-700 focus:outline-none focus:border-indigo-500"
            >
              <option value="All Filtered Customers">All Filtered Customers</option>
              <option value="Champions & VIPs">Champions & VIPs</option>
              <option value="At Risk High Spenders">At Risk High Spenders</option>
              <option value="Recent Active Buyers">Recent Active Buyers</option>
              <option value="Multi-Order Repeat Buyers">Multi-Order Repeat Buyers</option>
            </select>
          </div>

          <div className="md:col-span-8">
            <label className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-1.5">
              Select or Search Customer ID
            </label>
            <select
              value={selectedCid}
              onChange={(e) => handleSelectCustomer(e.target.value)}
              className="w-full text-xs font-mono font-semibold bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-indigo-700 focus:outline-none focus:border-indigo-500"
            >
              {customerOptions.map((c) => (
                <option key={c.customer_id} value={c.customer_id}>
                  {c.customer_id} — {c.rfm_segment} | R$ {c.total_spend.toFixed(2)} | {c.city}, {c.state}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Assembling unified customer 360 profile dossier..." />
      ) : !customerData ? (
        <EmptyState
          title="Customer Profile Not Found"
          description={`No customer record found matching ID '${selectedCid}'. Try selecting another customer from the dropdown above.`}
          onReset={() => setPreset('All Filtered Customers')}
        />
      ) : (
        <>
          {/* Customer 360 Header Bar */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-xl shadow-sm shadow-indigo-200 shrink-0">
                  <User className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <h2 className="text-lg font-extrabold font-mono text-slate-900">{customerData.profile.customer_id}</h2>
                    <Badge color="indigo">{customerData.profile.rfm_segment}</Badge>
                    <span
                      className="text-xs font-bold px-2 py-0.5 rounded-full text-white"
                      style={{ backgroundColor: customerData.recommendation.badge_color }}
                    >
                      {customerData.recommendation.priority} Action
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 font-medium">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{customerData.profile.city}, {customerData.profile.state}</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>Member since {formatDate(customerData.profile.first_purchase_date)}</span>
                    </span>
                    <span className="flex items-center gap-1 font-bold text-indigo-600">
                      <Award className="w-3.5 h-3.5" />
                      <span>Tier: {customerData.profile.clv_band}</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleDownloadDossier}
                  className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center gap-1.5"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Dossier</span>
                </button>
              </div>
            </div>
          </div>

          {/* Customer Summary KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
            <KpiCard
              label="12M Forward CLV"
              value={formatBrl(customerData.profile.predicted_clv)}
              subtitle={`Tier: ${customerData.profile.clv_band}`}
              icon="💎"
            />
            <KpiCard
              label="Total Spend"
              value={formatBrl(customerData.profile.total_spend)}
              subtitle="Lifetime GMV"
              icon="💰"
            />
            <KpiCard
              label="Total Orders"
              value={formatNum(customerData.profile.total_orders)}
              subtitle="Completed orders"
              icon="📦"
            />
            <KpiCard
              label="Average Order"
              value={formatBrl(customerData.profile.avg_order_value)}
              subtitle="Per order"
              icon="🛒"
            />
            <KpiCard
              label="Recency"
              value={`${Math.round(customerData.profile.recency_days)} days`}
              subtitle="Days inactive"
              icon="⏱️"
            />
            <KpiCard
              label="Churn Propensity"
              value={formatPct(customerData.profile.churn_probability)}
              delta={customerData.risk_diagnostics.risk_level}
              deltaDirection={customerData.profile.churn_probability >= 0.65 ? 'negative' : 'positive'}
              subtitle="Calibrated risk"
              icon="🎯"
            />
          </div>

          {/* Customer Health Grid */}
          <CustomerHealthGrid health={customerData.health} />

          {/* Customer Lifecycle Progression */}
          <LifecycleJourney lifecycle={customerData.lifecycle} />

          {/* Deep Dossier Tabs */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="flex border-b border-slate-200 overflow-x-auto bg-slate-50/70">
              {[
                { id: 'overview', label: 'Profile & Segmentation Rationale', icon: User },
                { id: 'behavior', label: 'Touchpoint Engagement & Risk', icon: Sparkles },
                { id: 'orders', label: `Order History (${customerData.orders.length})`, icon: ShoppingBag },
                { id: 'payments', label: `Payment Methods (${customerData.payments.length})`, icon: CreditCard },
                { id: 'recs', label: 'AI Next-Best-Category Offers', icon: Gift },
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
              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  <div className="lg:col-span-7 space-y-4">
                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                      <div className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">
                        Segment Assignment Rationale
                      </div>
                      <div className="text-base font-extrabold text-slate-900 mt-1">
                        {customerData.rfm_explanation.segment} ({customerData.rfm_explanation.rfm_code})
                      </div>
                      <p className="text-xs text-slate-600 mt-1 mb-3">{customerData.rfm_explanation.explanation}</p>
                      <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        Contributing Data Factors:
                      </div>
                      <ul className="space-y-1 text-xs text-slate-800 font-medium">
                        {customerData.rfm_explanation.factors.map((f, i) => (
                          <li key={i} className="flex items-center gap-1.5">
                            <span className="text-indigo-500 font-bold">•</span>
                            <span>{f}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-white border border-slate-200 rounded-xl p-4">
                      <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
                        Canonical Profile Attributes
                      </h4>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="p-2 bg-slate-50 rounded">
                          <span className="text-slate-500 block text-[10px]">Primary Category:</span>
                          <span className="font-bold text-slate-800">{customerData.profile.favorite_category}</span>
                        </div>
                        <div className="p-2 bg-slate-50 rounded">
                          <span className="text-slate-500 block text-[10px]">Distinct Products:</span>
                          <span className="font-bold text-slate-800">{customerData.profile.number_of_products || 1}</span>
                        </div>
                        <div className="p-2 bg-slate-50 rounded">
                          <span className="text-slate-500 block text-[10px]">Average CSAT Rating:</span>
                          <span className="font-bold text-slate-800">{customerData.profile.avg_review_score.toFixed(1)} / 5.0</span>
                        </div>
                        <div className="p-2 bg-slate-50 rounded">
                          <span className="text-slate-500 block text-[10px]">Customer Tenure:</span>
                          <span className="font-bold text-slate-800">{Math.round(customerData.profile.customer_age_days)} days</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="lg:col-span-5">
                    <GaugeChart
                      value={customerData.profile.churn_probability}
                      label="Calibrated Churn Propensity"
                      actionInfo={customerData.recommendation}
                    />
                  </div>
                </div>
              )}

              {activeTab === 'behavior' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    <KpiCard
                      label="Digital Web Sessions"
                      value={formatNum(customerData.profile.sessions || 0)}
                      subtitle="Website visits"
                      icon="🌐"
                    />
                    <KpiCard
                      label="Product Page Views"
                      value={formatNum(customerData.profile.views || 0)}
                      subtitle="Catalog browsing"
                      icon="👁️"
                    />
                    <KpiCard
                      label="Cart Additions"
                      value={formatNum(customerData.profile.cart_additions || 0)}
                      subtitle="High-intent actions"
                      icon="🛒"
                    />
                    <KpiCard
                      label="Campaign Conversions"
                      value={formatNum(customerData.profile.campaign_conversions || 0)}
                      subtitle="Marketing response"
                      icon="🎯"
                    />
                  </div>
                  <RiskDiagnostics
                    riskDiagnostics={customerData.risk_diagnostics}
                    actionInfo={customerData.recommendation}
                  />
                </div>
              )}

              {activeTab === 'orders' && (
                <div>
                  <CustomerTimeline orders={customerData.orders} reviews={customerData.reviews} />
                  <div className="mt-4 overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                          <th className="py-2.5 px-3">Order ID</th>
                          <th className="py-2.5 px-3">Date</th>
                          <th className="py-2.5 px-3">Status</th>
                          <th className="py-2.5 px-3 text-right">Item Price</th>
                          <th className="py-2.5 px-3 text-right">Freight</th>
                          <th className="py-2.5 px-3 text-right">Gross Revenue</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-medium">
                        {customerData.orders.map((o) => (
                          <tr key={o.order_id}>
                            <td className="py-2 px-3 font-mono text-indigo-600 font-bold">{o.order_id}</td>
                            <td className="py-2 px-3">{formatDate(o.purchase_date)}</td>
                            <td className="py-2 px-3">
                              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-semibold">
                                {o.order_status}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-right">{formatBrl(o.item_price)}</td>
                            <td className="py-2 px-3 text-right">{formatBrl(o.freight_value)}</td>
                            <td className="py-2 px-3 text-right font-bold text-slate-900">{formatBrl(o.revenue)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeTab === 'payments' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
                      Payment Method & Installment Ledger
                    </h5>
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                          <th className="py-2.5 px-3">Payment Type</th>
                          <th className="py-2.5 px-3 text-center">Installments</th>
                          <th className="py-2.5 px-3 text-right">Amount</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-medium">
                        {customerData.payments.map((p, idx) => (
                          <tr key={idx}>
                            <td className="py-2 px-3 font-semibold capitalize text-slate-800">{p.payment_type.replace('_', ' ')}</td>
                            <td className="py-2 px-3 text-center">{p.payment_installments}x</td>
                            <td className="py-2 px-3 text-right font-bold">{formatBrl(p.payment_value)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div>
                    <PieChartComponent
                      title="Payment Value by Method"
                      data={customerData.payments.map((p) => ({
                        name: p.payment_type.replace('_', ' '),
                        count: p.payment_value,
                      }))}
                      dataKey="count"
                      nameKey="name"
                      height={220}
                    />
                  </div>
                </div>
              )}

              {activeTab === 'recs' && (
                <div>
                  <h5 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-4">
                    Explainable Next-Best-Category Cross-Sell Recommendations
                  </h5>
                  {customerData.category_recommendations.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      {customerData.category_recommendations.map((rec, idx) => (
                        <div
                          key={idx}
                          className="bg-indigo-50/40 border border-indigo-200 rounded-xl p-4 flex flex-col justify-between"
                        >
                          <div>
                            <div className="flex items-center justify-between text-xs font-bold mb-2">
                              <span className="text-indigo-700">Rank #{rec.rank || idx + 1}</span>
                              <Badge color="indigo">Basket Co-occurrence</Badge>
                            </div>
                            <h6 className="text-sm font-extrabold text-slate-900 capitalize mb-1">
                              {rec.recommended_category.replace(/_/g, ' ')}
                            </h6>
                            <p className="text-xs text-slate-600 mb-3">{rec.reason}</p>
                          </div>
                          <span className="text-[11px] font-semibold text-indigo-600 bg-white px-2.5 py-1 rounded border border-indigo-100 w-fit">
                            Method: {rec.method || 'Market Basket'}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No category recommendations available for this record.</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
