const mongoose = require('mongoose');

const CustomerSchema = new mongoose.Schema(
  {
    customer_id: { type: String, required: true, unique: true, index: true },
    total_spend: { type: Number, default: 0, index: true },
    total_orders: { type: Number, default: 1 },
    avg_order_value: { type: Number, default: 0 },
    recency_days: { type: Number, default: 0, index: true },
    frequency: { type: Number, default: 1 },
    monetary: { type: Number, default: 0 },
    rfm_segment: { type: String, default: 'Regular Customers', index: true },
    r_score: { type: Number, default: 1 },
    f_score: { type: Number, default: 1 },
    m_score: { type: Number, default: 1 },
    rfm_score: { type: Number, default: 111 },
    predicted_clv: { type: Number, default: 0, index: true },
    clv_band: { type: String, default: 'Bronze', index: true },
    churn_probability: { type: Number, default: 0.5, index: true },
    priority_score: { type: Number, default: 0, index: true },
    avg_review_score: { type: Number, default: 5.0 },
    low_rating_count: { type: Number, default: 0 },
    web_engagement_score: { type: Number, default: 0 },
    sessions: { type: Number, default: 0 },
    views: { type: Number, default: 0 },
    cart_additions: { type: Number, default: 0 },
    campaign_conversions: { type: Number, default: 0 },
    customer_age_days: { type: Number, default: 1 },
    favorite_category: { type: String, default: 'General' },
    city: { type: String, default: 'Unknown' },
    state: { type: String, default: 'SP', index: true },
    cluster_segment: { type: String, default: 'Standard' },
    first_purchase_date: { type: Date },
    last_purchase_date: { type: Date },
    predicted_90d_revenue: { type: Number, default: 0 },
  },
  {
    timestamps: true,
  }
);

// Helpful Compound Indexes for Enterprise Analytics Filtering
CustomerSchema.index({ rfm_segment: 1, churn_probability: 1 });
CustomerSchema.index({ state: 1, total_spend: -1 });
CustomerSchema.index({ predicted_clv: -1, churn_probability: -1 });

module.exports = mongoose.model('Customer', CustomerSchema);
