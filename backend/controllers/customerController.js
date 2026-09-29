const dataService = require('../services/dataService');
const customerService = require('../services/customerService');
const recommendationService = require('../services/recommendationService');

const getCustomersList = async (req, res, next) => {
  try {
    const filters = {
      segment: req.query.segment || 'All',
      risk_level: req.query.risk_level || 'All',
      state: req.query.state || 'All',
      clv_band: req.query.clv_band || 'All',
      recency_filter: req.query.recency_filter || 'All',
      search_query: req.query.search_query || '',
    };

    const preset = req.query.preset;
    let list = dataService.getCustomers(filters);

    if (preset === 'Champions & VIPs') {
      list = list.filter((c) => c.rfm_segment === 'Champions');
    } else if (preset === 'At Risk High Spenders') {
      list = list.filter((c) => c.churn_probability >= 0.65 && c.total_spend >= 200);
    } else if (preset === 'Recent Active Buyers') {
      list = list.filter((c) => c.recency_days <= 60);
    } else if (preset === 'Multi-Order Repeat Buyers') {
      list = list.filter((c) => c.total_orders > 1);
    }

    const page = parseInt(req.query.page || 1, 10);
    const limit = parseInt(req.query.limit || 25, 10);
    const sortBy = req.query.sort_by || 'total_spend';
    const sortOrder = req.query.sort_order === 'asc' ? 1 : -1;

    const sorted = [...list].sort((a, b) => {
      const aVal = a[sortBy] !== undefined ? a[sortBy] : 0;
      const bVal = b[sortBy] !== undefined ? b[sortBy] : 0;
      return (aVal > bVal ? 1 : aVal < bVal ? -1 : 0) * sortOrder;
    });

    const startIndex = (page - 1) * limit;
    const paginated = sorted.slice(startIndex, startIndex + limit);

    res.json({
      success: true,
      data: paginated,
      pagination: {
        total: list.length,
        page,
        limit,
        total_pages: Math.ceil(list.length / limit),
      },
    });
  } catch (error) {
    next(error);
  }
};

const getCustomerDetails = async (req, res, next) => {
  try {
    const { id } = req.params;
    const profile = dataService.getCustomerById(id);

    if (!profile) {
      return res.status(404).json({
        success: false,
        message: `Customer record with ID '${id}' was not found.`,
      });
    }

    const health = customerService.computeCustomerHealth(profile);
    const lifecycle = customerService.deriveLifecycleStages(profile);
    const riskDiagnostics = customerService.diagnoseCustomerRiskFactors(profile);
    const rfmExplanation = customerService.explainRfmSegment(profile);
    const recommendation = recommendationService.generateCustomerRecommendation(profile);

    const orders = dataService.getOrdersForCustomer(id);
    const orderIds = orders.map((o) => o.order_id);
    const payments = dataService.getPaymentsForOrders(orderIds);
    const reviews = dataService.getReviewsForOrders(orderIds);
    const categoryRecs = dataService.getRecommendationsForCustomer(id);

    res.json({
      success: true,
      data: {
        profile,
        health,
        lifecycle,
        risk_diagnostics: riskDiagnostics,
        rfm_explanation: rfmExplanation,
        recommendation,
        orders,
        payments,
        reviews,
        category_recommendations: categoryRecs,
      },
    });
  } catch (error) {
    next(error);
  }
};

const getCustomerPdfDossier = async (req, res, next) => {
  try {
    const { id } = req.params;
    const profile = dataService.getCustomerById(id);

    if (!profile) {
      return res.status(404).json({
        success: false,
        message: `Customer record with ID '${id}' was not found.`,
      });
    }

    const health = customerService.computeCustomerHealth(profile);
    const riskDiagnostics = customerService.diagnoseCustomerRiskFactors(profile);
    const recommendation = recommendationService.generateCustomerRecommendation(profile);

    // Return structured dossier metadata for immediate client download / rendering
    res.json({
      success: true,
      data: {
        dossier_title: 'CustomerAtlas — Unified Customer 360 Dossier',
        generated_at: new Date().toISOString(),
        customer_id: profile.customer_id,
        summary_attributes: {
          'Customer ID': profile.customer_id,
          'Location': `${profile.city}, ${profile.state}`,
          'RFM Segment': profile.rfm_segment,
          'Behavior Cluster': profile.cluster_segment,
          'Favorite Category': profile.favorite_category,
          'Total Lifetime Spend': `R$ ${profile.total_spend.toFixed(2)}`,
          'Total Orders Placed': `${profile.total_orders}`,
          'Average Order Value': `R$ ${profile.avg_order_value.toFixed(2)}`,
          'Recency (Days Inactive)': `${Math.round(profile.recency_days)} days`,
          '12-Month CLV Proxy': `R$ ${profile.predicted_clv.toFixed(2)}`,
          'Churn Propensity': `${(profile.churn_probability * 100).toFixed(1)}%`,
          'Health Score': `${health.total_score} / 100 (${health.health_tier})`,
          'Risk Level': riskDiagnostics.risk_level,
          'Recommended Action': recommendation.action_type,
          'Action Strategy Detail': recommendation.description,
        },
      },
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getCustomersList,
  getCustomerDetails,
  getCustomerPdfDossier,
};
