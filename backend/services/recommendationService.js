const dataService = require('./dataService');

const RECOMMENDATION_RULES = [
  {
    action_type: 'VIP Retention Outreach',
    priority: 'Urgent',
    badge_color: '#DC2626',
    target_audience: 'Champions & High CLV with Churn Risk >= 65%',
    channel: 'Dedicated Account Manager / VIP Concierge',
    description: 'Immediate white-glove contact, custom retention incentives, and logistics friction resolution.',
    rationale: 'High lifetime value is exposed to imminent churn; proactive white-glove outreach provides highest ROI.',
  },
  {
    action_type: 'Win-back Campaign',
    priority: 'High',
    badge_color: '#EA580C',
    target_audience: 'At Risk / Lost Customers with Recency > 180 days',
    channel: 'Automated Personalized Email + Exclusive Re-activation Discount',
    description: 'Multi-touch automated email re-engagement sequence offering personalized discount in previous affinity category.',
    rationale: 'Lapsed customers require economic incentives and updated catalog exposure to re-enter the purchasing cycle.',
  },
  {
    action_type: 'Loyalty Reward & Advocacy',
    priority: 'High',
    badge_color: '#16A34A',
    target_audience: 'Champions & Loyal Customers with CSAT >= 4.5 and Churn Risk < 35%',
    channel: 'Loyalty Program Tier Upgrade / Early Product Drops',
    description: 'Surprise-and-delight rewards, tier upgrade badges, and invitations to beta programs or review advocacy.',
    rationale: 'Deepens brand affinity, safeguards against competitive poaching, and drives organic word-of-mouth advocacy.',
  },
  {
    action_type: 'Second-Purchase Cross-Sell',
    priority: 'High',
    badge_color: '#8B5CF6',
    target_audience: 'Potential Loyalists (1 completed order, Recency <= 90 days)',
    channel: 'Personalized Category Recommendation Workflow',
    description: 'Curated cross-sell bundle recommendations based on market basket co-occurrence within 14-30 days of first order.',
    rationale: 'Converting a 1-time buyer into a repeat customer increases expected 12-month CLV by over 2.5x.',
  },
  {
    action_type: 'Service Recovery & Feedback',
    priority: 'Urgent',
    badge_color: '#E11D48',
    target_audience: 'Customers with CSAT Review <= 2.0 stars',
    channel: 'Customer Success Ticket & Quality Apology Voucher',
    description: 'Direct contact from support team to investigate fulfillment friction and offer store credit resolution.',
    rationale: 'Resolving customer complaints effectively can recover up to 70% of dissatisfied accounts.',
  },
  {
    action_type: 'Category Upsell & Basket Expansion',
    priority: 'Medium',
    badge_color: '#0284C7',
    target_audience: 'Regular Customers with AOV below category average',
    channel: 'In-app Promos / Free Shipping Threshold Boosts',
    description: "Tiered volume discounts (e.g. 'Add R$30 for Free Shipping') and complementary product bundles.",
    rationale: 'Drives immediate incremental order value without degrading gross margin.',
  },
  {
    action_type: 'Standard Lifecycle Nurture',
    priority: 'Standard',
    badge_color: '#64748B',
    target_audience: 'Healthy baseline customers with low churn risk and moderate spend',
    channel: 'Standard Weekly Newsletter & New Arrivals Digest',
    description: 'Regular communication cadence highlighting trending new catalog arrivals in preferred categories.',
    rationale: 'Maintains brand top-of-mind recall at low marginal distribution cost.',
  },
];

const generateCustomerRecommendation = (profile) => {
  const churnProb = parseFloat(profile.churn_probability || 0.5);
  const spend = parseFloat(profile.total_spend || 0.0);
  const clv = parseFloat(profile.predicted_clv || 0.0);
  const orders = parseInt(profile.total_orders || 1, 10);
  const recency = parseInt(profile.recency_days || 0, 10);
  const csat = parseFloat(profile.avg_review_score || 5.0);
  const segment = profile.rfm_segment || 'Regular Customers';

  let rule = RECOMMENDATION_RULES[6];
  let reason = 'Stable baseline customer with normal purchase interval.';

  // Priority 1: Service Recovery
  if (csat <= 2.0 && orders >= 1) {
    rule = RECOMMENDATION_RULES[4];
    reason = `Low CSAT rating (${csat.toFixed(1)}/5.0 stars). High friction risk requiring customer success outreach.`;
  }
  // Priority 2: VIP Retention
  else if (churnProb >= 0.65 && (spend >= 250 || clv >= 300 || ['Champions', 'Loyal Customers'].includes(segment))) {
    rule = RECOMMENDATION_RULES[0];
    reason = `High Churn Risk (${(churnProb * 100).toFixed(1)}%) on High-Value Account (R$ ${spend.toFixed(2)} GMV, 12M CLV: R$ ${clv.toFixed(2)}).`;
  }
  // Priority 3: Win-back
  else if ((churnProb >= 0.65 || recency > 180) && ['At Risk', 'Lost Customers', 'Regular Customers'].includes(segment)) {
    rule = RECOMMENDATION_RULES[1];
    reason = `Extended inactivity (${recency} days). Requires economic win-back trigger.`;
  }
  // Priority 4: Loyalty Reward
  else if (['Champions', 'Loyal Customers'].includes(segment) && churnProb < 0.35) {
    rule = RECOMMENDATION_RULES[2];
    reason = `Loyal Customer (${orders} orders, R$ ${spend.toFixed(2)}) with high health and low churn risk (${(churnProb * 100).toFixed(1)}%).`;
  }
  // Priority 5: Second-Purchase Cross-Sell
  else if (orders === 1 && recency <= 90) {
    rule = RECOMMENDATION_RULES[3];
    reason = `Recent first purchase (${recency} days ago). Prime window to trigger repeat purchase nurturing.`;
  }
  // Priority 6: Upsell
  else if (orders >= 1 && spend >= 100) {
    rule = RECOMMENDATION_RULES[5];
    reason = `Active customer with baseline spend (R$ ${spend.toFixed(2)}). Opportunity for basket size expansion.`;
  }

  return {
    customer_id: String(profile.customer_id),
    action_type: rule.action_type,
    priority: rule.priority,
    badge_color: rule.badge_color,
    channel: rule.channel,
    reason,
    description: rule.description,
    rfm_segment: segment,
    total_spend: spend,
    total_orders: orders,
    avg_order_value: parseFloat(profile.avg_order_value || (spend / Math.max(1, orders)).toFixed(2)),
    clv_band: profile.clv_band || 'Bronze',
    predicted_clv: clv,
    churn_probability: churnProb,
    recency_days: recency,
    avg_review_score: csat,
    favorite_category: profile.favorite_category || 'General',
    city: profile.city || '',
    state: profile.state || '',
  };
};

const computeRecommendationPortfolio = (customers, limit = 2500) => {
  const sample = customers.slice(0, limit);
  return sample.map(generateCustomerRecommendation);
};

const computeRecommendationSummary = (portfolio) => {
  const map = {};
  portfolio.forEach((r) => {
    const key = r.action_type;
    if (!map[key]) {
      map[key] = {
        action_type: r.action_type,
        priority: r.priority,
        badge_color: r.badge_color,
        customer_count: 0,
        total_gmv: 0,
        clv_sum: 0,
        churn_sum: 0,
      };
    }
    map[key].customer_count++;
    map[key].total_gmv += r.total_spend;
    map[key].clv_sum += r.predicted_clv;
    map[key].churn_sum += r.churn_probability;
  });

  return Object.values(map)
    .map((m) => ({
      action_type: m.action_type,
      priority: m.priority,
      badge_color: m.badge_color,
      customer_count: m.customer_count,
      total_gmv: parseFloat(m.total_gmv.toFixed(2)),
      avg_clv: parseFloat((m.clv_sum / m.customer_count).toFixed(2)),
      avg_churn_risk: parseFloat((m.churn_sum / m.customer_count).toFixed(4)),
    }))
    .sort((a, b) => b.customer_count - a.customer_count);
};

module.exports = {
  RECOMMENDATION_RULES,
  generateCustomerRecommendation,
  computeRecommendationPortfolio,
  computeRecommendationSummary,
};
