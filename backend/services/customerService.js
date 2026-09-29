const dataService = require('./dataService');

const computeCustomerHealth = (profile) => {
  const recencyDays = parseFloat(profile.recency_days || 300);
  const orders = parseInt(profile.total_orders || 1, 10);
  const spend = parseFloat(profile.total_spend || 0);
  const webScore = parseFloat(profile.web_engagement_score || 0);
  const csat = parseFloat(profile.avg_review_score || 5.0);
  const churnProb = parseFloat(profile.churn_probability || 0.5);

  // Recency Vital
  let recLabel, recStatus, recColor;
  if (recencyDays <= 60) {
    recLabel = 'High (Active)';
    recStatus = 'Recent order within 60 days';
    recColor = '#16A34A';
  } else if (recencyDays <= 180) {
    recLabel = 'Moderate';
    recStatus = `Last order ${Math.round(recencyDays)} days ago`;
    recColor = '#F59E0B';
  } else {
    recLabel = 'At Risk (Inactive)';
    recStatus = `Inactive for ${Math.round(recencyDays)} days`;
    recColor = '#DC2626';
  }

  // Frequency Vital
  let freqLabel, freqStatus, freqColor;
  if (orders >= 3) {
    freqLabel = 'Excellent';
    freqStatus = `${orders} completed orders (Repeat)`;
    freqColor = '#16A34A';
  } else if (orders === 2) {
    freqLabel = 'Strong';
    freqStatus = '2 completed orders (Repeat buyer)';
    freqColor = '#0284C7';
  } else {
    freqLabel = 'Standard';
    freqStatus = '1 single purchase completed';
    freqColor = '#64748B';
  }

  // Monetary Vital
  let monLabel, monStatus, monColor;
  if (spend >= 500) {
    monLabel = 'Top Tier';
    monStatus = `R$ ${spend.toFixed(2)} lifetime spend`;
    monColor = '#16A34A';
  } else if (spend >= 150) {
    monLabel = 'Healthy';
    monStatus = `R$ ${spend.toFixed(2)} lifetime spend`;
    monColor = '#0284C7';
  } else {
    monLabel = 'Modest';
    monStatus = `R$ ${spend.toFixed(2)} lifetime spend`;
    monColor = '#64748B';
  }

  // Engagement Vital
  let engLabel, engStatus, engColor;
  if (webScore >= 50) {
    engLabel = 'High';
    engStatus = `${webScore.toFixed(1)} digital engagement points`;
    engColor = '#16A34A';
  } else if (webScore >= 20) {
    engLabel = 'Moderate';
    engStatus = `${webScore.toFixed(1)} digital engagement points`;
    engColor = '#0284C7';
  } else {
    engLabel = 'Low / Passive';
    engStatus = `${webScore.toFixed(1)} digital engagement points`;
    engColor = '#94A3B8';
  }

  // CSAT Vital
  let sentLabel, sentStatus, sentColor;
  if (csat >= 4.5) {
    sentLabel = 'Positive (5/5)';
    sentStatus = `${csat.toFixed(1)} average review score`;
    sentColor = '#16A34A';
  } else if (csat >= 3.0) {
    sentLabel = 'Neutral (3-4/5)';
    sentStatus = `${csat.toFixed(1)} average review score`;
    sentColor = '#F59E0B';
  } else {
    sentLabel = 'Negative (<3/5)';
    sentStatus = `${csat.toFixed(1)} average review score`;
    sentColor = '#DC2626';
  }

  // Churn Vital
  let riskLabel, riskStatus, riskColor;
  if (churnProb < 0.35) {
    riskLabel = 'Low Risk';
    riskStatus = `${(churnProb * 100).toFixed(1)}% propensity`;
    riskColor = '#16A34A';
  } else if (churnProb < 0.65) {
    riskLabel = 'Medium Risk';
    riskStatus = `${(churnProb * 100).toFixed(1)}% propensity`;
    riskColor = '#F59E0B';
  } else {
    riskLabel = 'High Risk';
    riskStatus = `${(churnProb * 100).toFixed(1)}% propensity`;
    riskColor = '#DC2626';
  }

  // Overall Health Score Formula (0-100)
  const rNorm = Math.max(0.0, Math.min(100.0, 100.0 * (1.0 - recencyDays / 365.0)));
  const fNorm = Math.min(100.0, orders * 33.33);
  const mNorm = Math.min(100.0, (spend / 500.0) * 100.0);
  const engNorm = Math.min(100.0, (webScore / 60.0) * 100.0);
  const csatNorm = Math.min(100.0, (csat / 5.0) * 100.0);
  const riskPenalty = churnProb * 100.0;

  const rawScore =
    0.25 * rNorm +
    0.25 * fNorm +
    0.25 * mNorm +
    0.15 * engNorm +
    0.10 * csatNorm -
    0.20 * riskPenalty;

  const totalScore = parseFloat(Math.max(0.0, Math.min(100.0, rawScore)).toFixed(1));

  let tier = 'Critical 🔴';
  let tierColor = '#DC2626';
  if (totalScore >= 75.0) {
    tier = 'Thriving 🟢';
    tierColor = '#16A34A';
  } else if (totalScore >= 50.0) {
    tier = 'Healthy 🔵';
    tierColor = '#0284C7';
  } else if (totalScore >= 30.0) {
    tier = 'At Risk 🟡';
    tierColor = '#F59E0B';
  }

  return {
    total_score: totalScore,
    health_tier: tier,
    badge_color: tierColor,
    vitals: [
      { dimension: 'Purchase Recency', rating: recLabel, detail: recStatus, color: recColor, icon: '⏱️' },
      { dimension: 'Order Frequency', rating: freqLabel, detail: freqStatus, color: freqColor, icon: '📦' },
      { dimension: 'Monetary Value', rating: monLabel, detail: monStatus, color: monColor, icon: '💰' },
      { dimension: 'Digital Engagement', rating: engLabel, detail: engStatus, color: engColor, icon: '🌐' },
      { dimension: 'Feedback & CSAT', rating: sentLabel, detail: sentStatus, color: sentColor, icon: '⭐' },
      { dimension: 'Retention Health', rating: riskLabel, detail: riskStatus, color: riskColor, icon: '🎯' },
    ],
    components: {
      recency_vital: parseFloat(rNorm.toFixed(1)),
      frequency_vital: parseFloat(fNorm.toFixed(1)),
      monetary_vital: parseFloat(mNorm.toFixed(1)),
      engagement_vital: parseFloat(engNorm.toFixed(1)),
      csat_vital: parseFloat(csatNorm.toFixed(1)),
      risk_penalty: parseFloat(riskPenalty.toFixed(1)),
    },
    formula: 'Score = 0.25*R + 0.25*F + 0.25*M + 0.15*Eng + 0.10*CSAT - 0.20*Risk',
  };
};

const deriveLifecycleStages = (profile) => {
  const firstDate = profile.first_purchase_date
    ? new Date(profile.first_purchase_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : 'Recorded';
  const lastDate = profile.last_purchase_date
    ? new Date(profile.last_purchase_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    : 'Recorded';

  const orders = parseInt(profile.total_orders || 1, 10);
  const spend = parseFloat(profile.total_spend || 0);
  const segment = profile.rfm_segment || 'Regular Customers';
  const clvBand = profile.clv_band || 'Bronze';
  const ageDays = parseInt(profile.customer_age_days || 1, 10);
  const recency = parseInt(profile.recency_days || 0, 10);
  const churnProb = parseFloat(profile.churn_probability || 0);

  let currentState = 'Activated';
  if (recency > 365 && churnProb >= 0.65) {
    currentState = 'Inactive / Lost';
  } else if (recency > 180 || churnProb >= 0.65) {
    currentState = 'At Risk';
  } else if (orders >= 3 || segment === 'Champions' || segment === 'Loyal Customers') {
    currentState = 'Loyal';
  } else if (orders >= 2 && recency <= 120) {
    currentState = 'Engaged';
  } else if (ageDays <= 60 && orders === 1) {
    currentState = 'New';
  }

  return [
    {
      stage: 'First Purchase',
      reached: true,
      date: firstDate,
      description: `Initial order recorded (${profile.favorite_category || 'General'})`,
    },
    {
      stage: 'Repeat Purchase',
      reached: orders > 1,
      date: orders > 1 ? lastDate : 'Not yet reached',
      description: orders > 1 ? `${orders} total orders completed` : 'Single transaction customer',
    },
    {
      stage: 'Loyal Customer Status',
      reached: ['Champions', 'Loyal Customers'].includes(segment) || orders >= 3,
      date: ['Champions', 'Loyal Customers'].includes(segment) || orders >= 3 ? 'Active' : 'Not yet reached',
      description: `RFM Segment: ${segment}`,
    },
    {
      stage: 'High-Value Tier',
      reached: spend >= 300 || ['Platinum', 'Gold'].includes(clvBand),
      date: `Tier: ${clvBand}`,
      description: `Lifetime Spend: R$ ${spend.toFixed(2)}`,
    },
    {
      stage: 'Current Lifecycle Segment',
      reached: true,
      date: `Status: ${currentState}`,
      description: `Cluster: ${profile.cluster_segment || 'Standard'}`,
    },
  ];
};

const diagnoseCustomerRiskFactors = (profile) => {
  const recencyDays = parseFloat(profile.recency_days || 0);
  const orders = parseInt(profile.total_orders || 1, 10);
  const csat = parseFloat(profile.avg_review_score || 5.0);
  const spend = parseFloat(profile.total_spend || 0);
  const webScore = parseFloat(profile.web_engagement_score || 0);
  const churnProb = parseFloat(profile.churn_probability || 0);

  const riskFactors = [];
  const protectiveFactors = [];

  if (recencyDays > 365) {
    riskFactors.push(`Extended inactivity: ${Math.round(recencyDays)} days since last purchase (>1 year)`);
  } else if (recencyDays > 180) {
    riskFactors.push(`Lapsed purchase recency: ${Math.round(recencyDays)} days inactive (>6 months)`);
  } else {
    protectiveFactors.push(`Recent purchase activity: ${Math.round(recencyDays)} days ago`);
  }

  if (orders === 1) {
    riskFactors.push('Single-purchase customer (no repeat order history established)');
  } else {
    protectiveFactors.push(`Repeat purchase history established (${orders} completed orders)`);
  }

  if (csat <= 2.0) {
    riskFactors.push(`Low satisfaction signal: Average rating of ${csat.toFixed(1)} / 5.0 stars`);
  } else if (csat >= 4.0) {
    protectiveFactors.push(`Positive customer feedback: Average rating of ${csat.toFixed(1)} / 5.0 stars`);
  }

  if (webScore < 10) {
    riskFactors.push('Low recent digital touchpoint engagement');
  } else if (webScore >= 40) {
    protectiveFactors.push('Active digital web browsing session footprint');
  }

  const exposureNote =
    spend >= 400
      ? `High revenue at risk: R$ ${spend.toFixed(2)} lifetime merchandise spend`
      : `Standard value exposure: R$ ${spend.toFixed(2)} lifetime spend`;

  const riskLevel = churnProb >= 0.65 ? 'High Risk' : churnProb >= 0.35 ? 'Medium Risk' : 'Low Risk';

  return {
    risk_level: riskLevel,
    churn_probability: churnProb,
    risk_factors: riskFactors,
    protective_factors: protectiveFactors,
    exposure_note: exposureNote,
  };
};

const explainRfmSegment = (profile) => {
  const segment = profile.rfm_segment || 'Regular Customers';
  const rScore = profile.r_score || 1;
  const fScore = profile.f_score || 1;
  const mScore = profile.m_score || 1;
  const recency = Math.round(profile.recency_days || 0);
  const orders = profile.total_orders || 1;
  const spend = (profile.total_spend || 0).toFixed(2);

  const factors = [
    `Recency Score ${rScore}/5 (Purchased ${recency} days ago)`,
    `Frequency Score ${fScore}/5 (${orders} completed order${orders > 1 ? 's' : ''})`,
    `Monetary Score ${mScore}/5 (R$ ${spend} total lifetime spend)`,
  ];

  const descriptions = {
    Champions: 'Top-tier customers with recent purchases, frequent orders, and highest monetary spending.',
    'Loyal Customers': 'Consistent repeat buyers with high lifetime spend and dependable purchase intervals.',
    'Potential Loyalists': 'Recent purchasers with good initial spend who show high potential for repeat conversion.',
    'Regular Customers': 'Standard baseline customers with average recency, order frequency, and transaction sizes.',
    'At Risk': 'Previously active customers who have not made a purchase recently and require re-engagement.',
    'Lost Customers': 'Longest inactive customers with lowest recency scores who have likely churned.',
  };

  return {
    segment,
    rfm_code: `R:${rScore} | F:${fScore} | M:${mScore}`,
    explanation: descriptions[segment] || 'Customer classified based on quintile RFM matrix scoring.',
    factors,
  };
};

module.exports = {
  computeCustomerHealth,
  deriveLifecycleStages,
  diagnoseCustomerRiskFactors,
  explainRfmSegment,
};
