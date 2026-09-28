import { getCustomers } from '../services/dataStore.js';
import { computeExecutiveKPIs } from '../services/analyticsService.js';

const SEGMENT_PLAYBOOKS = {
  Champions: {
    title: 'Champions Retention & VIP Advocacy',
    priority: 'Highest Commercial Priority (P0)',
    badgeColor: '#16A34A',
    summary: 'Your most valuable and engaged customers with recent high-value purchases.',
    actions: [
      'Reward loyalty with early access to new product catalog drops.',
      'Offer exclusive VIP perks, dedicated concierge support, and milestone rewards.',
      'Cross-sell premium complementary categories with personalized bundles.',
    ],
  },
  'Loyal Customers': {
    title: 'Loyal Customer Value Maximization',
    priority: 'High Commercial Priority (P1)',
    badgeColor: '#0284C7',
    summary: 'Dependable repeat purchasers who form the core revenue backbone.',
    actions: [
      'Implement tiered loyalty rewards to incentivize progression to Champion status.',
      'Recommend higher-value variants and seasonal merchandise.',
      'Engage with feedback requests and Voice of Customer surveys.',
    ],
  },
  'Potential Loyalists': {
    title: 'Potential Loyalist Conversion & Nurturing',
    priority: 'Growth Opportunity (P2)',
    badgeColor: '#8B5CF6',
    summary: 'Recent buyers with solid initial spend who need encouragement to build a repeat habit.',
    actions: [
      'Trigger automated post-purchase second-order onboarding workflows.',
      'Provide targeted category recommendations based on initial purchase.',
      'Offer time-limited free shipping or bundle savings on their next order.',
    ],
  },
  'Regular Customers': {
    title: 'Regular Customer Engagement & Activation',
    priority: 'Standard Baseline (P3)',
    badgeColor: '#4F46E5',
    summary: 'Moderate frequency and spending customers who maintain steady baseline demand.',
    actions: [
      'Personalize marketing touchpoints according to favorite product category.',
      'Deploy seasonal promotional campaigns to increase purchase velocity.',
      'Promote high-rated cross-sell categories with positive review social proof.',
    ],
  },
  'At Risk': {
    title: 'At-Risk Customer Win-Back Campaign',
    priority: 'Urgent Attention Required (P1)',
    badgeColor: '#F59E0B',
    summary: 'Valuable customers whose purchase frequency has dropped and recency has extended.',
    actions: [
      'Launch personalized win-back re-engagement email sequence with incentives.',
      'Audit logistics satisfaction and resolve recurring fulfillment bottlenecks.',
      'Re-engage with dynamic new arrivals in previously purchased categories.',
    ],
  },
  'Lost Customers': {
    title: 'Lost Customer Diagnostics & Revival',
    priority: 'Low Touch / Selective Reactivation (P4)',
    badgeColor: '#DC2626',
    summary: 'Longest inactive customers with low recent engagement.',
    actions: [
      'Run low-cost automated revival campaigns during major seasonal clearance events.',
      'Collect exit feedback to diagnose root causes of customer churn.',
      'Filter unengaged contacts to optimize marketing campaign deliverability.',
    ],
  },
};

export function getSegmentsOverview(req, res) {
  try {
    const customers = getCustomers();
    const { segmentDistribution } = computeExecutiveKPIs(customers);

    // Sample scatter data (recency vs frequency vs monetary) for visual plotting
    const scatterSample = customers
      .slice(0, 800)
      .map(c => ({
        customer_id: c.customer_id,
        recency: Number(c.recency_days) || 0,
        frequency: Number(c.total_orders) || 1,
        monetary: Number(c.total_spend) || 0,
        segment: c.rfm_segment || 'Regular Customers',
        churn_prob: Number(c.churn_probability) || 0,
        clv: Number(c.predicted_clv) || 0,
      }));

    return res.status(200).json({
      success: true,
      data: {
        segments: segmentDistribution,
        playbooks: SEGMENT_PLAYBOOKS,
        scatterSample,
      },
    });
  } catch (error) {
    console.error('Error in getSegmentsOverview:', error);
    return res.status(500).json({ success: false, message: error.message });
  }
}

export function compareSegments(req, res) {
  try {
    const { segmentA = 'Champions', segmentB = 'At Risk' } = req.query;
    const customers = getCustomers();

    const subA = customers.filter(c => c.rfm_segment === segmentA);
    const subB = customers.filter(c => c.rfm_segment === segmentB);

    const totalBase = customers.length;
    const totalGmv = customers.reduce((a, c) => a + (Number(c.total_spend) || 0), 0);

    const calcMetrics = (sub) => {
      const count = sub.length;
      if (count === 0) return { count: 0, share: 0, revenue: 0, revShare: 0, avgClv: 0, avgOrders: 0, avgRecency: 0, avgAov: 0, churnRate: 0, avgCsat: 0 };
      const revenue = sub.reduce((a, c) => a + (Number(c.total_spend) || 0), 0);
      const avgClv = sub.reduce((a, c) => a + (Number(c.predicted_clv) || 0), 0) / count;
      const avgOrders = sub.reduce((a, c) => a + (Number(c.total_orders) || 1), 0) / count;
      const avgRecency = sub.reduce((a, c) => a + (Number(c.recency_days) || 0), 0) / count;
      const avgAov = sub.reduce((a, c) => a + (Number(c.avg_order_value) || 0), 0) / count;
      const churnRate = sub.reduce((a, c) => a + (Number(c.churn_probability) || 0), 0) / count;
      const avgCsat = sub.reduce((a, c) => a + (Number(c.avg_review_score) || 5), 0) / count;

      return {
        count,
        share: Math.round((count / totalBase) * 1000) / 10,
        revenue: Math.round(revenue),
        revShare: Math.round((revenue / Math.max(1, totalGmv)) * 1000) / 10,
        avgClv: Math.round(avgClv * 100) / 100,
        avgOrders: Math.round(avgOrders * 100) / 100,
        avgRecency: Math.round(avgRecency),
        avgAov: Math.round(avgAov * 100) / 100,
        churnRate: Math.round(churnRate * 1000) / 10,
        avgCsat: Math.round(avgCsat * 100) / 100,
      };
    };

    const metricsA = calcMetrics(subA);
    const metricsB = calcMetrics(subB);

    return res.status(200).json({
      success: true,
      data: {
        segmentA: { name: segmentA, ...metricsA, playbook: SEGMENT_PLAYBOOKS[segmentA] },
        segmentB: { name: segmentB, ...metricsB, playbook: SEGMENT_PLAYBOOKS[segmentB] },
      },
    });
  } catch (error) {
    return res.status(500).json({ success: false, message: error.message });
  }
}
