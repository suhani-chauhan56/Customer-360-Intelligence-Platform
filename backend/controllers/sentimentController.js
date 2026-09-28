import { getCustomers } from '../services/dataStore.js';
import { computeSentimentIntelligence } from '../services/analyticsService.js';

export function getSentimentOverview(req, res) {
  try {
    const customers = getCustomers();
    const sentimentData = computeSentimentIntelligence(customers);

    return res.status(200).json({
      success: true,
      data: sentimentData,
    });
  } catch (error) {
    console.error('Error in getSentimentOverview:', error);
    return res.status(500).json({ success: false, message: error.message });
  }
}
