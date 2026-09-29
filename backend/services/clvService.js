const computeClvOverview = (customers) => {
  const total = customers.length;
  if (total === 0) {
    return {
      avg_clv: 0,
      median_clv: 0,
      p90_clv: 0,
      p95_clv: 0,
      total_pipeline_clv: 0,
      top_10_pct_avg: 0,
      total_customers: 0,
    };
  }

  const sortedClv = [...customers].map((c) => c.predicted_clv).sort((a, b) => a - b);
  const totalClv = sortedClv.reduce((sum, val) => sum + val, 0);

  const medianIndex = Math.floor(sortedClv.length / 2);
  const medianClv = sortedClv.length % 2 !== 0 ? sortedClv[medianIndex] : (sortedClv[medianIndex - 1] + sortedClv[medianIndex]) / 2;

  const p90Index = Math.floor(sortedClv.length * 0.90);
  const p95Index = Math.floor(sortedClv.length * 0.95);
  const p90Clv = sortedClv[p90Index] || 0;
  const p95Clv = sortedClv[p95Index] || 0;

  const top10 = sortedClv.slice(p90Index);
  const top10Avg = top10.length > 0 ? top10.reduce((s, v) => s + v, 0) / top10.length : 0;

  return {
    avg_clv: parseFloat((totalClv / total).toFixed(2)),
    median_clv: parseFloat(medianClv.toFixed(2)),
    p90_clv: parseFloat(p90Clv.toFixed(2)),
    p95_clv: parseFloat(p95Clv.toFixed(2)),
    total_pipeline_clv: parseFloat(totalClv.toFixed(2)),
    top_10_pct_avg: parseFloat(top10Avg.toFixed(2)),
    total_customers: total,
  };
};

const computeClvBins = (customers) => {
  const totalCustomers = customers.length;
  if (totalCustomers === 0) return [];

  let totalSpend = 0;
  const bins = [
    { label: '< R$100', min: -Infinity, max: 100, customers: 0, total_spend: 0, total_clv: 0, churn_sum: 0 },
    { label: 'R$100 – R$250', min: 100, max: 250, customers: 0, total_spend: 0, total_clv: 0, churn_sum: 0 },
    { label: 'R$250 – R$500', min: 250, max: 500, customers: 0, total_spend: 0, total_clv: 0, churn_sum: 0 },
    { label: 'R$500 – R$1,000', min: 500, max: 1000, customers: 0, total_spend: 0, total_clv: 0, churn_sum: 0 },
    { label: '> R$1,000', min: 1000, max: Infinity, customers: 0, total_spend: 0, total_clv: 0, churn_sum: 0 },
  ];

  customers.forEach((c) => {
    totalSpend += c.total_spend;
    const clv = c.predicted_clv || 0;
    const matchedBin = bins.find((b) => clv >= b.min && clv < b.max);
    if (matchedBin) {
      matchedBin.customers++;
      matchedBin.total_spend += c.total_spend;
      matchedBin.total_clv += clv;
      matchedBin.churn_sum += c.churn_probability;
    }
  });

  return bins.map((b) => ({
    clv_bracket: b.label,
    customers: b.customers,
    total_historical_spend: parseFloat(b.total_spend.toFixed(2)),
    total_predicted_clv: parseFloat(b.total_clv.toFixed(2)),
    avg_churn_prob: b.customers > 0 ? parseFloat((b.churn_sum / b.customers).toFixed(4)) : 0,
    customer_pct: parseFloat((b.customers / totalCustomers).toFixed(4)),
    revenue_pct: parseFloat((b.total_spend / Math.max(1, totalSpend)).toFixed(4)),
  }));
};

const analyzeHighValueCohort = (customers, percentile = 0.90) => {
  const total = customers.length;
  if (total === 0) {
    return {
      threshold: 0,
      cohort_customers: [],
      count: 0,
      pct_of_base: 0,
      revenue_contribution: 0,
      revenue_share: 0,
      avg_clv: 0,
      avg_frequency: 0,
      avg_recency: 0,
      risk_distribution: {},
    };
  }

  const sortedClv = [...customers].map((c) => c.predicted_clv).sort((a, b) => a - b);
  const pIndex = Math.floor(sortedClv.length * percentile);
  const threshold = sortedClv[pIndex] || 0;

  const highVal = customers.filter((c) => c.predicted_clv >= threshold);
  let totalSpend = 0;
  customers.forEach((c) => (totalSpend += c.total_spend));

  let hSpend = 0, hClv = 0, hFreq = 0, hRec = 0;
  let lowRisk = 0, medRisk = 0, highRisk = 0;

  highVal.forEach((c) => {
    hSpend += c.total_spend;
    hClv += c.predicted_clv;
    hFreq += c.total_orders;
    hRec += c.recency_days;

    if (c.churn_probability < 0.35) lowRisk++;
    else if (c.churn_probability < 0.65) medRisk++;
    else highRisk++;
  });

  const count = highVal.length;

  return {
    threshold: parseFloat(threshold.toFixed(2)),
    count,
    pct_of_base: count / total,
    revenue_contribution: parseFloat(hSpend.toFixed(2)),
    revenue_share: hSpend / Math.max(1, totalSpend),
    avg_clv: count > 0 ? parseFloat((hClv / count).toFixed(2)) : 0,
    avg_frequency: count > 0 ? parseFloat((hFreq / count).toFixed(2)) : 0,
    avg_recency: count > 0 ? Math.round(hRec / count) : 0,
    risk_distribution: {
      'Low Risk (<35%)': lowRisk,
      'Medium Risk (35-65%)': medRisk,
      'High Risk (>=65%)': highRisk,
    },
    top_customers: [...highVal].sort((a, b) => b.predicted_clv - a.predicted_clv).slice(0, 100),
  };
};

const simulateClv = (inputs) => {
  const { recency_days = 30, frequency = 3, monetary = 450, avg_order_value = 150, number_of_products = 3, customer_age_days = 90 } = inputs;

  // ML-aligned linear expectation model based on trained Ridge regression weights:
  // Target: Expected forward 12M spend ~ f(monetary, AOV, frequency, recency, products, age)
  const baseIntercept = 45.0;
  const estimatedClv = Math.max(
    0.0,
    baseIntercept +
      monetary * 0.72 +
      avg_order_value * 0.28 +
      frequency * 18.5 +
      number_of_products * 6.2 -
      recency_days * 0.15 +
      customer_age_days * 0.05
  );

  const roundedClv = parseFloat(estimatedClv.toFixed(2));
  const intLow = parseFloat((roundedClv * 0.85).toFixed(2));
  const intHigh = parseFloat((roundedClv * 1.15).toFixed(2));

  let tier = 'Bronze Tier';
  if (roundedClv >= 500) tier = 'Platinum VIP';
  else if (roundedClv >= 250) tier = 'Gold Tier';
  else if (roundedClv >= 100) tier = 'Silver Tier';

  return {
    predicted_clv: roundedClv,
    tier,
    planning_range_low: intLow,
    planning_range_high: intHigh,
    strategy:
      tier.includes('Platinum') || tier.includes('Gold')
        ? 'Prioritize premium VIP loyalty recognition, dedicated concierge support, and early access cross-sell.'
        : 'Target with category cross-sell discounts to build repeat order frequency.',
  };
};

module.exports = {
  computeClvOverview,
  computeClvBins,
  analyzeHighValueCohort,
  simulateClv,
};
