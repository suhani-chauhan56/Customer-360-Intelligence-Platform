const dataService = require('../services/dataService');

const getAnalyticsExplorer = async (req, res, next) => {
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

    let totalGmv = 0, totalClv = 0, churnSum = 0;
    filtered.forEach((c) => {
      totalGmv += c.total_spend;
      totalClv += c.predicted_clv;
      churnSum += c.churn_probability;
    });

    const count = filtered.length;
    const kpis = {
      matching_profiles: count,
      total_gmv: parseFloat(totalGmv.toFixed(2)),
      avg_clv: count > 0 ? parseFloat((totalClv / count).toFixed(2)) : 0,
      avg_churn_risk: count > 0 ? parseFloat((churnSum / count).toFixed(4)) : 0,
    };

    // Histograms
    // 1. Spend histogram bins
    const spendBins = [];
    const spendMax = 1000;
    const spendStep = 100;
    for (let s = 0; s < spendMax; s += spendStep) {
      spendBins.push({ range: `R$ ${s} - R$ ${s + spendStep}`, min: s, max: s + spendStep, count: 0 });
    }
    spendBins.push({ range: `> R$ ${spendMax}`, min: spendMax, max: Infinity, count: 0 });

    // 2. Recency histogram bins
    const recencyBins = [
      { range: '0 - 60d', min: 0, max: 60, count: 0 },
      { range: '61 - 120d', min: 61, max: 120, count: 0 },
      { range: '121 - 180d', min: 121, max: 180, count: 0 },
      { range: '181 - 365d', min: 181, max: 365, count: 0 },
      { range: '> 365d', min: 366, max: Infinity, count: 0 },
    ];

    filtered.forEach((c) => {
      const sBin = spendBins.find((b) => c.total_spend >= b.min && c.total_spend < b.max);
      if (sBin) sBin.count++;

      const rBin = recencyBins.find((b) => c.recency_days >= b.min && c.recency_days <= b.max);
      if (rBin) rBin.count++;
    });

    const page = parseInt(req.query.page || 1, 10);
    const limit = parseInt(req.query.limit || 25, 10);
    const startIndex = (page - 1) * limit;
    const paginated = filtered.slice(startIndex, startIndex + limit);

    res.json({
      success: true,
      data: {
        kpis,
        spend_distribution: spendBins,
        recency_distribution: recencyBins,
        customers: paginated,
        pagination: {
          total: count,
          page,
          limit,
          total_pages: Math.ceil(count / limit),
        },
      },
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getAnalyticsExplorer,
};
