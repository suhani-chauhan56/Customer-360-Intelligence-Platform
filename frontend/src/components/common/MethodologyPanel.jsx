import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

export default function MethodologyPanel({ domain = 'rfm' }) {
  const [isOpen, setIsOpen] = useState(false);

  const content = {
    rfm: {
      title: 'RFM Scoring & Segmentation Methodology',
      details: [
        'Recency (R): Calendar days between customer last order and snapshot anchor date, binned into quintiles (1-5).',
        'Frequency (F): Total completed orders across customer lifetime, quintile ranked.',
        'Monetary (M): Total cumulative gross merchandise spend (BRL), quintile ranked.',
        'Segment Assignments: Champions (R:4-5, F:4-5, M:4-5), Loyal Customers (F:3-5, M:3-5, R:3-4), Potential Loyalists (R:4-5, F:1-2, M:3-4), Regular Customers (R:2-4, F:1-2, M:2-3), At Risk (R:1-2, F:2-5, M:2-5), Lost Customers (R:1, F:1-2, M:1-2).',
      ],
    },
    clv: {
      title: '12-Month Predictive CLV Formulation & Tiers',
      details: [
        'Model Architecture: Supervised Ridge / XGBoost Regressor trained on longitudinal transaction trajectories.',
        'Features: recency_days, frequency, monetary, avg_order_value, number_of_products, customer_age_days.',
        'Target: Expected forward 12-month gross revenue proxy.',
        'Value Bands: Platinum (>= 75th percentile), Gold (50th - 75th percentile), Silver (25th - 50th percentile), Bronze (< 25th percentile).',
      ],
    },
    risk: {
      title: 'XGBoost Churn Propensity & Non-Causal Attribution',
      details: [
        'Model Architecture: Supervised Calibrated XGBoost Classifier producing calibrated inactivity probabilities [0.0, 1.0].',
        'High Risk Threshold: Calibrated probability >= 0.65 of persistent inactivity.',
        'Priority Formula: Priority Score = Churn Probability * (Predicted CLV / CLV_p99) * 100.',
        'Attribution Policy: Model feature weights reflect statistical correlation, not guaranteed causal guarantees.',
      ],
    },
  };

  const active = content[domain] || content.rfm;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm mt-6 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left font-bold text-xs text-slate-700 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-indigo-600" />
          <span>Governance & Mathematical Methodology: {active.title}</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>

      {isOpen && (
        <div className="px-5 pb-5 pt-1 text-xs text-slate-600 border-t border-slate-100 bg-slate-50/50 space-y-2">
          {active.details.map((d, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-indigo-500 font-bold">•</span>
              <span>{d}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
