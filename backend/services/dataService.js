const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

const ROOT_DIR = path.resolve(__dirname, '../../');
const DATA_PROCESSED_DIR = path.join(ROOT_DIR, 'data', 'processed');
const DATA_RAW_DIR = path.join(ROOT_DIR, 'data', 'raw');

// In-memory feature cache
let customersCache = [];
let factOrdersCache = [];
let factPaymentsCache = [];
let recommendationsCache = [];
let reviewsCache = [];
let featureImportanceCache = [];
let isLoaded = false;

const loadCsvFile = (filePath) => {
  return new Promise((resolve) => {
    if (!fs.existsSync(filePath)) {
      console.warn(`[DataService] File not found: ${filePath}`);
      return resolve([]);
    }
    const results = [];
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (data) => results.push(data))
      .on('end', () => resolve(results))
      .on('error', (err) => {
        console.error(`[DataService] Error parsing CSV ${filePath}:`, err.message);
        resolve([]);
      });
  });
};

const initializeData = async () => {
  if (isLoaded) return;
  console.log('[DataService] Ingesting CSV datasets into memory store...');

  try {
    const rawCustomers = await loadCsvFile(path.join(DATA_PROCESSED_DIR, 'customer_360_features.csv'));
    customersCache = rawCustomers.map((c) => ({
      customer_id: String(c.customer_id || ''),
      total_spend: parseFloat(c.total_spend || 0) || 0,
      total_orders: parseInt(c.total_orders || 1, 10) || 1,
      avg_order_value: parseFloat(c.avg_order_value || 0) || 0,
      recency_days: parseFloat(c.recency_days || 0) || 0,
      frequency: parseFloat(c.frequency || 1) || 1,
      monetary: parseFloat(c.monetary || 0) || 0,
      rfm_segment: c.rfm_segment || 'Regular Customers',
      r_score: parseInt(c.r_score || 1, 10) || 1,
      f_score: parseInt(c.f_score || 1, 10) || 1,
      m_score: parseInt(c.m_score || 1, 10) || 1,
      rfm_score: parseInt(c.rfm_score || 111, 10) || 111,
      predicted_clv: parseFloat(c.predicted_clv || 0) || 0,
      clv_band: c.clv_band || 'Bronze',
      churn_probability: parseFloat(c.churn_probability || 0.5) || 0.5,
      priority_score: parseFloat(c.priority_score || 0) || 0,
      avg_review_score: parseFloat(c.avg_review_score || 5.0) || 5.0,
      low_rating_count: parseInt(c.low_rating_count || 0, 10) || 0,
      web_engagement_score: parseFloat(c.web_engagement_score || 0) || 0,
      sessions: parseFloat(c.sessions || 0) || 0,
      views: parseFloat(c.views || 0) || 0,
      cart_additions: parseFloat(c.cart_additions || 0) || 0,
      campaign_conversions: parseFloat(c.campaign_conversions || 0) || 0,
      customer_age_days: parseFloat(c.customer_age_days || 1) || 1,
      favorite_category: c.favorite_category || 'General',
      city: c.city || 'Unknown',
      state: (c.state || 'SP').toUpperCase(),
      cluster_segment: c.cluster_segment || 'Standard',
      first_purchase_date: c.first_purchase_date || null,
      last_purchase_date: c.last_purchase_date || null,
      predicted_90d_revenue: parseFloat(c.predicted_90d_revenue || 0) || 0,
      number_of_products: parseFloat(c.number_of_products || 1) || 1,
    }));

    // Calculate priority scores if missing
    if (customersCache.length > 0) {
      const sortedClv = [...customersCache].map((c) => c.predicted_clv).sort((a, b) => a - b);
      const p99Index = Math.floor(sortedClv.length * 0.99);
      const p99Clv = sortedClv[p99Index] || 1000;
      
      customersCache.forEach((c) => {
        if (!c.priority_score) {
          const normClv = Math.min(1.0, c.predicted_clv / Math.max(1, p99Clv));
          c.priority_score = parseFloat((c.churn_probability * normClv * 100).toFixed(1));
        }
      });
    }

    const rawOrders = await loadCsvFile(path.join(DATA_PROCESSED_DIR, 'fact_orders.csv'));
    factOrdersCache = rawOrders.map((o) => ({
      order_id: o.order_id,
      customer_id: o.customer_id,
      purchase_date: o.purchase_date,
      order_status: o.order_status,
      item_price: parseFloat(o.item_price || 0) || 0,
      freight_value: parseFloat(o.freight_value || 0) || 0,
      revenue: parseFloat(o.revenue || 0) || 0,
      month_year: o.purchase_date ? o.purchase_date.substring(0, 7) : '',
    }));

    const rawPayments = await loadCsvFile(path.join(DATA_PROCESSED_DIR, 'fact_payments.csv'));
    factPaymentsCache = rawPayments.map((p) => ({
      order_id: p.order_id,
      payment_type: p.payment_type || 'credit_card',
      payment_installments: parseInt(p.payment_installments || 1, 10) || 1,
      payment_value: parseFloat(p.payment_value || 0) || 0,
    }));

    const rawRecs = await loadCsvFile(path.join(DATA_PROCESSED_DIR, 'recommendations.csv'));
    recommendationsCache = rawRecs.map((r) => ({
      customer_id: r.customer_id,
      recommended_category: r.recommended_category,
      rank: parseInt(r.rank || 1, 10) || 1,
      reason: r.reason || 'Basket Co-occurrence Association',
      method: r.method || 'Market Basket Co-occurrence',
    }));

    const rawReviews = await loadCsvFile(path.join(DATA_RAW_DIR, 'olist_order_reviews_dataset.csv'));
    reviewsCache = rawReviews.map((rev) => {
      const score = parseInt(rev.review_score || 5, 10) || 5;
      let category = 'Neutral';
      if (score >= 4) category = 'Positive';
      else if (score <= 2) category = 'Negative';

      const polarityMap = { 5: 1.0, 4: 0.5, 3: 0.0, 2: -0.5, 1: -1.0 };
      const polarity = polarityMap[score] !== undefined ? polarityMap[score] : 0.0;
      const month = rev.review_creation_date ? rev.review_creation_date.substring(0, 7) : '';

      return {
        review_id: rev.review_id,
        order_id: rev.order_id,
        review_score: score,
        sentiment_category: category,
        sentiment_polarity: polarity,
        review_comment_title: rev.review_comment_title || '',
        review_comment_message: rev.review_comment_message || '',
        review_creation_date: rev.review_creation_date || '',
        review_month: month,
      };
    });

    const rawImportance = await loadCsvFile(path.join(DATA_PROCESSED_DIR, 'model_feature_importance.csv'));
    featureImportanceCache = rawImportance.map((f) => ({
      feature: f.feature,
      churn_importance: parseFloat(f.churn_importance || 0) || 0,
    }));

    isLoaded = true;
    console.log(`[DataService] Datasets ingested: ${customersCache.length} customers, ${factOrdersCache.length} orders, ${reviewsCache.length} reviews, ${recommendationsCache.length} recs.`);
  } catch (err) {
    console.error('[DataService] Error during dataset ingestion:', err);
  }
};

const getCustomers = (filters = {}) => {
  let list = customersCache;

  if (filters.segment && filters.segment !== 'All') {
    list = list.filter((c) => c.rfm_segment === filters.segment);
  }
  if (filters.risk_level && filters.risk_level !== 'All') {
    if (filters.risk_level === 'High Risk (>=65%)' || filters.risk_level === 'High Risk') {
      list = list.filter((c) => c.churn_probability >= 0.65);
    } else if (filters.risk_level === 'Medium Risk (35-65%)' || filters.risk_level === 'Medium Risk') {
      list = list.filter((c) => c.churn_probability >= 0.35 && c.churn_probability < 0.65);
    } else if (filters.risk_level === 'Low Risk (<35%)' || filters.risk_level === 'Low Risk') {
      list = list.filter((c) => c.churn_probability < 0.35);
    }
  }
  if (filters.state && filters.state !== 'All') {
    list = list.filter((c) => c.state === filters.state.toUpperCase());
  }
  if (filters.clv_band && filters.clv_band !== 'All') {
    list = list.filter((c) => c.clv_band === filters.clv_band);
  }
  if (filters.recency_filter && filters.recency_filter !== 'All') {
    if (filters.recency_filter === 'Recent (<90 days)') {
      list = list.filter((c) => c.recency_days < 90);
    } else if (filters.recency_filter === 'Active (90-180 days)') {
      list = list.filter((c) => c.recency_days >= 90 && c.recency_days <= 180);
    } else if (filters.recency_filter === 'Lapsed (181-365 days)') {
      list = list.filter((c) => c.recency_days > 180 && c.recency_days <= 365);
    } else if (filters.recency_filter === 'Inactive (>365 days)') {
      list = list.filter((c) => c.recency_days > 365);
    }
  }
  if (filters.search_query && filters.search_query.trim()) {
    const q = filters.search_query.trim().toLowerCase();
    list = list.filter(
      (c) =>
        c.customer_id.toLowerCase().includes(q) ||
        (c.city && c.city.toLowerCase().includes(q)) ||
        (c.favorite_category && c.favorite_category.toLowerCase().includes(q))
    );
  }

  return list;
};

const getCustomerById = (id) => {
  if (!id) return null;
  return customersCache.find((c) => c.customer_id === id) || null;
};

const getOrdersForCustomer = (customerId) => {
  return factOrdersCache.filter((o) => o.customer_id === customerId);
};

const getPaymentsForOrders = (orderIds) => {
  const set = new Set(orderIds);
  return factPaymentsCache.filter((p) => set.has(p.order_id));
};

const getReviewsForOrders = (orderIds) => {
  const set = new Set(orderIds);
  return reviewsCache.filter((r) => set.has(r.order_id));
};

const getRecommendationsForCustomer = (customerId) => {
  return recommendationsCache.filter((r) => r.customer_id === customerId);
};

const getAllReviews = () => reviewsCache;
const getAllOrders = () => factOrdersCache;
const getAllPayments = () => factPaymentsCache;
const getAllRecommendations = () => recommendationsCache;
const getFeatureImportance = () => featureImportanceCache;

module.exports = {
  initializeData,
  getCustomers,
  getCustomerById,
  getOrdersForCustomer,
  getPaymentsForOrders,
  getReviewsForOrders,
  getRecommendationsForCustomer,
  getAllReviews,
  getAllOrders,
  getAllPayments,
  getAllRecommendations,
  getFeatureImportance,
};
