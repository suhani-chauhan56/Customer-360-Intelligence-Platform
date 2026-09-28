import { getCustomers, getRecommendations } from '../services/dataStore.js';
import {
  RECOMMENDATION_RULES,
  generateCustomerRecommendation,
} from '../services/analyticsService.js';

export function getRecommendationsOverview(req, res) {
  try {
    const customers = getCustomers();
    const { actionType = 'All', priority = 'All', limit = 50 } = req.query;

    // Generate recommendations for top sample
    const sample = customers.slice(0, 1000);
    const recs = sample.map(c => generateCustomerRecommendation(c));

    // Summary of portfolio recommendations
    const summaryMap = {};
    for (const r of recs) {
      const key = r.action_type;
      if (!summaryMap[key]) {
        summaryMap[key] = {
          action_type: r.action_type,
          priority: r.priority,
          badge_color: r.badge_color,
          channel: r.channel,
          count: 0,
          total_spend: 0,
          avg_clv: 0,
          avg_churn: 0,
        };
      }
      summaryMap[key].count += 1;
      summaryMap[key].total_spend += Number(r.total_spend || 0);
      summaryMap[key].avg_clv += Number(r.predicted_clv || 0);
      summaryMap[key].avg_churn += Number(r.churn_probability || 0);
    }

    const portfolioSummary = Object.values(summaryMap).map(s => ({
      ...s,
      total_spend: Math.round(s.total_spend),
      avg_clv: Math.round((s.avg_clv / Math.max(1, s.count)) * 100) / 100,
      avg_churn: Math.round((s.avg_churn / Math.max(1, s.count)) * 1000) / 10,
    })).sort((a, b) => b.count - a.count);

    // Filtered queue
    let queue = recs;
    if (actionType && actionType !== 'All') {
      queue = queue.filter(r => r.action_type === actionType);
    }
    if (priority && priority !== 'All') {
      queue = queue.filter(r => r.priority === priority);
    }

    // Next-Best-Category cross-sell items
    const rawRecs = getRecommendations().slice(0, 100);

    return res.status(200).json({
      success: true,
      data: {
        portfolioSummary,
        rulesMatrix: RECOMMENDATION_RULES,
        actionQueue: queue.slice(0, parseInt(limit, 10) || 50),
        nextBestCategories: rawRecs,
      },
    });
  } catch (error) {
    console.error('Error in getRecommendationsOverview:', error);
    return res.status(500).json({ success: false, message: error.message });
  }
}
