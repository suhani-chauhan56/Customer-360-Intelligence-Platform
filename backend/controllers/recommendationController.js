const dataService = require('../services/dataService');
const recommendationService = require('../services/recommendationService');

const getRecommendationsOverview = async (req, res, next) => {
  try {
    const customers = dataService.getCustomers();
    const portfolio = recommendationService.computeRecommendationPortfolio(customers, 2500);
    const summary = recommendationService.computeRecommendationSummary(portfolio);
    const rules = recommendationService.RECOMMENDATION_RULES;

    const actionTypeFilter = req.query.action_type || 'All';
    const priorityFilter = req.query.priority || 'All';
    const segmentFilter = req.query.segment || 'All';

    let filteredQueue = portfolio;
    if (actionTypeFilter !== 'All') {
      filteredQueue = filteredQueue.filter((r) => r.action_type === actionTypeFilter);
    }
    if (priorityFilter !== 'All') {
      filteredQueue = filteredQueue.filter((r) => r.priority === priorityFilter);
    }
    if (segmentFilter !== 'All') {
      filteredQueue = filteredQueue.filter((r) => r.rfm_segment === segmentFilter);
    }

    const urgentCount = portfolio.filter((r) => r.priority === 'Urgent').length;
    const highCount = portfolio.filter((r) => r.priority === 'High').length;
    let totalSpendCovered = 0;
    portfolio.forEach((r) => (totalSpendCovered += r.total_spend));

    const topAction = summary.length > 0 ? summary[0].action_type : 'Standard Lifecycle Nurture';

    const sampleCategoryCatalog = dataService.getAllRecommendations().slice(0, 100);

    res.json({
      success: true,
      data: {
        kpis: {
          actionable_profiles: portfolio.length,
          urgent_count: urgentCount,
          high_count: highCount,
          top_action: topAction,
          covered_revenue: parseFloat(totalSpendCovered.toFixed(2)),
        },
        summary,
        rules,
        queue: filteredQueue.slice(0, 200),
        total_queue_count: filteredQueue.length,
        category_catalog_sample: sampleCategoryCatalog,
      },
    });
  } catch (error) {
    next(error);
  }
};

const getCustomerNextBestCategory = async (req, res, next) => {
  try {
    const { customerId } = req.params;
    const recs = dataService.getRecommendationsForCustomer(customerId);

    res.json({
      success: true,
      data: recs,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getRecommendationsOverview,
  getCustomerNextBestCategory,
};
