export interface ExecutiveKPIs {
  totalCustomers: number;
  activeCustomers: number;
  activeRate: number;
  totalGmv: number;
  avgCustomerValue: number;
  avgOrderValue: number;
  avgClv: number;
  repeatCustomerRate: number;
  repeatCustomersCount: number;
  atRiskCustomersCount: number;
  atRiskRevenueExposure: number;
  highValueCustomersCount: number;
  highValueRevenue: number;
}

export interface StructuredInsight {
  id: string;
  title: string;
  badge: string;
  kind: 'info' | 'warning' | 'success' | 'danger';
  observation: string;
  evidence: string;
  implication: string;
}

export interface SegmentDistribution {
  segment: string;
  customers: number;
  revenue: number;
  customerShare: number;
  revenueShare: number;
  avgSpend: number;
  avgClv: number;
  avgRecency: number;
  avgChurn: number;
}

export interface StateDistribution {
  state: string;
  customers: number;
  revenue: number;
  share: number;
}

export interface RiskDistribution {
  tier: string;
  count: number;
  share: number;
  revenue: number;
  color: string;
}

export interface OverviewData {
  kpis: ExecutiveKPIs;
  insights: StructuredInsight[];
  segmentDistribution: SegmentDistribution[];
  topStates: StateDistribution[];
  riskDistribution: RiskDistribution[];
}

export interface CustomerProfile {
  customer_id: string;
  total_orders: number;
  total_spend: number;
  avg_order_value: number;
  recency_days: number;
  frequency: number;
  monetary: number;
  customer_age_days: number;
  favorite_category: string;
  city: string;
  state: string;
  web_engagement_score: number;
  avg_review_score: number;
  low_rating_count: number;
  r_score: number;
  f_score: number;
  m_score: number;
  rfm_score: number;
  rfm_segment: string;
  cluster: number;
  cluster_segment: string;
  churn_probability: number;
  predicted_clv: number;
  churn_risk_band: string;
  clv_band: string;
  first_purchase_date?: string;
  last_purchase_date?: string;
}

export interface HealthScore {
  score: number;
  health_tier: string;
  badge_color: string;
  components: {
    recency_vital: number;
    frequency_vital: number;
    monetary_vital: number;
    engagement_vital: number;
    csat_vital: number;
    risk_penalty: number;
  };
}

export interface LifecycleStage {
  stage: string;
  reached: boolean;
  date: string;
  description: string;
}

export interface RiskDiagnostics {
  risk_level: string;
  churn_probability: number;
  risk_factors: string[];
  protective_factors: string[];
  exposure_note: string;
}

export interface RecommendationAction {
  customer_id: string;
  action_type: string;
  priority: string;
  badge_color: string;
  channel: string;
  reason: string;
  description: string;
  rfm_segment: string;
  total_spend: number;
  total_orders: number;
  avg_order_value: number;
  clv_band: string;
  predicted_clv: number;
  churn_probability: number;
  recency_days: number;
  avg_review_score: number;
  favorite_category: string;
  city: string;
  state: string;
}

export interface Customer360Dossier {
  profile: CustomerProfile;
  health: HealthScore;
  lifecycle: LifecycleStage[];
  riskDiagnostics: RiskDiagnostics;
  nextBestAction: RecommendationAction;
  rfmExplanation: {
    segment: string;
    code: string;
    factors: string[];
  };
  orders: any[];
  categoryRecommendations: any[];
}

export interface GroundedAnswer {
  query: string;
  intent: string;
  headline: string;
  detailed_answer: string;
  metrics: Record<string, any>;
  evidence_points: string[];
  recommended_action?: string;
  citations?: string;
}
