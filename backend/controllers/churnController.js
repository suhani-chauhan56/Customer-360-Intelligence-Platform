import { getCustomers, getFeatureImportance } from '../services/dataStore.js';
import {
  computeQuadrantMatrix,
  prioritizeRetentionQueue,
  simulateChurn,
  computeExecutiveKPIs,
} from '../services/analyticsService.js';

export function getChurnOverview(req, res) {
  try {
    const customers = getCustomers();
    const { kpis, riskDistribution } = computeExecutiveKPIs(customers);
    const quadrantMatrix = computeQuadrantMatrix(customers);
    const featureImportance = getFeatureImportance();
    const retentionQueue = prioritizeRetentionQueue(customers, 50);

    return res.status(200).json({
      success: true,
      data: {
        summary: {
          totalCustomers: kpis.totalCustomers,
          atRiskCount: kpis.atRiskCustomersCount,
          atRiskRevenue: kpis.atRiskRevenueExposure,
          atRiskPct: Math.round((kpis.atRiskCustomersCount / Math.max(1, kpis.totalCustomers)) * 1000) / 10,
          avgChurnProb: Math.round(customers.reduce((a, c) => a + Number(c.churn_probability || 0), 0) / Math.max(1, customers.length) * 1000) / 10,
        },
        riskDistribution,
        quadrantMatrix,
        featureImportance,
        retentionQueue,
      },
    });
  } catch (error) {
    console.error('Error in getChurnOverview:', error);
    return res.status(500).json({ success: false, message: error.message });
  }
}

export function handleChurnSimulation(req, res) {
  try {
    const {
      recency_days = 120,
      frequency = 1,
      monetary = 150,
      avg_order_value = 150,
      number_of_products = 1,
      customer_age_days = 200,
    } = req.body;

    const result = simulateChurn(recency_days, frequency, monetary, avg_order_value, number_of_products, customer_age_days);
    return res.status(200).json({ success: true, data: result });
  } catch (error) {
    return res.status(500).json({ success: false, message: error.message });
  }
}
