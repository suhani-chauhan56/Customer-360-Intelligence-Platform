import { getCustomers } from '../services/dataStore.js';
import { computeCLVOverview, simulateCLV } from '../services/analyticsService.js';

export function getCLVOverview(req, res) {
  try {
    const customers = getCustomers();
    const clvData = computeCLVOverview(customers);

    return res.status(200).json({
      success: true,
      data: clvData,
    });
  } catch (error) {
    console.error('Error in getCLVOverview:', error);
    return res.status(500).json({ success: false, message: error.message });
  }
}

export function handleCLVSimulation(req, res) {
  try {
    const {
      recency_days = 90,
      frequency = 2,
      monetary = 250,
      avg_order_value = 125,
      number_of_products = 2,
      customer_age_days = 180,
    } = req.body;

    const result = simulateCLV(recency_days, frequency, monetary, avg_order_value, number_of_products, customer_age_days);
    return res.status(200).json({ success: true, data: result });
  } catch (error) {
    return res.status(500).json({ success: false, message: error.message });
  }
}
