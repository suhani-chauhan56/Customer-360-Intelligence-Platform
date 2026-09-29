const dataService = require('../services/dataService');
const dataQualityService = require('../services/dataQualityService');
const driftService = require('../services/driftService');
const auditService = require('../services/auditService');

const getDataQualityOverview = async (req, res, next) => {
  try {
    const customers = dataService.getCustomers();
    const qualityAudit = dataQualityService.runDataQualityAudit(customers);
    const fieldCompleteness = dataQualityService.getFieldCompletenessStats(customers);
    const dataLineage = dataQualityService.getDataLineageSummary();
    const modelRegistry = dataQualityService.getModelRegistryStatus();

    // Drift audit between baseline (>180d inactive) vs current (<=180d active)
    const baseline = customers.filter((c) => c.recency_days > 180);
    const current = customers.filter((c) => c.recency_days <= 180);
    const driftReport = driftService.runFeatureDriftAudit(baseline, current);

    const recentAuditLogs = await auditService.getRecentAuditEvents(30);

    res.json({
      success: true,
      data: {
        quality_kpis: {
          data_quality_score: qualityAudit.quality_score_pct,
          is_healthy: qualityAudit.is_healthy,
          canonical_profiles: customers.length,
          total_attributes: qualityAudit.total_columns,
          models_ready: `${modelRegistry.filter((m) => m.Status.includes('Ready')).length} / ${modelRegistry.length}`,
        },
        integrity_checks: qualityAudit.checks,
        field_completeness: fieldCompleteness,
        data_lineage: dataLineage,
        drift_monitoring: driftReport,
        model_registry: modelRegistry,
        compliance_audit_logs: recentAuditLogs,
      },
    });
  } catch (error) {
    next(error);
  }
};

const recordAudit = async (req, res, next) => {
  try {
    const { action, resource_type, resource_id, details, user_id } = req.body;
    const event = await auditService.recordAuditEvent({
      action: action || 'client_action',
      resource_type: resource_type || 'user_interaction',
      resource_id,
      user_id: user_id || 'usr_analyst',
      details,
      ip_address: req.ip,
    });

    res.json({
      success: true,
      data: event,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getDataQualityOverview,
  recordAudit,
};
