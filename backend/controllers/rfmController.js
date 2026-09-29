const dataService = require('../services/dataService');
const rfmService = require('../services/rfmService');

const getRfmOverview = async (req, res, next) => {
  try {
    const customers = dataService.getCustomers();
    const distribution = rfmService.computeRfmDistribution(customers);

    res.json({
      success: true,
      data: {
        distribution,
        total_customers: customers.length,
      },
    });
  } catch (error) {
    next(error);
  }
};

const getSegmentDetails = async (req, res, next) => {
  try {
    const { segment } = req.params;
    const customers = dataService.getCustomers();
    const segmentCustomers = customers.filter((c) => c.rfm_segment === segment);
    const playbook = rfmService.getSegmentPlaybook(segment);

    let totalSpend = 0, totalClv = 0, totalOrders = 0, totalRecency = 0, totalChurn = 0;
    segmentCustomers.forEach((c) => {
      totalSpend += c.total_spend;
      totalClv += c.predicted_clv;
      totalOrders += c.total_orders;
      totalRecency += c.recency_days;
      totalChurn += c.churn_probability;
    });

    const count = segmentCustomers.length;
    const metrics = {
      size: count,
      share_of_base: count / Math.max(1, customers.length),
      total_gmv: parseFloat(totalSpend.toFixed(2)),
      avg_clv: count > 0 ? parseFloat((totalClv / count).toFixed(2)) : 0,
      avg_orders: count > 0 ? parseFloat((totalOrders / count).toFixed(2)) : 0,
      avg_recency: count > 0 ? Math.round(totalRecency / count) : 0,
      avg_churn_prob: count > 0 ? parseFloat((totalChurn / count).toFixed(4)) : 0,
    };

    const topCustomers = [...segmentCustomers].sort((a, b) => b.total_spend - a.total_spend).slice(0, 50);

    res.json({
      success: true,
      data: {
        segment,
        playbook,
        metrics,
        top_customers: topCustomers,
      },
    });
  } catch (error) {
    next(error);
  }
};

const compareSegments = async (req, res, next) => {
  try {
    const { segmentA, segmentB } = req.query;
    const customers = dataService.getCustomers();
    const comparison = rfmService.compareSegments(customers, segmentA || 'Champions', segmentB || 'Loyal Customers');

    res.json({
      success: true,
      data: comparison,
    });
  } catch (error) {
    next(error);
  }
};

const buildCohort = async (req, res, next) => {
  try {
    const { segments = [], min_spend = 0, max_churn = 1.0 } = req.body;
    let customers = dataService.getCustomers();

    if (Array.isArray(segments) && segments.length > 0) {
      const segSet = new Set(segments);
      customers = customers.filter((c) => segSet.has(c.rfm_segment));
    }

    const minSpendNum = parseFloat(min_spend) || 0;
    const maxChurnNum = parseFloat(max_churn) || 1.0;

    const cohort = customers.filter(
      (c) => c.total_spend >= minSpendNum && c.churn_probability <= maxChurnNum
    );

    let totalGmv = 0, totalClv = 0;
    cohort.forEach((c) => {
      totalGmv += c.total_spend;
      totalClv += c.predicted_clv;
    });

    res.json({
      success: true,
      data: {
        matching_count: cohort.length,
        total_gmv: parseFloat(totalGmv.toFixed(2)),
        avg_clv: cohort.length > 0 ? parseFloat((totalClv / cohort.length).toFixed(2)) : 0,
        cohort: cohort.slice(0, 500),
      },
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getRfmOverview,
  getSegmentDetails,
  compareSegments,
  buildCohort,
};
