import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
export const ROOT_DIR = path.resolve(__dirname, '..');
export const DATA_PROCESSED_DIR = path.resolve(ROOT_DIR, 'data', 'processed');
export const DATA_RAW_DIR = path.resolve(ROOT_DIR, 'data', 'raw');
export const MODELS_DIR = path.resolve(ROOT_DIR, 'models');

// In-memory data cache
let cachedCustomers = null;
let customerIndex = new Map();
let cachedOrders = null;
let cachedRecommendations = null;
let cachedFeatureImportance = null;
let cachedReviews = null;

/**
 * Fast CSV line parser handling quotes and commas
 */
function parseCSV(content, maxRows = Infinity) {
  const lines = content.split(/\r?\n/);
  if (lines.length === 0 || !lines[0].trim()) return [];

  const headers = parseCSVLine(lines[0]);
  const records = [];

  for (let i = 1; i < lines.length && records.length < maxRows; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const values = parseCSVLine(line);
    if (values.length === 0) continue;

    const record = {};
    for (let j = 0; j < headers.length; j++) {
      const header = headers[j];
      const val = values[j] !== undefined ? values[j] : '';
      // Parse numbers if applicable
      if (val === '' || val === null || val === undefined) {
        record[header] = null;
      } else if (!isNaN(val) && val.trim() !== '' && !val.includes('-') && !val.includes(':')) {
        record[header] = Number(val);
      } else {
        record[header] = val;
      }
    }
    records.push(record);
  }
  return records;
}

function parseCSVLine(line) {
  const values = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"' || char === "'") {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      values.push(current.trim().replace(/^["']|["']$/g, ''));
      current = '';
    } else {
      current += char;
    }
  }
  values.push(current.trim().replace(/^["']|["']$/g, ''));
  return values;
}

/**
 * Load Customer 360 Features
 */
export function getCustomers() {
  if (cachedCustomers) return cachedCustomers;

  const filePath = path.join(DATA_PROCESSED_DIR, 'customer_360_features.csv');
  if (!fs.existsSync(filePath)) {
    console.warn(`Customer dataset not found at ${filePath}`);
    return [];
  }

  console.log('Loading customer_360_features.csv into memory...');
  const fileContent = fs.readFileSync(filePath, 'utf-8');
  cachedCustomers = parseCSV(fileContent);

  // Build hash index for O(1) customer lookups
  customerIndex.clear();
  for (const cust of cachedCustomers) {
    if (cust.customer_id) {
      customerIndex.set(String(cust.customer_id), cust);
    }
  }

  console.log(`Loaded ${cachedCustomers.length} customer profiles.`);
  return cachedCustomers;
}

/**
 * Get Single Customer by ID
 */
export function getCustomerById(customerId) {
  if (!cachedCustomers) {
    getCustomers();
  }
  return customerIndex.get(String(customerId)) || null;
}

/**
 * Load Fact Orders
 */
export function getFactOrders(limit = 10000) {
  if (cachedOrders) return cachedOrders;

  const filePath = path.join(DATA_PROCESSED_DIR, 'fact_orders.csv');
  if (!fs.existsSync(filePath)) {
    return [];
  }

  const fileContent = fs.readFileSync(filePath, 'utf-8');
  cachedOrders = parseCSV(fileContent, limit);
  return cachedOrders;
}

/**
 * Get Orders for Customer
 */
export function getOrdersByCustomerId(customerId) {
  const filePath = path.join(DATA_PROCESSED_DIR, 'fact_orders.csv');
  if (!fs.existsSync(filePath)) return [];

  // Stream/scan for matching customer ID
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split(/\r?\n/);
  if (lines.length <= 1) return [];

  const headers = parseCSVLine(lines[0]);
  const custIdIdx = headers.indexOf('customer_id');
  if (custIdIdx === -1) return [];

  const matched = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    if (line.includes(customerId)) {
      const values = parseCSVLine(line);
      if (values[custIdIdx] === customerId) {
        const order = {};
        headers.forEach((h, idx) => {
          order[h] = values[idx];
        });
        matched.push(order);
      }
    }
  }
  return matched;
}

/**
 * Load Precomputed Next-Best Recommendations
 */
export function getRecommendations() {
  if (cachedRecommendations) return cachedRecommendations;

  const filePath = path.join(DATA_PROCESSED_DIR, 'recommendations.csv');
  if (!fs.existsSync(filePath)) return [];

  const content = fs.readFileSync(filePath, 'utf-8');
  cachedRecommendations = parseCSV(content, 20000);
  return cachedRecommendations;
}

export function getRecommendationsByCustomerId(customerId) {
  const filePath = path.join(DATA_PROCESSED_DIR, 'recommendations.csv');
  if (!fs.existsSync(filePath)) return [];

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split(/\r?\n/);
  if (lines.length <= 1) return [];

  const headers = parseCSVLine(lines[0]);
  const custIdIdx = headers.indexOf('customer_id');
  if (custIdIdx === -1) return [];

  const recs = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    if (line.includes(customerId)) {
      const values = parseCSVLine(line);
      if (values[custIdIdx] === customerId) {
        const rec = {};
        headers.forEach((h, idx) => {
          rec[h] = values[idx];
        });
        recs.push(rec);
      }
    }
  }
  return recs;
}

/**
 * Load Model Feature Importance
 */
export function getFeatureImportance() {
  if (cachedFeatureImportance) return cachedFeatureImportance;

  const filePath = path.join(DATA_PROCESSED_DIR, 'model_feature_importance.csv');
  if (!fs.existsSync(filePath)) {
    return [
      { feature: 'recency_days', churn_importance: 0.6132, clv_importance: 0.0329 },
      { feature: 'frequency', churn_importance: 0.1262, clv_importance: 0.0265 },
      { feature: 'monetary', churn_importance: 0.0994, clv_importance: 0.7268 },
      { feature: 'number_of_products', churn_importance: 0.0558, clv_importance: 0.0048 },
      { feature: 'customer_age_days', churn_importance: 0.0533, clv_importance: 0.0075 },
      { feature: 'avg_order_value', churn_importance: 0.0520, clv_importance: 0.2015 },
    ];
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  cachedFeatureImportance = parseCSV(content);
  return cachedFeatureImportance;
}

/**
 * Load Reviews dataset for Sentiment Analytics
 */
export function getReviewsDataset(limit = 15000) {
  if (cachedReviews) return cachedReviews;

  let filePath = path.join(DATA_RAW_DIR, 'olist_order_reviews_dataset.csv');
  if (!fs.existsSync(filePath)) {
    filePath = path.join(ROOT_DIR, 'data', 'raw', 'olist_order_reviews_dataset.csv');
  }

  if (!fs.existsSync(filePath)) {
    return [];
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  cachedReviews = parseCSV(content, limit);
  return cachedReviews;
}
