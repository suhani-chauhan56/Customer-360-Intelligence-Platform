const dataService = require('../services/dataService');
const churnService = require('../services/churnService');

const getChurnOverview = async (req, res, next) => {
  try {
    const customers = dataService.getCustomers();
    const riskOverview = churnService.computeRiskOverview(customers);
    const quadrantMatrix = churnService.computeQuadrantMatrix(customers);
    const retentionQueue = churnService.getPrioritizedRetentionQueue(customers, 200);
    const featureImportance = dataService.getFeatureImportance();

    res.json({
      success: true,
      data: {
        risk_overview: riskOverview,
        quadrant_matrix: quadrantMatrix,
        retention_queue: retentionQueue,
        feature_importance: featureImportance,
      },
    });
  } catch (error) {
    next(error);
  }
};

const simulateChurnScenario = async (req, res, next) => {
  try {
    const inputs = {
      recency_days: parseFloat(req.body.recency_days || 90),
      frequency: parseFloat(req.body.frequency || 2),
      monetary: parseFloat(req.body.monetary || 280),
      avg_order_value: parseFloat(req.body.avg_order_value || 140),
      number_of_products: parseFloat(req.body.number_of_products || 2),
      customer_age_days: parseFloat(req.body.customer_age_days || 45),
    };

    const simulation = churnService.simulateChurn(inputs);

    res.json({
      success: true,
      data: simulation,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getChurnOverview,
  simulateChurnScenario,
};
