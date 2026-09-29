const dataService = require('../services/dataService');
const clvService = require('../services/clvService');

const getClvOverview = async (req, res, next) => {
  try {
    const customers = dataService.getCustomers();
    const overview = clvService.computeClvOverview(customers);
    const brackets = clvService.computeClvBins(customers);
    const highValueCohort = clvService.analyzeHighValueCohort(customers, 0.90);

    res.json({
      success: true,
      data: {
        benchmarks: overview,
        brackets,
        high_value_cohort: highValueCohort,
      },
    });
  } catch (error) {
    next(error);
  }
};

const simulateClvScenario = async (req, res, next) => {
  try {
    const inputs = {
      recency_days: parseFloat(req.body.recency_days || 30),
      frequency: parseFloat(req.body.frequency || 3),
      monetary: parseFloat(req.body.monetary || 450),
      avg_order_value: parseFloat(req.body.avg_order_value || 150),
      number_of_products: parseFloat(req.body.number_of_products || 3),
      customer_age_days: parseFloat(req.body.customer_age_days || 90),
    };

    const simulation = clvService.simulateClv(inputs);

    res.json({
      success: true,
      data: simulation,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getClvOverview,
  simulateClvScenario,
};
