const REQUIRED_CUSTOMER_COLUMNS = [
  'customer_id',
  'total_spend',
  'total_orders',
  'avg_order_value',
  'recency_days',
  'frequency',
  'monetary',
  'rfm_segment',
  'churn_probability',
  'predicted_clv',
];

const runDataQualityAudit = (customers) => {
  const totalRows = customers.length;
  if (totalRows === 0) {
    return {
      is_healthy: false,
      quality_score_pct: 0.0,
      total_records: 0,
      total_columns: 0,
      duplicate_customer_ids: 0,
      null_customer_ids: 0,
      negative_spend_records: 0,
      invalid_churn_probabilities: 0,
      missing_required_columns: REQUIRED_CUSTOMER_COLUMNS,
      checks: [],
    };
  }

  const first = customers[0];
  const totalCols = Object.keys(first).length;
  const missingRequired = REQUIRED_CUSTOMER_COLUMNS.filter((c) => !(c in first));
  const checkColsPass = missingRequired.length === 0;

  const idSet = new Set();
  let dupIds = 0;
  let nullIds = 0;
  let negSpend = 0;
  let invalidChurn = 0;
  let invalidOrders = 0;

  customers.forEach((c) => {
    if (!c.customer_id) nullIds++;
    else if (idSet.has(c.customer_id)) dupIds++;
    else idSet.add(c.customer_id);

    if (c.total_spend < 0) negSpend++;
    if (c.churn_probability < 0.0 || c.churn_probability > 1.0) invalidChurn++;
    if (c.total_orders < 1) invalidOrders++;
  });

  const checkDupPass = dupIds === 0;
  const checkNullPass = nullIds === 0;
  const checkSpendPass = negSpend === 0;
  const checkChurnPass = invalidChurn === 0;
  const checkOrdersPass = invalidOrders === 0;

  const checks = [
    {
      Test: 'Required Schema Columns',
      Status: checkColsPass ? 'Passed 🟢' : 'Failed 🔴',
      Detail: `${REQUIRED_CUSTOMER_COLUMNS.length - missingRequired.length}/${REQUIRED_CUSTOMER_COLUMNS.length} required columns present`,
    },
    {
      Test: 'Customer ID Uniqueness',
      Status: checkDupPass ? 'Passed 🟢' : 'Failed 🔴',
      Detail: `${dupIds.toLocaleString()} duplicate customer ID records`,
    },
    {
      Test: 'Customer ID Completeness',
      Status: checkNullPass ? 'Passed 🟢' : 'Failed 🔴',
      Detail: `${nullIds.toLocaleString()} missing/null ID records`,
    },
    {
      Test: 'Non-Negative Revenue',
      Status: checkSpendPass ? 'Passed 🟢' : 'Failed 🔴',
      Detail: `${negSpend.toLocaleString()} negative spend anomalies`,
    },
    {
      Test: 'Calibrated Churn Range',
      Status: checkChurnPass ? 'Passed 🟢' : 'Failed 🔴',
      Detail: `${invalidChurn.toLocaleString()} out-of-range probabilities`,
    },
    {
      Test: 'Order Count Sanity',
      Status: checkOrdersPass ? 'Passed 🟢' : 'Failed 🔴',
      Detail: `${invalidOrders.toLocaleString()} non-positive order records`,
    },
  ];

  const passedCount = [checkColsPass, checkDupPass, checkNullPass, checkSpendPass, checkChurnPass, checkOrdersPass].filter(Boolean).length;
  const qualityScore = (passedCount / 6.0) * 100.0;

  return {
    is_healthy: qualityScore >= 99.0,
    quality_score_pct: parseFloat(qualityScore.toFixed(1)),
    total_records: totalRows,
    total_columns: totalCols,
    duplicate_customer_ids: dupIds,
    null_customer_ids: nullIds,
    negative_spend_records: negSpend,
    invalid_churn_probabilities: invalidChurn,
    missing_required_columns: missingRequired,
    checks,
  };
};

const getFieldCompletenessStats = (customers) => {
  if (customers.length === 0) return [];
  const keys = Object.keys(customers[0]);
  const total = customers.length;

  return keys.map((key) => {
    let nullCount = 0;
    customers.forEach((c) => {
      if (c[key] === null || c[key] === undefined || c[key] === '') nullCount++;
    });
    const nonNull = total - nullCount;
    const completeness = (nonNull / total) * 100;

    return {
      'Attribute Field': key,
      'Data Type': typeof customers[0][key],
      'Non-Null Records': nonNull.toLocaleString(),
      'Completeness %': `${completeness.toFixed(1)}%`,
      'Missing / Null Count': nullCount.toLocaleString(),
      Status: nullCount === 0 ? 'Complete 🟢' : 'Contains Nulls 🟡',
    };
  });
};

const getDataLineageSummary = () => {
  return [
    {
      Stage: '1. Raw Order Records',
      'Source File': 'olist_orders_dataset.csv',
      'Raw Volume': '99,441 orders',
      Processing: 'Filtered out canceled/unavailable orders; extracted purchase timestamps',
    },
    {
      Stage: '2. Raw Order Items',
      'Source File': 'olist_order_items_dataset.csv',
      'Raw Volume': '112,650 items',
      Processing: 'Aggregated item prices and freight values per canonical customer',
    },
    {
      Stage: '3. Raw Customer Registry',
      'Source File': 'olist_customers_dataset.csv',
      'Raw Volume': '99,441 records',
      Processing: 'Mapped source customer IDs to canonical unique customer ID entities',
    },
    {
      Stage: '4. Raw Review Ratings',
      'Source File': 'olist_order_reviews_dataset.csv',
      'Raw Volume': '104,721 reviews',
      Processing: 'Calculated average CSAT rating, low rating counts, and sentiment polarity',
    },
    {
      Stage: '5. Raw Payment Facts',
      'Source File': 'olist_order_payments_dataset.csv',
      'Raw Volume': '103,886 payments',
      Processing: 'Consolidated payment methods, installments, and gross transaction values',
    },
    {
      Stage: '6. Canonical Feature Store',
      'Source File': 'customer_360_features.csv',
      'Processed Volume': '94,983 profiles',
      Processing: 'Engineered RFM quintiles, XGBoost churn probabilities, and 12M forward CLV',
    },
  ];
};

const getModelRegistryStatus = () => {
  return [
    {
      'Model Name': 'Churn Propensity Classifier',
      Artifact: 'churn_model.pkl',
      Version: '3.0.0',
      Algorithm: 'XGBoost Classifier',
      Status: 'Ready 🟢',
      'File Size (KB)': 142.8,
    },
    {
      'Model Name': '12-Month CLV Regressor',
      Artifact: 'clv_model.pkl',
      Version: '2.1.0',
      Algorithm: 'Ridge / XGBoost Regressor',
      Status: 'Ready 🟢',
      'File Size (KB)': 86.4,
    },
    {
      'Model Name': 'Behavioral Cluster Pipeline',
      Artifact: 'segment_model.pkl',
      Version: '1.4.0',
      Algorithm: 'K-Means + Standard Scaler',
      Status: 'Ready 🟢',
      'File Size (KB)': 34.2,
    },
    {
      'Model Name': 'NLP Review Sentiment Classifier',
      Artifact: 'sentiment_model.pkl',
      Version: '1.0.0',
      Algorithm: 'TF-IDF + Logistic Regression',
      Status: 'Ready 🟢',
      'File Size (KB)': 512.0,
    },
  ];
};

module.exports = {
  runDataQualityAudit,
  getFieldCompletenessStats,
  getDataLineageSummary,
  getModelRegistryStatus,
};
