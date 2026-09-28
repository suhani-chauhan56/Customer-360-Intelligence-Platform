import { getCustomers } from '../services/dataStore.js';
import { computeExecutiveKPIs } from '../services/analyticsService.js';

export function getOverview(req, res) {
  try {
    const customers = getCustomers();
    const data = computeExecutiveKPIs(customers);
    return res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    console.error('Error in getOverview:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to compute executive overview',
      error: error.message,
    });
  }
}
