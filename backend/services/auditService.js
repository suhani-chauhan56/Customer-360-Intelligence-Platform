const AuditEvent = require('../models/AuditEvent');

const transientBuffer = [];

const recordAuditEvent = async ({
  action,
  resource_type,
  resource_id = null,
  user_id = 'usr_analyst',
  org_id = 'default_org',
  details = null,
  status = 'success',
  ip_address = '127.0.0.1',
}) => {
  const event = {
    action,
    resource_type,
    resource_id,
    user_id,
    org_id,
    details: typeof details === 'object' ? JSON.stringify(details) : String(details || ''),
    status,
    ip_address,
    timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
  };

  transientBuffer.unshift(event);
  if (transientBuffer.length > 500) {
    transientBuffer.pop();
  }

  // Persist to MongoDB if connected
  try {
    if (AuditEvent.db && AuditEvent.db.readyState === 1) {
      await AuditEvent.create({
        action,
        resource_type,
        resource_id,
        user_id,
        org_id,
        details: event.details,
        status,
        ip_address,
      });
    }
  } catch (err) {
    // Silent catch for graceful transient buffer fallback
  }

  return event;
};

const getRecentAuditEvents = async (limit = 50) => {
  try {
    if (AuditEvent.db && AuditEvent.db.readyState === 1) {
      const dbEvents = await AuditEvent.find().sort({ createdAt: -1 }).limit(limit).lean();
      if (dbEvents && dbEvents.length > 0) {
        return dbEvents.map((e) => ({
          action: e.action,
          resource_type: e.resource_type,
          resource_id: e.resource_id,
          user_id: e.user_id,
          org_id: e.org_id,
          details: e.details,
          status: e.status,
          ip_address: e.ip_address,
          timestamp: new Date(e.createdAt || e.timestamp).toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
        }));
      }
    }
  } catch (err) {
    // fallback
  }

  return transientBuffer.slice(0, limit);
};

module.exports = {
  recordAuditEvent,
  getRecentAuditEvents,
};
