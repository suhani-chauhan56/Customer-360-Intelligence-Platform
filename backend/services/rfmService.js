const getSegmentPlaybook = (segmentName) => {
  const playbooks = {
    Champions: {
      title: 'Champions Retention & VIP Advocacy',
      priority: 'Highest Commercial Priority',
      badge_color: '#16A34A',
      summary: 'Your most valuable and engaged customers with recent high-value purchases.',
      actions: [
        'Reward loyalty with early access to new product catalog drops.',
        'Offer exclusive VIP perks, dedicated concierge support, and milestone rewards.',
        'Cross-sell premium complementary categories with personalized bundles.',
      ],
    },
    'Loyal Customers': {
      title: 'Loyal Customer Value Maximization',
      priority: 'High Commercial Priority',
      badge_color: '#0284C7',
      summary: 'Dependable repeat purchasers who form the core revenue backbone.',
      actions: [
        'Implement tiered loyalty rewards to incentivize progression to Champion status.',
        'Recommend higher-value variants and seasonal merchandise.',
        'Engage with feedback requests and Voice of Customer surveys.',
      ],
    },
    'Potential Loyalists': {
      title: 'Potential Loyalist Conversion & Nurturing',
      priority: 'Growth Opportunity',
      badge_color: '#8B5CF6',
      summary: 'Recent buyers with solid initial spend who need encouragement to build a repeat habit.',
      actions: [
        'Trigger automated post-purchase second-order onboarding workflows.',
        'Provide targeted category recommendations based on initial purchase.',
        'Offer time-limited free shipping or bundle savings on their next order.',
      ],
    },
    'Regular Customers': {
      title: 'Regular Customer Engagement & Activation',
      priority: 'Standard Baseline',
      badge_color: '#4F46E5',
      summary: 'Moderate frequency and spending customers who maintain steady baseline demand.',
      actions: [
        'Personalize marketing touchpoints according to favorite product category.',
        'Deploy seasonal promotional campaigns to increase purchase velocity.',
        'Promote high-rated cross-sell categories with positive review social proof.',
      ],
    },
    'At Risk': {
      title: 'At-Risk Customer Win-Back Campaign',
      priority: 'Urgent Attention Required',
      badge_color: '#F59E0B',
      summary: 'Valuable customers whose purchase frequency has dropped and recency has extended.',
      actions: [
        'Launch personalized win-back re-engagement email sequence with incentives.',
        'Audit logistics satisfaction and resolve recurring fulfillment bottlenecks.',
        'Re-engage with dynamic new arrivals in previously purchased categories.',
      ],
    },
    'Lost Customers': {
      title: 'Lost Customer Diagnostics & Revival',
      priority: 'Low Touch / Selective Reactivation',
      badge_color: '#DC2626',
      summary: 'Longest inactive customers with low recent engagement.',
      actions: [
        'Run low-cost automated revival campaigns during major seasonal clearance events.',
        'Collect exit feedback to diagnose root causes of customer churn.',
        'Filter unengaged contacts to optimize marketing campaign deliverability.',
      ],
    },
  };

  return (
    playbooks[segmentName] || {
      title: `${segmentName} Strategy`,
      priority: 'General Strategy',
      badge_color: '#64748B',
      summary: 'Audience segment based on RFM analytical scoring.',
      actions: ['Monitor purchase cadence and apply category-specific marketing.'],
    }
  );
};

const computeRfmDistribution = (customers) => {
  const totalCount = customers.length;
  if (totalCount === 0) return [];

  let totalRevenue = 0;
  const groups = {};

  customers.forEach((c) => {
    totalRevenue += c.total_spend;
    const seg = c.rfm_segment || 'Regular Customers';
    if (!groups[seg]) {
      groups[seg] = {
        rfm_segment: seg,
        customers: 0,
        total_revenue: 0,
        total_clv: 0,
        total_orders: 0,
        total_recency: 0,
        total_churn: 0,
      };
    }
    groups[seg].customers++;
    groups[seg].total_revenue += c.total_spend;
    groups[seg].total_clv += c.predicted_clv;
    groups[seg].total_orders += c.total_orders;
    groups[seg].total_recency += c.recency_days;
    groups[seg].total_churn += c.churn_probability;
  });

  return Object.values(groups)
    .map((g) => ({
      rfm_segment: g.rfm_segment,
      customers: g.customers,
      customer_share: parseFloat((g.customers / totalCount).toFixed(4)),
      total_revenue: parseFloat(g.total_revenue.toFixed(2)),
      revenue_share: parseFloat((g.total_revenue / Math.max(1, totalRevenue)).toFixed(4)),
      avg_spend: parseFloat((g.total_revenue / g.customers).toFixed(2)),
      avg_clv: parseFloat((g.total_clv / g.customers).toFixed(2)),
      avg_orders: parseFloat((g.total_orders / g.customers).toFixed(2)),
      avg_recency: Math.round(g.total_recency / g.customers),
      avg_churn_prob: parseFloat((g.total_churn / g.customers).toFixed(4)),
    }))
    .sort((a, b) => b.total_revenue - a.total_revenue);
};

const compareSegments = (customers, segA, segB) => {
  const totalBase = customers.length;
  let totalGmv = 0;
  customers.forEach((c) => (totalGmv += c.total_spend));

  const getMetrics = (segmentName) => {
    const sub = customers.filter((c) => c.rfm_segment === segmentName);
    if (sub.length === 0) {
      return {
        count: 0,
        share: 0,
        revenue: 0,
        rev_share: 0,
        avg_clv: 0,
        avg_orders: 0,
        avg_recency: 0,
        avg_aov: 0,
        churn_rate: 0,
        avg_csat: 0,
      };
    }

    let spend = 0, clv = 0, orders = 0, recency = 0, churn = 0, csat = 0, aovSum = 0;
    sub.forEach((c) => {
      spend += c.total_spend;
      clv += c.predicted_clv;
      orders += c.total_orders;
      recency += c.recency_days;
      churn += c.churn_probability;
      csat += c.avg_review_score;
      aovSum += c.avg_order_value;
    });

    const count = sub.length;
    return {
      count,
      share: count / Math.max(1, totalBase),
      revenue: parseFloat(spend.toFixed(2)),
      rev_share: spend / Math.max(1, totalGmv),
      avg_clv: parseFloat((clv / count).toFixed(2)),
      avg_orders: parseFloat((orders / count).toFixed(2)),
      avg_recency: Math.round(recency / count),
      avg_aov: parseFloat((aovSum / count).toFixed(2)),
      churn_rate: parseFloat((churn / count).toFixed(4)),
      avg_csat: parseFloat((csat / count).toFixed(2)),
    };
  };

  const mA = getMetrics(segA);
  const mB = getMetrics(segB);

  return [
    {
      metric: 'Customer Count',
      val_a: `${mA.count.toLocaleString()} (${(mA.share * 100).toFixed(1)}%)`,
      val_b: `${mB.count.toLocaleString()} (${(mB.share * 100).toFixed(1)}%)`,
    },
    {
      metric: 'Total Revenue (GMV)',
      val_a: `R$ ${mA.revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${(mA.rev_share * 100).toFixed(1)}%)`,
      val_b: `R$ ${mB.revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${(mB.rev_share * 100).toFixed(1)}%)`,
    },
    {
      metric: 'Average 12M CLV',
      val_a: `R$ ${mA.avg_clv.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      val_b: `R$ ${mB.avg_clv.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
    },
    {
      metric: 'Average Order Count',
      val_a: `${mA.avg_orders} orders`,
      val_b: `${mB.avg_orders} orders`,
    },
    {
      metric: 'Average Inactivity (Recency)',
      val_a: `${mA.avg_recency} days`,
      val_b: `${mB.avg_recency} days`,
    },
    {
      metric: 'Average Order Value (AOV)',
      val_a: `R$ ${mA.avg_aov.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
      val_b: `R$ ${mB.avg_aov.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
    },
    {
      metric: 'Average Churn Propensity',
      val_a: `${(mA.churn_rate * 100).toFixed(1)}%`,
      val_b: `${(mB.churn_rate * 100).toFixed(1)}%`,
    },
    {
      metric: 'Average CSAT Review Rating',
      val_a: `${mA.avg_csat.toFixed(2)} / 5.0`,
      val_b: `${mB.avg_csat.toFixed(2)} / 5.0`,
    },
  ];
};

module.exports = {
  getSegmentPlaybook,
  computeRfmDistribution,
  compareSegments,
};
