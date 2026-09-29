const mongoose = require('mongoose');

const AuditEventSchema = new mongoose.Schema(
  {
    action: { type: String, required: true },
    resource_type: { type: String, required: true },
    resource_id: { type: String },
    user_id: { type: String, default: 'usr_analyst' },
    org_id: { type: String, default: 'default_org' },
    details: { type: String },
    status: { type: String, default: 'success' },
    ip_address: { type: String, default: '127.0.0.1' },
    timestamp: { type: Date, default: Date.now },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model('AuditEvent', AuditEventSchema);
