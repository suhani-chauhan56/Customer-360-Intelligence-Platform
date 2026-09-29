import React, { useState } from 'react';
import { BookOpen, Code2, ShieldAlert, Cpu, Heart, Award, Layers } from 'lucide-react';

export default function Methodology() {
  const [activeTab, setActiveTab] = useState('rfm');

  const tabs = [
    { id: 'rfm', label: '1. RFM Segmentation', icon: Layers },
    { id: 'clv', label: '2. Customer Lifetime Value', icon: Award },
    { id: 'churn', label: '3. Churn Intelligence', icon: ShieldAlert },
    { id: 'sentiment', label: '4. Sentiment & CSAT', icon: Heart },
    { id: 'recs', label: '5. Recommendation Engine', icon: Cpu },
    { id: 'health', label: '6. Health Score & Lifecycle', icon: Heart },
    { id: 'tech', label: '7. Tech Stack & Architecture', icon: Code2 },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Governance & Standards
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Methodology, Architecture & Enterprise Standards
        </h1>
        <p className="text-xs text-slate-600 leading-relaxed max-w-4xl mt-1">
          Comprehensive documentation of mathematical formulations, machine learning models, ETL pipelines, non-causal attribution policies, and engineering standards.
          Every metric displayed in CustomerAtlas is mathematically derived from verified database records with zero hardcoded assumptions or ungrounded generative hallucinations.
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="flex border-b border-slate-200 overflow-x-auto bg-slate-50/70">
          {tabs.map((tab) => {
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

        <div className="p-6 text-xs text-slate-700 leading-relaxed space-y-4">
          {activeTab === 'rfm' && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900">1. Recency, Frequency, Monetary (RFM) Methodology</h3>
              <p>
                <strong>Analytical Principles:</strong>
              </p>
              <ul className="list-disc pl-5 space-y-1 text-slate-600">
                <li><strong>Recency (R):</strong> Number of calendar days elapsed between the customer's most recent completed order and the snapshot anchor date. Quintile binned from 1 (longest inactive) to 5 (most recent).</li>
                <li><strong>Frequency (F):</strong> Total number of distinct completed transaction orders placed across the customer's lifespan.</li>
                <li><strong>Monetary (M):</strong> Total cumulative gross spend (in Brazilian Reais, BRL) across all completed orders.</li>
              </ul>
              <h4 className="font-bold text-slate-900 pt-2">Canonical Audience Segment Matrix:</h4>
              <ul className="list-disc pl-5 space-y-1 text-slate-600">
                <li><strong>Champions (R: 4-5, F: 4-5, M: 4-5):</strong> High-value, frequent, and recently active customers. VIP advocacy & early access perks.</li>
                <li><strong>Loyal Customers (F: 3-5, M: 3-5, R: 3-4):</strong> Consistent repeat purchasers forming the primary revenue backbone. Tiered loyalty rewards.</li>
                <li><strong>Potential Loyalists (R: 4-5, F: 1-2, M: 3-4):</strong> Recent buyers with healthy initial basket values. Second-purchase cross-sell nurturing.</li>
                <li><strong>Regular Customers (R: 2-4, F: 1-2, M: 2-3):</strong> Moderate spend baseline customers. Seasonal catalog promotions.</li>
                <li><strong>At Risk (R: 1-2, F: 2-5, M: 2-5):</strong> Previously active repeat buyers who have lapsed past 180 days. Win-back re-engagement incentives.</li>
                <li><strong>Lost Customers (R: 1, F: 1-2, M: 1-2):</strong> Longest inactive cohort (>365 days inactive) with lowest engagement.</li>
              </ul>
            </div>
          )}

          {activeTab === 'clv' && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900">2. Customer Lifetime Value (CLV) Methodology</h3>
              <p>
                <strong>Model Architecture & Target Formulation:</strong>
              </p>
              <ul className="list-disc pl-5 space-y-1 text-slate-600">
                <li><strong>Model Algorithm:</strong> Supervised Ridge / XGBoost Regressor trained on historical customer transaction trajectories.</li>
                <li><strong>Features Utilized:</strong> <code>recency_days</code>, <code>frequency</code>, <code>monetary</code>, <code>avg_order_value</code>, <code>number_of_products</code>, <code>customer_age_days</code>.</li>
                <li><strong>Target Definition:</strong> Forward 12-month expected cumulative merchandise gross revenue.</li>
              </ul>
              <h4 className="font-bold text-slate-900 pt-2">Dynamic Value Tiers:</h4>
              <ul className="list-disc pl-5 space-y-1 text-slate-600">
                <li><strong>Platinum VIP:</strong> &ge; 75th percentile of predicted CLV.</li>
                <li><strong>Gold Tier:</strong> 50th to 75th percentile.</li>
                <li><strong>Silver Tier:</strong> 25th to 50th percentile.</li>
                <li><strong>Bronze Tier:</strong> &lt; 25th percentile.</li>
              </ul>
            </div>
          )}

          {activeTab === 'churn' && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900">3. Customer Churn & Risk Intelligence</h3>
              <p>
                <strong>Methodology & Attribution Policy:</strong>
              </p>
              <ul className="list-disc pl-5 space-y-1 text-slate-600">
                <li><strong>Model Algorithm:</strong> Supervised Calibrated XGBoost Classifier outputting calibrated class probabilities [0.0, 1.0].</li>
                <li><strong>Definition:</strong> High risk corresponds to a calibrated probability &ge; 0.65 of persistent ongoing inactivity.</li>
                <li><strong>Feature Drivers:</strong> Inactivity duration (<code>recency_days</code>), order cadence deceleration, review rating signals, and digital footprint.</li>
                <li><strong>Causal Transparency Policy:</strong> Model feature importances reflect statistical predictive correlation rather than asserting direct causality.</li>
              </ul>
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 font-mono font-bold text-indigo-700">
                Priority Score = Churn Probability × (Predicted CLV / CLV_p99) × 100
              </div>
            </div>
          )}

          {activeTab === 'sentiment' && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900">4. Sentiment Intelligence & CSAT Scale</h3>
              <ul className="list-disc pl-5 space-y-1 text-slate-600">
                <li><strong>Positive Sentiment:</strong> Review Rating 4-5 Stars.</li>
                <li><strong>Neutral Sentiment:</strong> Review Rating 3 Stars.</li>
                <li><strong>Negative Sentiment:</strong> Review Rating 1-2 Stars.</li>
                <li><strong>Root-Cause Theme Extraction:</strong> Deterministic Portuguese keyword matching against customer comments across Logistics Delays, Product Quality, Catalog Inaccuracy, Missing Items, and Customer Support.</li>
              </ul>
            </div>
          )}

          {activeTab === 'recs' && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900">5. Multi-Signal Recommendation Engine</h3>
              <p>
                Synthesizes churn probability, RFM segment, predicted CLV, CSAT rating, and product affinity into deterministic Next-Best-Actions:
              </p>
              <ol className="list-decimal pl-5 space-y-1 text-slate-600">
                <li><strong>VIP Retention Outreach:</strong> Urgent outreach for Champions / High CLV accounts with churn risk &ge; 65%.</li>
                <li><strong>Win-back Campaign:</strong> Re-activation discounts for lapsed buyers inactive &gt; 180 days.</li>
                <li><strong>Loyalty Reward:</strong> Advocacy perks for high-health Champions and Loyal customers.</li>
                <li><strong>Second-Purchase Cross-Sell:</strong> Market basket co-occurrence recommendations within 90 days of first order.</li>
                <li><strong>Service Recovery:</strong> Immediate support ticket for customers rating &le; 2.0 stars.</li>
                <li><strong>Category Upsell:</strong> Basket expansion incentives for baseline spenders.</li>
              </ol>
            </div>
          )}

          {activeTab === 'health' && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900">6. Customer Health Score (0-100) & Lifecycle</h3>
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 font-mono font-bold text-indigo-700">
                Health Score = 0.25*R_norm + 0.25*F_norm + 0.25*M_norm + 0.15*Eng_norm + 0.10*CSAT_norm - 0.20*Risk_Penalty
              </div>
              <h4 className="font-bold text-slate-900 pt-2">6-Stage Lifecycle State Machine:</h4>
              <ul className="list-disc pl-5 space-y-1 text-slate-600">
                <li><strong>New:</strong> Tenure &le; 60 days and completed 1 order.</li>
                <li><strong>Activated:</strong> Completed 1 order with recency &le; 180 days.</li>
                <li><strong>Engaged:</strong> &ge; 2 orders with recency &le; 120 days.</li>
                <li><strong>Loyal:</strong> &ge; 3 orders or in Champions / Loyal segments.</li>
                <li><strong>At Risk:</strong> Recency &gt; 180 days or churn risk &ge; 65%.</li>
                <li><strong>Inactive / Lost:</strong> Recency &gt; 365 days and churn risk &ge; 65%.</li>
              </ul>
            </div>
          )}

          {activeTab === 'tech' && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-900">7. Modern MERN Tech Stack & Deployment Architecture</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                  <h4 className="font-bold text-slate-900 mb-2">Frontend Stack:</h4>
                  <ul className="space-y-1 text-slate-600">
                    <li>• React 18 with Vite build tooling</li>
                    <li>• Tailwind CSS for modern enterprise UI</li>
                    <li>• Recharts & Lucide Icons</li>
                    <li>• Axios REST Client with React Router v6</li>
                    <li>• Vercel Edge / Static CDN Hosting</li>
                  </ul>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                  <h4 className="font-bold text-slate-900 mb-2">Backend Stack:</h4>
                  <ul className="space-y-1 text-slate-600">
                    <li>• Node.js & Express REST API Engine</li>
                    <li>• MongoDB / Mongoose Data Schema & Indexing</li>
                    <li>• Zero Streamlit Presentation Dependency</li>
                    <li>• Safe In-Memory Caching with Dataset Lineage</li>
                    <li>• Vercel Serverless Function & Node Deployment</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
