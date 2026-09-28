import {
  OverviewData,
  Customer360Dossier,
  GroundedAnswer,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function fetchOverview(): Promise<OverviewData> {
  const res = await fetch(`${API_BASE}/dashboard/overview`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchCustomers(params: {
  search?: string;
  segment?: string;
  risk?: string;
  state?: string;
  clvBand?: string;
  recency?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '') {
      query.append(key, String(val));
    }
  });

  const res = await fetch(`${API_BASE}/customers?${query.toString()}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function fetchCustomerDossier(id: string): Promise<Customer360Dossier> {
  const res = await fetch(`${API_BASE}/customers/${id}`);
  if (!res.ok) throw new Error(`Customer ${id} not found`);
  const json = await res.json();
  return json.data;
}

export async function fetchSegmentsOverview() {
  const res = await fetch(`${API_BASE}/segments`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchSegmentComparison(segmentA: string, segmentB: string) {
  const res = await fetch(`${API_BASE}/segments/compare?segmentA=${encodeURIComponent(segmentA)}&segmentB=${encodeURIComponent(segmentB)}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchChurnIntelligence() {
  const res = await fetch(`${API_BASE}/churn`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function simulateChurnPropensity(data: {
  recency_days: number;
  frequency: number;
  monetary: number;
  avg_order_value: number;
  number_of_products: number;
  customer_age_days: number;
}) {
  const res = await fetch(`${API_BASE}/churn/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchCLVIntelligence() {
  const res = await fetch(`${API_BASE}/clv`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function simulateCLVValue(data: {
  recency_days: number;
  frequency: number;
  monetary: number;
  avg_order_value: number;
  number_of_products: number;
  customer_age_days: number;
}) {
  const res = await fetch(`${API_BASE}/clv/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchSentimentIntelligence() {
  const res = await fetch(`${API_BASE}/sentiment`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchProductAndRevenue() {
  const res = await fetch(`${API_BASE}/products`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchRecommendations(params?: { actionType?: string; priority?: string; limit?: number }) {
  const query = new URLSearchParams();
  if (params?.actionType) query.append('actionType', params.actionType);
  if (params?.priority) query.append('priority', params.priority);
  if (params?.limit) query.append('limit', String(params.limit));

  const res = await fetch(`${API_BASE}/recommendations?${query.toString()}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function fetchDataQualityAudit() {
  const res = await fetch(`${API_BASE}/data-quality`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}

export async function queryGroundedAI(query: string, customerId?: string): Promise<GroundedAnswer> {
  const res = await fetch(`${API_BASE}/ai/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, customerId }),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  const json = await res.json();
  return json.data;
}
