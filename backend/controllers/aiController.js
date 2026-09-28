import { executeGroundedAIQuery } from '../services/analyticsService.js';

export function handleGroundedAIQuery(req, res) {
  try {
    const { query, customerId } = req.body;
    const answer = executeGroundedAIQuery(query, customerId);

    return res.status(200).json({
      success: true,
      data: answer,
    });
  } catch (error) {
    console.error('Error in handleGroundedAIQuery:', error);
    return res.status(500).json({
      success: false,
      message: 'Failed to process AI query',
      error: error.message,
    });
  }
}
