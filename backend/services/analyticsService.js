const dataService = require('./dataService');

const computeExecutiveKPIs = (customers) => {
  const totalCustomers = customers.length;
  if (totalCustomers === 0) {
    return {
      total_customers: 0,
      active_customers: 0,
      active_rate: 0,
      total_gmv: 0,
      avg_customer_value: 0,
      avg_order_value: 0,
      repeat_customer_rate: 0,
      repeat_customers_count: 0,
      at_risk_customers_count: 0,
      at_risk_revenue_exposure: 0,
      high_value_customers_count: 0,
      high_value_revenue: 0,
      avg_clv: 0,
    };
  }

  let totalGmv = 0;
  let totalOrders = 0;
  let activeCustomers = 0;
  let repeatCustomers = 0;
  let atRiskCount = 0;
  let atRiskRev = 0;
  let totalClv = 0;

  customers.forEach((c) => {
    totalGmv += c.total_spend;
    totalOrders += c.total_orders;
    totalClv += c.predicted_clv;

    if (c.recency_days <= 180) activeCustomers++;
    if (c.total_orders > 1) repeatCustomers++;
    if (c.churn_probability >= 0.65) {
      atRiskCount++;
      atRiskRev += c.total_spend;
    }
  });

  const sortedClv = [...customers].map((c) => c.predicted_clv).sort((a, b) => a - b);
  const p90Index = Math.floor(sortedClv.length * 0.90);
  const p90Clv = sortedClv[p90Index] || 0;

  let highValueCount = 0;
  let highValueRev = 0;
  customers.forEach((c) => {
    if (c.predicted_clv >= p90Clv) {
      highValueCount++;
      highValueRev += c.total_spend;
    }
  });

  return {
    total_customers: totalCustomers,
    active_customers: activeCustomers,
    active_rate: activeCustomers / totalCustomers,
    total_gmv: parseFloat(totalGmv.toFixed(2)),
    avg_customer_value: parseFloat((totalGmv / totalCustomers).toFixed(2)),
    avg_order_value: parseFloat((totalGmv / Math.max(1, totalOrders)).toFixed(2)),
    repeat_customer_rate: repeatCustomers / totalCustomers,
    repeat_customers_count: repeatCustomers,
    at_risk_customers_count: atRiskCount,
    at_risk_revenue_exposure: parseFloat(atRiskRev.toFixed(2)),
    high_value_customers_count: highValueCount,
    high_value_revenue: parseFloat(highValueRev.toFixed(2)),
    avg_clv: parseFloat((totalClv / totalCustomers).toFixed(2)),
  };
};

const computeDynamicInsights = (customers, kpis) => {
  const totalGmv = kpis.total_gmv;
  const totalCustomers = kpis.total_customers;
  if (totalCustomers === 0) return [];

  // Segment revenue calculation
  const segSpend = {};
  customers.forEach((c) => {
    segSpend[c.rfm_segment] = (segSpend[c.rfm_segment] || 0) + c.total_spend;
  });
  let topSegName = 'Champions';
  let topSegRev = 0;
  Object.entries(segSpend).forEach(([seg, rev]) => {
    if (rev > topSegRev) {
      topSegRev = rev;
      topSegName = seg;
    }
  });
  const topSegShare = topSegRev / Math.max(1, totalGmv);

  // Geographic revenue calculation
  const stateSpend = {};
  customers.forEach((c) => {
    stateSpend[c.state] = (stateSpend[c.state] || 0) + c.total_spend;
  });
  let topStateName = 'SP';
  let topStateRev = 0;
  Object.entries(stateSpend).forEach(([st, rev]) => {
    if (rev > topStateRev) {
      topStateRev = rev;
      topStateName = st;
    }
  });
  const topStateShare = topStateRev / Math.max(1, totalGmv);

  // Top 20% spenders
  const sortedSpend = [...customers].map((c) => c.total_spend).sort((a, b) => a - b);
  const p80Index = Math.floor(sortedSpend.length * 0.80);
  const p80Spend = sortedSpend[p80Index] || 0;
  let top20Rev = 0;
  customers.forEach((c) => {
    if (c.total_spend >= p80Spend) top20Rev += c.total_spend;
  });
  const top20Share = top20Rev / Math.max(1, totalGmv);

  return [
    {
      title: 'Revenue Concentration (Pareto Distribution)',
      observation: 'A small minority of top spenders accounts for the disproportionate share of cumulative merchandise sales.',
      evidence: `The top 20% of spenders account for ${(top20Share * 100).toFixed(1)}% (R$ ${top20Rev.toLocaleString('en-US', { minimumFractionDigits: 2 })}) of total GMV. Leading segment '${topSegName}' contributes R$ ${topSegRev.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${(topSegShare * 100).toFixed(1)}%).`,
      implication: 'Prioritize VIP retention and loyalty perks for this cohort to safeguard the core revenue foundation.',
      badge: 'Pareto Health',
      kind: 'info',
    },
    {
      title: 'Regional Demand Hubs (Geographic Focus)',
      observation: 'Merchandise demand is strongly clustered in key economic centers.',
      evidence: `State '${topStateName}' represents the largest geographic market with R$ ${topStateRev.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${(topStateShare * 100).toFixed(1)}% of total GMV).`,
      implication: 'Optimize regional fulfillment, carrier routing, and localized promotional campaigns in primary states.',
      badge: 'Geographic Intelligence',
      kind: 'success',
    },
    {
      title: 'Single-Purchase Drop-Off Opportunity',
      observation: 'The majority of customer relationships conclude after a single completed purchase.',
      evidence: `Repeat buyer rate is ${(kpis.repeat_customer_rate * 100).toFixed(1)}% (${kpis.repeat_customers_count.toLocaleString()} multi-order buyers out of ${totalCustomers.toLocaleString()} total profiles).`,
      implication: 'Deploying an automated 14-day post-purchase replenishment workflow represents the highest leverage CLV multiplier.',
      badge: 'Retention Lever',
      kind: kpis.repeat_customer_rate < 0.1 ? 'warning' : 'info',
    },
    {
      title: 'Churn Risk Exposure & Capital Protection',
      observation: 'A substantial amount of historical revenue belongs to customers currently exhibiting extended inactivity.',
      evidence: `${kpis.at_risk_customers_count.toLocaleString()} customers (${((kpis.at_risk_customers_count / Math.max(1, totalCustomers)) * 100).toFixed(1)}%) represent R$ ${kpis.at_risk_revenue_exposure.toLocaleString('en-US', { minimumFractionDigits: 2 })} in cumulative merchandise spend at risk (churn probability >= 65%).`,
      implication: 'Deploy targeted win-back incentives to reactivate lapsed relationships before complete account attrition.',
      badge: 'Risk Exposure',
      kind: 'alert',
    },
  ];
};

const computeAudienceComposition = (customers) => {
  const total = customers.length;
  if (total === 0) return { pie: [], cohorts: {} };

  const segCounts = {};
  customers.forEach((c) => {
    segCounts[c.rfm_segment] = (segCounts[c.rfm_segment] || 0) + 1;
  });

  const pie = Object.entries(segCounts).map(([name, count]) => ({
    name,
    count,
    share: count / total,
  }));

  // Cohort summaries
  const healthyCohorts = ['Champions', 'Loyal Customers', 'Potential Loyalists'];
  let hCount = 0, hRev = 0;
  let regCount = 0, regRev = 0;
  let riskCount = 0, riskRev = 0;
  let lostCount = 0, lostRev = 0;

  customers.forEach((c) => {
    if (healthyCohorts.includes(c.rfm_segment)) {
      hCount++;
      hRev += c.total_spend;
    } else if (c.rfm_segment === 'Regular Customers') {
      regCount++;
      regRev += c.total_spend;
    } else if (c.rfm_segment === 'At Risk') {
      riskCount++;
      riskRev += c.total_spend;
    } else if (c.rfm_segment === 'Lost Customers') {
      lostCount++;
      lostRev += c.total_spend;
    }
  });

  return {
    pie,
    cohorts: {
      healthy: { count: hCount, share: hCount / total, revenue: parseFloat(hRev.toFixed(2)) },
      regular: { count: regCount, share: regCount / total, revenue: parseFloat(regRev.toFixed(2)) },
      at_risk: { count: riskCount, share: riskCount / total, revenue: parseFloat(riskRev.toFixed(2)) },
      lost: { count: lostCount, share: lostCount / total, revenue: parseFloat(lostRev.toFixed(2)) },
    },
  };
};

const computeMonthlyRevenueTrajectory = () => {
  const orders = dataService.getAllOrders();
  const valid = orders.filter((o) => !['canceled', 'unavailable'].includes(o.order_status) && o.month_year);

  const monthly = {};
  valid.forEach((o) => {
    if (!monthly[o.month_year]) {
      monthly[o.month_year] = { month: o.month_year, revenue: 0, orders: 0, orderSet: new Set() };
    }
    monthly[o.month_year].revenue += o.revenue;
    if (o.order_id && !monthly[o.month_year].orderSet.has(o.order_id)) {
      monthly[o.month_year].orderSet.add(o.order_id);
      monthly[o.month_year].orders++;
    }
  });

  return Object.values(monthly)
    .map((m) => ({
      month: m.month,
      revenue: parseFloat(m.revenue.toFixed(2)),
      orders: m.orders,
    }))
    .sort((a, b) => a.month.localeCompare(b.month));
};

const computeSegmentAndStateRevenue = (customers) => {
  const segRev = {};
  const stateRev = {};

  customers.forEach((c) => {
    segRev[c.rfm_segment] = (segRev[c.rfm_segment] || 0) + c.total_spend;
    stateRev[c.state] = (stateRev[c.state] || 0) + c.total_spend;
  });

  const segments = Object.entries(segRev)
    .map(([segment, revenue]) => ({ segment, revenue: parseFloat(revenue.toFixed(2)) }))
    .sort((a, b) => b.revenue - a.revenue);

  const states = Object.entries(stateRev)
    .map(([state, revenue]) => ({ state, revenue: parseFloat(revenue.toFixed(2)) }))
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 10);

  return { segments, states };
};

module.exports = {
  computeExecutiveKPIs,
  computeDynamicInsights,
  computeAudienceComposition,
  computeMonthlyRevenueTrajectory,
  computeSegmentAndStateRevenue,
};
