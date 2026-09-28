import { getCustomers, getCustomerById, getOrdersByCustomerId, getRecommendationsByCustomerId } from '../services/dataStore.js';
import {
  calculateHealthScore,
  deriveLifecycleStages,
  diagnoseCustomerRisk,
  generateCustomerRecommendation,
} from '../services/analyticsService.js';

export function getCustomersList(req, res) {
  try {
    const {
      search = '',
      segment = 'All',
      risk = 'All',
      state = 'All',
      clvBand = 'All',
      recency = 'All',
      page = 1,
      limit = 50,
      sortBy = 'total_spend',
      sortOrder = 'desc',
    } = req.query;

    let customers = getCustomers();

    // Search filter (customer_id, city, state)
    if (search && search.trim()) {
      const q = search.trim().toLowerCase();
      customers = customers.filter(c =>
        (c.customer_id && String(c.customer_id).toLowerCase().includes(q)) ||
        (c.city && String(c.city).toLowerCase().includes(q)) ||
        (c.state && String(c.state).toLowerCase().includes(q))
      );
    }

    // Segment filter
    if (segment && segment !== 'All') {
      customers = customers.filter(c => c.rfm_segment === segment);
    }

    // Risk level filter
    if (risk && risk !== 'All') {
      if (risk.includes('High')) {
        customers = customers.filter(c => Number(c.churn_probability) >= 0.65);
      } else if (risk.includes('Medium')) {
        customers = customers.filter(c => Number(c.churn_probability) >= 0.35 && Number(c.churn_probability) < 0.65);
      } else if (risk.includes('Low')) {
        customers = customers.filter(c => Number(c.churn_probability) < 0.35);
      }
    }

    // State filter
    if (state && state !== 'All') {
      customers = customers.filter(c => (c.state || '').toUpperCase() === state.toUpperCase());
    }

    // CLV Band filter
    if (clvBand && clvBand !== 'All') {
      customers = customers.filter(c => c.clv_band === clvBand);
    }

    // Recency filter
    if (recency && recency !== 'All') {
      if (recency.includes('<90') || recency.includes('Recent')) {
        customers = customers.filter(c => Number(c.recency_days) < 90);
      } else if (recency.includes('90-180') || recency.includes('Active')) {
        customers = customers.filter(c => Number(c.recency_days) >= 90 && Number(c.recency_days) <= 180);
      } else if (recency.includes('181-365') || recency.includes('Lapsed')) {
        customers = customers.filter(c => Number(c.recency_days) > 180 && Number(c.recency_days) <= 365);
      } else if (recency.includes('>365') || recency.includes('Inactive')) {
        customers = customers.filter(c => Number(c.recency_days) > 365);
      }
    }

    const totalMatching = customers.length;

    // Sorting
    const sorted = [...customers].sort((a, b) => {
      let valA = a[sortBy];
      let valB = b[sortBy];

      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();

      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    // Pagination
    const pageNum = Math.max(1, parseInt(page, 10) || 1);
    const limitNum = Math.min(200, Math.max(1, parseInt(limit, 10) || 50));
    const startIndex = (pageNum - 1) * limitNum;
    const paginated = sorted.slice(startIndex, startIndex + limitNum);

    return res.status(200).json({
      success: true,
      pagination: {
        total: totalMatching,
        page: pageNum,
        limit: limitNum,
        totalPages: Math.ceil(totalMatching / limitNum),
      },
      data: paginated,
    });
  } catch (error) {
    console.error('Error in getCustomersList:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to retrieve customers',
      error: error.message,
    });
  }
}

export function getCustomerDetails(req, res) {
  try {
    const { id } = req.params;
    if (!id) {
      return res.status(400).json({ success: false, message: 'Customer ID is required' });
    }

    const profile = getCustomerById(id);
    if (!profile) {
      return res.status(404).json({ success: false, message: `Customer profile not found for ID: ${id}` });
    }

    const health = calculateHealthScore(profile);
    const lifecycle = deriveLifecycleStages(profile);
    const riskDiagnostics = diagnoseCustomerRisk(profile);
    const nextBestAction = generateCustomerRecommendation(profile);
    const orders = getOrdersByCustomerId(id);
    const categoryRecommendations = getRecommendationsByCustomerId(id);

    // RFM explanation
    const rScore = Number(profile.r_score) || 1;
    const fScore = Number(profile.f_score) || 1;
    const mScore = Number(profile.m_score) || 1;

    const rfmExplanation = {
      segment: profile.rfm_segment || 'Regular Customers',
      code: `R:${rScore} | F:${fScore} | M:${mScore}`,
      factors: [
        `Recency Score ${rScore}/5 (${profile.recency_days} days inactive)`,
        `Frequency Score ${fScore}/5 (${profile.total_orders} orders placed)`,
        `Monetary Score ${mScore}/5 (R$ ${Number(profile.total_spend || 0).toFixed(2)} lifetime spend)`,
      ],
    };

    return res.status(200).json({
      success: true,
      data: {
        profile,
        health,
        lifecycle,
        riskDiagnostics,
        nextBestAction,
        rfmExplanation,
        orders,
        categoryRecommendations,
      },
    });
  } catch (error) {
    console.error('Error in getCustomerDetails:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to retrieve customer dossier',
      error: error.message,
    });
  }
}

export function getCustomerOrders(req, res) {
  try {
    const { id } = req.params;
    const orders = getOrdersByCustomerId(id);
    return res.status(200).json({ success: true, data: orders });
  } catch (error) {
    return res.status(500).json({ success: false, message: error.message });
  }
}
