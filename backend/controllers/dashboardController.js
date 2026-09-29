const dataService = require('../services/dataService');
const analyticsService = require('../services/analyticsService');

const getDashboardOverview = async (req, res, next) => {
  try {
    const filters = {
      segment: req.query.segment || 'All',
      risk_level: req.query.risk_level || 'All',
      state: req.query.state || 'All',
      clv_band: req.query.clv_band || 'All',
      recency_filter: req.query.recency_filter || 'All',
      search_query: req.query.search_query || '',
    };

    const filtered = dataService.getCustomers(filters);
    const kpis = analyticsService.computeExecutiveKPIs(filtered);
    const dynamicInsights = analyticsService.computeDynamicInsights(filtered, kpis);
    const audienceComposition = analyticsService.computeAudienceComposition(filtered);
    const monthlyTrajectory = analyticsService.computeMonthlyRevenueTrajectory();
    const { segments, states } = analyticsService.computeSegmentAndStateRevenue(filtered);

    res.json({
      success: true,
      data: {
        kpis,
        insights: dynamicInsights,
        audience_composition: audienceComposition,
        monthly_trajectory: monthlyTrajectory,
        segment_revenue: segments,
        state_revenue: states,
        total_filtered_records: filtered.length,
      },
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getDashboardOverview,
};
