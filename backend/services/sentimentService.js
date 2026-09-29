const dataService = require('./dataService');

const computeSentimentOverview = () => {
  const reviews = dataService.getAllReviews();
  const total = reviews.length;
  if (total === 0) {
    return {
      total_reviews: 0,
      avg_review_score: 0,
      positive_pct: 0,
      neutral_pct: 0,
      negative_pct: 0,
      positive_count: 0,
      neutral_count: 0,
      negative_count: 0,
      comments_count: 0,
      comment_rate: 0,
    };
  }

  let totalScore = 0;
  let pos = 0, neu = 0, neg = 0, withComments = 0;

  reviews.forEach((r) => {
    totalScore += r.review_score;
    if (r.sentiment_category === 'Positive') pos++;
    else if (r.sentiment_category === 'Neutral') neu++;
    else if (r.sentiment_category === 'Negative') neg++;

    if (r.review_comment_message && r.review_comment_message.trim().length > 0) {
      withComments++;
    }
  });

  return {
    total_reviews: total,
    avg_review_score: parseFloat((totalScore / total).toFixed(2)),
    positive_pct: parseFloat((pos / total).toFixed(4)),
    neutral_pct: parseFloat((neu / total).toFixed(4)),
    negative_pct: parseFloat((neg / total).toFixed(4)),
    positive_count: pos,
    neutral_count: neu,
    negative_count: neg,
    comments_count: withComments,
    comment_rate: parseFloat((withComments / total).toFixed(4)),
  };
};

const computeRatingDistribution = () => {
  const reviews = dataService.getAllReviews();
  const counts = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  reviews.forEach((r) => {
    if (counts[r.review_score] !== undefined) {
      counts[r.review_score]++;
    }
  });

  return [1, 2, 3, 4, 5].map((score) => ({
    star_label: `${score} Star(s)`,
    score,
    count: counts[score] || 0,
  }));
};

const computeSentimentPolarityPie = () => {
  const reviews = dataService.getAllReviews();
  const counts = { Positive: 0, Neutral: 0, Negative: 0 };
  reviews.forEach((r) => {
    if (counts[r.sentiment_category] !== undefined) {
      counts[r.sentiment_category]++;
    }
  });

  return [
    { name: 'Positive', count: counts.Positive, color: '#16A34A' },
    { name: 'Neutral', count: counts.Neutral, color: '#F59E0B' },
    { name: 'Negative', count: counts.Negative, color: '#DC2626' },
  ];
};

const computeLongitudinalSentimentTrend = () => {
  const reviews = dataService.getAllReviews();
  const monthly = {};

  reviews.forEach((r) => {
    if (r.review_month && /^201[6-8]-\d{2}$/.test(r.review_month)) {
      if (!monthly[r.review_month]) {
        monthly[r.review_month] = {
          month: r.review_month,
          total: 0,
          score_sum: 0,
          pos: 0,
          neg: 0,
          neu: 0,
        };
      }
      monthly[r.review_month].total++;
      monthly[r.review_month].score_sum += r.review_score;
      if (r.sentiment_category === 'Positive') monthly[r.review_month].pos++;
      else if (r.sentiment_category === 'Negative') monthly[r.review_month].neg++;
      else monthly[r.review_month].neu++;
    }
  });

  return Object.values(monthly)
    .map((m) => ({
      review_month: m.month,
      total_reviews: m.total,
      avg_score: parseFloat((m.score_sum / Math.max(1, m.total)).toFixed(2)),
      pos_reviews: m.pos,
      neg_reviews: m.neg,
      neu_reviews: m.neu,
      positive_pct: parseFloat((m.pos / Math.max(1, m.total)).toFixed(4)),
      negative_pct: parseFloat((m.neg / Math.max(1, m.total)).toFixed(4)),
    }))
    .sort((a, b) => a.review_month.localeCompare(b.review_month));
};

const extractNegativeThemes = (topN = 5) => {
  const reviews = dataService.getAllReviews();
  const negWithComments = reviews.filter(
    (r) => r.review_score <= 2 && r.review_comment_message && r.review_comment_message.trim().length > 0
  );

  const totalWithComments = negWithComments.length;
  if (totalWithComments === 0) return [];

  const themesDef = [
    {
      theme: 'Delivery Delay & Logistics Friction',
      keywords: ['atraso', 'atrasou', 'demora', 'demorou', 'nao recebi', 'não recebi', 'prazo', 'entrega', 'esperando', 'nunca chegou'],
      description: 'Shipment arrived past promised estimated delivery date or is currently delayed in transit.',
      action: 'Audit carrier performance, adjust delivery promise algorithms, and trigger proactive delay notifications.',
      badge_color: '#DC2626',
      icon: '🚚',
    },
    {
      theme: 'Product Quality & Physical Defect',
      keywords: ['defeito', 'quebrado', 'danificado', 'qualidade', 'estragado', 'pessimo', 'péssimo', 'ruim', 'fraco', 'material'],
      description: 'Received merchandise was broken, defective, or of lower manufacturing quality than expected.',
      action: 'Enforce vendor quality control standards and streamline automated replacement returns.',
      badge_color: '#EA580C',
      icon: '⚠️',
    },
    {
      theme: 'Product Discrepancy & Catalog Inaccuracy',
      keywords: ['diferente', 'errado', 'foto', 'veio errado', 'outro produto', 'tamanho', 'cor errada', 'modelo diferente'],
      description: 'Delivered item did not match catalog listing photos, size description, or specifications.',
      action: 'Audit marketplace seller listings, update product images, and verify SKU dimension specifications.',
      badge_color: '#F59E0B',
      icon: '📦',
    },
    {
      theme: 'Missing Items & Incomplete Shipments',
      keywords: ['faltou', 'incompleto', 'veio faltando', 'nao veio', 'não veio', 'metade', 'falta', 'peca faltando'],
      description: 'Customer received a multi-item package where one or more line items were omitted.',
      action: 'Improve warehouse pick-and-pack scanning verification and barcode audit checkpoints.',
      badge_color: '#8B5CF6',
      icon: '🔍',
    },
    {
      theme: 'Customer Support & Communication Responsiveness',
      keywords: ['contato', 'atendimento', 'resposta', 'nao responde', 'não responde', 'ninguem', 'sac', 'ignorado'],
      description: 'Customer experienced unresponsiveness when seeking assistance or order status updates.',
      action: 'Deploy omni-channel automated ticketing and establish an SLA of < 4 business hours for issue resolution.',
      badge_color: '#0284C7',
      icon: '💬',
    },
  ];

  const results = themesDef.map((t) => {
    const regex = new RegExp(t.keywords.join('|'), 'i');
    let matchedCount = 0;
    const sampleFeedback = [];

    negWithComments.forEach((r) => {
      if (regex.test(r.review_comment_message)) {
        matchedCount++;
        if (sampleFeedback.length < 3) {
          sampleFeedback.push(r.review_comment_message);
        }
      }
    });

    return {
      theme: t.theme,
      matched_count: matchedCount,
      share_of_negative_comments: parseFloat((matchedCount / totalWithComments).toFixed(4)),
      description: t.description,
      action: t.action,
      badge_color: t.badge_color,
      icon: t.icon,
      sample_feedback: sampleFeedback,
    };
  });

  return results.sort((a, b) => b.matched_count - a.matched_count).slice(0, topN);
};

const computeSentimentBySegment = (customers) => {
  const segMap = {};
  customers.forEach((c) => {
    const seg = c.rfm_segment || 'Regular Customers';
    if (!segMap[seg]) {
      segMap[seg] = { rfm_segment: seg, customers: 0, csat_sum: 0, low_rating_customers: 0 };
    }
    segMap[seg].customers++;
    segMap[seg].csat_sum += c.avg_review_score || 5.0;
    if (c.low_rating_count > 0) segMap[seg].low_rating_customers++;
  });

  return Object.values(segMap)
    .map((s) => ({
      rfm_segment: s.rfm_segment,
      customers: s.customers,
      avg_csat: parseFloat((s.csat_sum / Math.max(1, s.customers)).toFixed(2)),
      low_rating_customers: s.low_rating_customers,
      low_rating_pct: parseFloat((s.low_rating_customers / Math.max(1, s.customers)).toFixed(4)),
    }))
    .sort((a, b) => b.avg_csat - a.avg_csat);
};

const computeCategorySatisfaction = (customers) => {
  const catMap = {};
  customers.forEach((c) => {
    const cat = c.favorite_category || 'General';
    if (!catMap[cat]) {
      catMap[cat] = { favorite_category: cat, customers: 0, csat_sum: 0, total_spend: 0 };
    }
    catMap[cat].customers++;
    catMap[cat].csat_sum += c.avg_review_score || 5.0;
    catMap[cat].total_spend += c.total_spend;
  });

  return Object.values(catMap)
    .filter((c) => c.customers >= 50)
    .map((c) => ({
      favorite_category: c.favorite_category,
      customers: c.customers,
      avg_review_score: parseFloat((c.csat_sum / c.customers).toFixed(2)),
      total_revenue: parseFloat(c.total_spend.toFixed(2)),
    }))
    .sort((a, b) => b.avg_review_score - a.avg_review_score)
    .slice(0, 10);
};

const searchReviews = (filters = {}) => {
  let reviews = dataService.getAllReviews();

  if (filters.stars && filters.stars.length > 0) {
    const set = new Set(filters.stars.map(Number));
    reviews = reviews.filter((r) => set.has(r.review_score));
  }
  if (filters.only_comments) {
    reviews = reviews.filter((r) => r.review_comment_message && r.review_comment_message.trim().length > 0);
  }

  return reviews.slice(0, 100);
};

module.exports = {
  computeSentimentOverview,
  computeRatingDistribution,
  computeSentimentPolarityPie,
  computeLongitudinalSentimentTrend,
  extractNegativeThemes,
  computeSentimentBySegment,
  computeCategorySatisfaction,
  searchReviews,
};
