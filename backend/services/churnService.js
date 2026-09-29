const dataService = require('./dataService');

const computeRiskOverview = (customers) => {
  const total = customers.length;
  if (total === 0) {
    return {
      total_customers: 0,
      at_risk_count: 0,
      at_risk_pct: 0,
      at_risk_revenue: 0,
      at_risk_rev_pct: 0,
      high_val_at_risk_count: 0,
      high_val_at_risk_rev: 0,
      avg_churn_prob: 0,
    };
  }

  let totalSpend = 0;
  let atRiskCount = 0;
  let atRiskRev = 0;
  let churnSum = 0;

  customers.forEach((c) => {
    totalSpend += c.total_spend;
    churnSum += c.churn_probability;
    if (c.churn_probability >= 0.65) {
      atRiskCount++;
      atRiskRev += c.total_spend;
    }
  });

  const sortedSpend = [...customers].map((c) => c.total_spend).sort((a, b) => a - b);
  const p75Index = Math.floor(sortedSpend.length * 0.75);
  const p75Spend = sortedSpend[p75Index] || 200;

  let hvAtRiskCount = 0;
  let hvAtRiskRev = 0;
  customers.forEach((c) => {
    if (c.churn_probability >= 0.65 && c.total_spend >= p75Spend) {
      hvAtRiskCount++;
      hvAtRiskRev += c.total_spend;
    }
  });

  return {
    total_customers: total,
    at_risk_count: atRiskCount,
    at_risk_pct: atRiskCount / total,
    at_risk_revenue: parseFloat(atRiskRev.toFixed(2)),
    at_risk_rev_pct: atRiskRev / Math.max(1, totalSpend),
    high_val_at_risk_count: hvAtRiskCount,
    high_val_at_risk_rev: parseFloat(hvAtRiskRev.toFixed(2)),
    avg_churn_prob: parseFloat((churnSum / total).toFixed(4)),
  };
};

const computeQuadrantMatrix = (customers) => {
  const total = customers.length;
  if (total === 0) return {};

  const sortedClv = [...customers].map((c) => c.predicted_clv).sort((a, b) => a - b);
  const medianClv = sortedClv[Math.floor(sortedClv.length / 2)] || 0;
  const churnThreshold = 0.5;

  let qProtectCount = 0, qProtectRev = 0;
  let qNurtureCount = 0, qNurtureRev = 0;
  let qReengageCount = 0, qReengageRev = 0;
  let qMonitorCount = 0, qMonitorRev = 0;

  customers.forEach((c) => {
    const isHighRisk = c.churn_probability >= churnThreshold;
    const isHighVal = c.predicted_clv >= medianClv;

    if (isHighVal && isHighRisk) {
      qProtectCount++;
      qProtectRev += c.total_spend;
    } else if (isHighVal && !isHighRisk) {
      qNurtureCount++;
      qNurtureRev += c.total_spend;
    } else if (!isHighVal && isHighRisk) {
      qReengageCount++;
      qReengageRev += c.total_spend;
    } else {
      qMonitorCount++;
      qMonitorRev += c.total_spend;
    }
  });

  return {
    median_clv: medianClv,
    churn_threshold: churnThreshold,
    quadrants: {
      'Priority Protect (High Value, High Risk)': {
        count: qProtectCount,
        share: qProtectCount / total,
        revenue: parseFloat(qProtectRev.toFixed(2)),
        action: 'Immediate high-touch outreach, custom retention offer, logistics friction audit.',
        badge_color: '#DC2626',
      },
      'Advocate & Nurture (High Value, Low Risk)': {
        count: qNurtureCount,
        share: qNurtureCount / total,
        revenue: parseFloat(qNurtureRev.toFixed(2)),
        action: 'VIP appreciation rewards, exclusive product previews, premium cross-sell.',
        badge_color: '#16A34A',
      },
      'Automated Re-Engage (Low Value, High Risk)': {
        count: qReengageCount,
        share: qReengageCount / total,
        revenue: parseFloat(qReengageRev.toFixed(2)),
        action: 'Automated email win-back campaign with seasonal discount promotion.',
        badge_color: '#F59E0B',
      },
      'Standard Monitor (Low Value, Low Risk)': {
        count: qMonitorCount,
        share: qMonitorCount / total,
        revenue: parseFloat(qMonitorRev.toFixed(2)),
        action: 'Standard lifecycle nurture workflows and product discovery recommendations.',
        badge_color: '#0284C7',
      },
    },
  };
};

const getPrioritizedRetentionQueue = (customers, limit = 200) => {
  return [...customers]
    .sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0))
    .slice(0, limit);
};

const simulateChurn = (inputs) => {
  const { recency_days = 90, frequency = 2, monetary = 280, avg_order_value = 140, number_of_products = 2, customer_age_days = 45 } = inputs;

  // Calibrated logistic risk function aligning with XGBoost Churn Classifier
  // Key drivers: recency_days (+), frequency (-), monetary (-), customer_age_days (-)
  const logit =
    -1.2 +
    recency_days * 0.0095 -
    frequency * 0.45 -
    (monetary / 500.0) * 0.35 +
    (avg_order_value > 200 ? -0.2 : 0.1) -
    (customer_age_days / 365.0) * 0.3;

  const prob = 1.0 / (1.0 + Math.exp(-logit));
  const churnProb = parseFloat(Math.min(0.99, Math.max(0.01, prob)).toFixed(4));

  let band = 'Low Risk';
  let badgeColor = '#16A34A';
  let action = 'Encourage second purchase journey with streamlined discovery and first-repeat free shipping incentive.';

  if (churnProb >= 0.65) {
    band = 'High Risk';
    badgeColor = '#DC2626';
    action = 'Immediate VIP retention outreach. Audit fulfillment delay and deploy personalized win-back voucher.';
  } else if (churnProb >= 0.35) {
    band = 'Medium Risk';
    badgeColor = '#F59E0B';
    action = 'Target with tailored category re-engagement campaign highlighting top-rated new arrivals.';
  }

  return {
    churn_probability: churnProb,
    risk_classification: band,
    badge_color: badgeColor,
    action,
  };
};

module.exports = {
  computeRiskOverview,
  computeQuadrantMatrix,
  getPrioritizedRetentionQueue,
  simulateChurn,
};
