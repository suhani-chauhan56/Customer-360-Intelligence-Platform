const groundedAiService = require('../services/groundedAiService');
const auditService = require('../services/auditService');

const askGroundedQuestion = async (req, res, next) => {
  try {
    const { query, question, customer_id } = req.body;
    const activeQuery = query || question;

    if (!activeQuery) {
      return res.status(400).json({
        success: false,
        message: 'Query is required.',
      });
    }

    const answer = groundedAiService.processGroundedQuery(activeQuery, customer_id);

    // Record compliance audit
    await auditService.recordAuditEvent({
      action: 'grounded_ai_query',
      resource_type: 'analytics_query',
      resource_id: answer.intent,
      details: { query, intent: answer.intent },
      ip_address: req.ip,
    });

    res.json({
      success: true,
      data: answer,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  askGroundedQuestion,
};
