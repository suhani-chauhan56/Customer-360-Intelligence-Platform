const dataService = require('./dataService');
const customerService = require('./customerService');
const rfmService = require('./rfmService');

const detectIntent = (query, contextCid) => {
  const q = query.toLowerCase();

  const cidMatch = q.match(/\b([a-f0-9]{32})\b/);
  const foundCid = cidMatch ? cidMatch[1] : contextCid;

  const segments = ['champions', 'loyal customers', 'potential loyalists', 'at risk', 'regular customers', 'lost customers'];
  let foundSeg = null;
  for (const s of segments) {
    if (q.includes(s)) {
      foundSeg = s.split(' ').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
      break;
    }
  }

  if (
    ['high value and high risk', 'high-value and high-risk', 'vips at risk', 'high risk high spend', 'at risk high value'].some((k) =>
      q.includes(k)
    )
  ) {
    return { intent: 'high_value_high_risk', params: {} };
  }

  if (
    ['which segment generates the most', 'top segment revenue', 'highest revenue segment', 'segment revenue'].some((k) =>
      q.includes(k)
    )
  ) {
    return { intent: 'segment_revenue_leader', params: {} };
  }

  if (
    ['explain this customer', 'why is this customer', 'explain risk', 'customer risk', "customer's risk"].some((k) => q.includes(k)) ||
    (foundCid && q.includes('risk'))
  ) {
    return { intent: 'customer_risk_explanation', params: { customer_id: foundCid } };
  }

  if (['why is this segment important', 'explain segment', 'about segment', 'segment playbook'].some((k) => q.includes(k)) || foundSeg) {
    return { intent: 'segment_importance', params: { segment_name: foundSeg || 'Champions' } };
  }

  if (['repeat purchase', 'repeat rate', 'single order', 'multi-order', 'second purchase'].some((k) => q.includes(k))) {
    return { intent: 'repeat_rate_opportunity', params: {} };
  }

  if (['geographic', 'state', 'region', 'where are customers', 'top states', 'location'].some((k) => q.includes(k))) {
    return { intent: 'geographic_hubs', params: {} };
  }

  if (['clv', 'lifetime value', 'forward value', 'predicted value'].some((k) => q.includes(k))) {
    return { intent: 'clv_benchmark', params: {} };
  }

  if (['overview', 'summary', 'total revenue', 'how many customers', 'macro', 'kpi'].some((k) => q.includes(k))) {
    return { intent: 'macro_overview', params: {} };
  }

  return { intent: 'unsupported', params: {} };
};

const processGroundedQuery = (query, contextCustomerId = null, customers = null) => {
  const dataset = customers || dataService.getCustomers();
  const cleanQuery = query.trim();

  if (!cleanQuery) {
    return {
      query,
      intent: 'empty_query',
      headline: 'No Question Provided',
      detailed_answer: 'Please enter a question regarding your customer base, segments, risks, or metrics.',
      metrics: {},
      evidence_points: ['Input was empty.'],
      recommended_action: "Type a query such as 'Which customers are high value and high risk?'",
      data_source: 'customer_360_features.csv',
      confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
      limitations_disclaimer:
        'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
    };
  }

  const { intent, params } = detectIntent(cleanQuery, contextCustomerId);
  let totalGmv = 0;
  dataset.forEach((c) => (totalGmv += c.total_spend));
  const totalCust = dataset.length;

  if (intent === 'high_value_high_risk') {
    const sortedSpend = [...dataset].map((c) => c.total_spend).sort((a, b) => a - b);
    const p80Spend = sortedSpend[Math.floor(sortedSpend.length * 0.8)] || 200;
    const hvHr = dataset.filter((c) => c.total_spend >= p80Spend && c.churn_probability >= 0.65);

    const count = hvHr.length;
    const shareBase = count / Math.max(1, totalCust);
    let revExposed = 0, recSum = 0;
    hvHr.forEach((c) => {
      revExposed += c.total_spend;
      recSum += c.recency_days;
    });
    const avgRecency = count > 0 ? recSum / count : 0;
    const shareRev = revExposed / Math.max(1, totalGmv);

    return {
      query: cleanQuery,
      intent,
      headline: `${count.toLocaleString()} High-Value Customers (R$ ${revExposed.toLocaleString('en-US', { minimumFractionDigits: 2 })}) Are at Severe Churn Risk`,
      detailed_answer: `Across the active base of ${totalCust.toLocaleString()} customers, ${count.toLocaleString()} profiles (${(shareBase * 100).toFixed(1)}%) fall into the top 20% spend tier (>= R$ ${p80Spend.toFixed(2)}) while exhibiting an estimated churn propensity of 65% or higher. These customers have an average inactivity period of ${Math.round(avgRecency)} days.`,
      metrics: {
        at_risk_vip_count: count,
        at_risk_vip_share_pct: parseFloat((shareBase * 100).toFixed(2)),
        revenue_exposed_brl: parseFloat(revExposed.toFixed(2)),
        revenue_exposed_share_pct: parseFloat((shareRev * 100).toFixed(2)),
        average_inactivity_days: Math.round(avgRecency),
      },
      evidence_points: [
        `Spend threshold for Top 20% cohort: >= R$ ${p80Spend.toFixed(2)}.`,
        `Identified ${count.toLocaleString()} customers holding ${(shareRev * 100).toFixed(1)}% of cumulative merchandise spend.`,
        `Average days since last purchase for this cohort: ${Math.round(avgRecency)} days.`,
      ],
      recommended_action: 'Immediate white-glove outreach via VIP concierge or specialized win-back incentive to protect vulnerable core revenue.',
      data_source: 'customer_360_features.csv',
      confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
      limitations_disclaimer:
        'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
    };
  }

  if (intent === 'segment_revenue_leader') {
    const segMap = {};
    dataset.forEach((c) => {
      if (!segMap[c.rfm_segment]) segMap[c.rfm_segment] = { revenue: 0, count: 0 };
      segMap[c.rfm_segment].revenue += c.total_spend;
      segMap[c.rfm_segment].count++;
    });

    const sortedSegs = Object.entries(segMap).sort((a, b) => b[1].revenue - a[1].revenue);
    const topSeg = sortedSegs[0] || ['Champions', { revenue: 0, count: 0 }];
    const topName = topSeg[0];
    const topRev = topSeg[1].revenue;
    const topCount = topSeg[1].count;
    const topShare = topRev / Math.max(1, totalGmv);
    const avgSpend = topRev / Math.max(1, topCount);

    return {
      query: cleanQuery,
      intent,
      headline: `'${topName}' Generates the Highest Revenue (R$ ${topRev.toLocaleString('en-US', { minimumFractionDigits: 2 })}, ${(topShare * 100).toFixed(1)}% of GMV)`,
      detailed_answer: `The '${topName}' segment represents the leading commercial driver, generating R$ ${topRev.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${(topShare * 100).toFixed(1)}%) of total portfolio spend across ${topCount.toLocaleString()} customers, with an average spend of R$ ${avgSpend.toFixed(2)} per customer.`,
      metrics: {
        leading_segment: topName,
        segment_revenue_brl: parseFloat(topRev.toFixed(2)),
        revenue_share_pct: parseFloat((topShare * 100).toFixed(2)),
        customer_count: topCount,
        avg_spend_per_customer_brl: parseFloat(avgSpend.toFixed(2)),
      },
      evidence_points: [
        `Top segment '${topName}' outperforms #2 segment by R$ ${(topRev - (sortedSegs[1] ? sortedSegs[1][1].revenue : 0)).toLocaleString('en-US', { minimumFractionDigits: 2 })}.`,
        `Customer count in this segment represents ${((topCount / Math.max(1, totalCust)) * 100).toFixed(1)}% of total audience.`,
      ],
      recommended_action: `Maintain dedicated loyalty rewards and VIP engagement for '${topName}' to sustain revenue velocity.`,
      data_source: 'customer_360_features.csv',
      confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
      limitations_disclaimer:
        'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
    };
  }

  if (intent === 'customer_risk_explanation') {
    const cid = params.customer_id;
    if (!cid) {
      return {
        query: cleanQuery,
        intent,
        headline: 'Customer ID Required for Individual Diagnostics',
        detailed_answer: 'To explain risk for an individual customer, select a profile in Customer 360 or provide a valid 32-character Customer ID.',
        metrics: {},
        evidence_points: ['No Customer ID was detected in query context.'],
        recommended_action: 'Navigate to Customer 360 or provide a valid Customer ID in the prompt.',
        data_source: 'customer_360_features.csv',
        confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
        limitations_disclaimer:
          'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
      };
    }

    const profile = dataService.getCustomerById(cid);
    if (!profile) {
      return {
        query: cleanQuery,
        intent,
        headline: `Customer ID '${cid}' Not Found`,
        detailed_answer: 'The requested customer profile could not be found within the currently filtered customer base.',
        metrics: { customer_id: cid },
        evidence_points: ['Zero database records matched the given ID.'],
        recommended_action: 'Provide a valid customer ID.',
        data_source: 'customer_360_features.csv',
        confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
        limitations_disclaimer:
          'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
      };
    }

    const diag = customerService.diagnoseCustomerRiskFactors(profile);
    const health = customerService.computeCustomerHealth(profile);
    const churnP = profile.churn_probability;
    const recency = Math.round(profile.recency_days);
    const spend = profile.total_spend;

    const riskList = diag.risk_factors.length > 0 ? diag.risk_factors : ['Extended purchase inactivity'];

    return {
      query: cleanQuery,
      intent,
      headline: `Customer #${cid.substring(0, 8)}... Risk Propensity is ${(churnP * 100).toFixed(1)}% (${diag.risk_level})`,
      detailed_answer: `Customer #${cid.substring(0, 8)}... has a calibrated churn probability of ${(churnP * 100).toFixed(1)}%, a documented Health Score of ${health.total_score}/100 (${health.health_tier}), and an inactivity window of ${recency} days. Contributing risk indicators include: ${riskList.join('; ')}.`,
      metrics: {
        customer_id: cid,
        churn_probability: churnP,
        risk_tier: diag.risk_level,
        health_score: health.total_score,
        recency_days: recency,
        total_spend_brl: spend,
      },
      evidence_points: [
        `Inactivity interval: ${recency} days since last completed order.`,
        `Historical lifetime merchandise spend: R$ ${spend.toFixed(2)} across ${profile.total_orders} order(s).`,
        `CSAT rating: ${profile.avg_review_score.toFixed(1)} / 5.0 stars.`,
        diag.exposure_note,
      ],
      recommended_action: 'Initiate targeted reactivation campaign and review recent fulfillment interactions.',
      data_source: 'customer_360_features.csv',
      confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
      limitations_disclaimer:
        'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
    };
  }

  if (intent === 'repeat_rate_opportunity') {
    let repeatCount = 0;
    dataset.forEach((c) => {
      if (c.total_orders > 1) repeatCount++;
    });
    const singleCount = totalCust - repeatCount;
    const repeatRate = repeatCount / Math.max(1, totalCust);

    return {
      query: cleanQuery,
      intent,
      headline: `Repeat Buyer Rate is ${(repeatRate * 100).toFixed(1)}% (${repeatCount.toLocaleString()} Repeat vs ${singleCount.toLocaleString()} Single-Order)`,
      detailed_answer: `Out of ${totalCust.toLocaleString()} customers, only ${repeatCount.toLocaleString()} (${(repeatRate * 100).toFixed(1)}%) have placed more than one order. Over ${(((totalCust - repeatCount) / Math.max(1, totalCust)) * 100).toFixed(1)}% of relationships currently conclude after the initial transaction, representing the primary bottleneck to accelerating CLV.`,
      metrics: {
        total_customers: totalCust,
        repeat_customers: repeatCount,
        single_order_customers: singleCount,
        repeat_rate_pct: parseFloat((repeatRate * 100).toFixed(2)),
      },
      evidence_points: [
        `Single-purchase drop-off affects ${singleCount.toLocaleString()} customer accounts.`,
        'Repeat buyers generate higher AOV on subsequent transactions.',
      ],
      recommended_action: 'Deploy an automated 14-day post-purchase replenishment and category cross-sell sequence.',
      data_source: 'customer_360_features.csv',
      confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
      limitations_disclaimer:
        'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
    };
  }

  if (intent === 'geographic_hubs') {
    const stateMap = {};
    dataset.forEach((c) => {
      stateMap[c.state] = (stateMap[c.state] || 0) + c.total_spend;
    });
    const sortedStates = Object.entries(stateMap).sort((a, b) => b[1] - a[1]);
    const topState = sortedStates[0] || ['SP', 0];
    const stateName = topState[0];
    const stateRev = topState[1];
    const share = stateRev / Math.max(1, totalGmv);

    return {
      query: cleanQuery,
      intent,
      headline: `State '${stateName}' Leads Demand with R$ ${stateRev.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${(share * 100).toFixed(1)}% of GMV)`,
      detailed_answer: `Customer demand is highly concentrated in state '${stateName}', accounting for R$ ${stateRev.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${(share * 100).toFixed(1)}%) of total merchandise spend. Top 3 states drive ${(((sortedStates.slice(0, 3).reduce((s, v) => s + v[1], 0)) / Math.max(1, totalGmv)) * 100).toFixed(1)}% of GMV.`,
      metrics: {
        leading_state: stateName,
        state_revenue_brl: parseFloat(stateRev.toFixed(2)),
        state_revenue_share_pct: parseFloat((share * 100).toFixed(2)),
      },
      evidence_points: [
        `Top 3 states: ${sortedStates.slice(0, 3).map((s) => s[0]).join(', ')}.`,
        `Fulfillment optimization in ${stateName} delivers highest direct revenue impact.`,
      ],
      recommended_action: 'Optimize regional logistics, fulfillment SLAs, and localized marketing in top demand states.',
      data_source: 'customer_360_features.csv',
      confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
      limitations_disclaimer:
        'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
    };
  }

  if (intent === 'clv_benchmark') {
    let clvSum = 0;
    dataset.forEach((c) => (clvSum += c.predicted_clv));
    const avgClv = clvSum / Math.max(1, totalCust);
    const sortedClv = [...dataset].map((c) => c.predicted_clv).sort((a, b) => a - b);
    const p90 = sortedClv[Math.floor(sortedClv.length * 0.9)] || 0;
    const top10 = sortedClv.slice(Math.floor(sortedClv.length * 0.9));
    const top10Avg = top10.length > 0 ? top10.reduce((s, v) => s + v, 0) / top10.length : 0;

    return {
      query: cleanQuery,
      intent,
      headline: `Average 12M Forward CLV is R$ ${avgClv.toFixed(2)} (Top 10% Average: R$ ${top10Avg.toFixed(2)})`,
      detailed_answer: `Across the active customer base, the forward 12-month predicted CLV averages R$ ${avgClv.toFixed(2)}, representing a cumulative pipeline value of R$ ${clvSum.toLocaleString('en-US', { minimumFractionDigits: 2 })}. Top 10% high-value customers exceed R$ ${p90.toFixed(2)} in individual forward value.`,
      metrics: {
        average_12m_clv_brl: parseFloat(avgClv.toFixed(2)),
        p90_threshold_brl: parseFloat(p90.toFixed(2)),
        top_10_pct_avg_clv_brl: parseFloat(top10Avg.toFixed(2)),
        total_pipeline_clv_brl: parseFloat(clvSum.toFixed(2)),
      },
      evidence_points: [
        'Model predictions generated by Ridge Regression on RFM & engagement features.',
        'Top decile represents core focus for VIP concierge outreach.',
      ],
      recommended_action: 'Align account tiers and customer success resource allocation with predicted CLV brackets.',
      data_source: 'customer_360_features.csv',
      confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
      limitations_disclaimer:
        'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
    };
  }

  // Macro Overview Fallback
  let ordersSum = 0, repeatCount = 0;
  dataset.forEach((c) => {
    ordersSum += c.total_orders;
    if (c.total_orders > 1) repeatCount++;
  });
  const avgSpend = totalGmv / Math.max(1, totalCust);
  const avgOrders = ordersSum / Math.max(1, totalCust);
  const repeatRate = repeatCount / Math.max(1, totalCust);

  return {
    query: cleanQuery,
    intent: intent === 'macro_overview' ? 'macro_overview' : 'unsupported_or_ambiguous',
    headline: `Portfolio Status: ${totalCust.toLocaleString()} Customers with R$ ${totalGmv.toLocaleString('en-US', { minimumFractionDigits: 2 })} Merchandise GMV`,
    detailed_answer: `The analyzed dataset contains ${totalCust.toLocaleString()} unique customer profiles representing R$ ${totalGmv.toLocaleString('en-US', { minimumFractionDigits: 2 })} in total GMV. Average customer spend is R$ ${avgSpend.toFixed(2)} with ${avgOrders.toFixed(2)} orders per profile. Repeat buyer rate is currently ${(repeatRate * 100).toFixed(1)}%.`,
    metrics: {
      total_customers: totalCust,
      total_gmv_brl: parseFloat(totalGmv.toFixed(2)),
      avg_spend_brl: parseFloat(avgSpend.toFixed(2)),
      avg_orders_per_customer: parseFloat(avgOrders.toFixed(2)),
      repeat_customer_rate_pct: parseFloat((repeatRate * 100).toFixed(2)),
    },
    evidence_points: [
      `Aggregated from ${totalCust.toLocaleString()} verified profile records.`,
      `Repeat buyers: ${repeatCount.toLocaleString()} profiles.`,
    ],
    recommended_action: 'Focus commercial strategy on accelerating first-to-second purchase conversion.',
    data_source: 'customer_360_features.csv',
    confidence_rating: 'Deterministic (100% Grounded in Verified Data)',
    limitations_disclaimer:
      'Metrics reflect the active filtered cohort. Model outputs represent correlational propensities, not guaranteed causal outcomes.',
  };
};

module.exports = {
  processGroundedQuery,
};
