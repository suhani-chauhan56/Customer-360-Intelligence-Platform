import React, { useState, useEffect } from 'react';
import { getSentimentOverview, searchReviews } from '../services/api';
import { formatPct, formatNum, formatDate } from '../utils/formatting';
import KpiCard from '../components/common/KpiCard';
import SectionHeader from '../components/common/SectionHeader';
import LoadingSpinner from '../components/common/LoadingSpinner';
import PieChartComponent from '../components/charts/PieChartComponent';
import BarChartComponent from '../components/charts/BarChartComponent';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Star, MessageSquare, Filter, AlertCircle } from 'lucide-react';

export default function SentimentIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Review Explorer State
  const [selectedStars, setSelectedStars] = useState([1, 2]);
  const [onlyComments, setOnlyComments] = useState(true);
  const [reviewList, setReviewList] = useState([]);
  const [loadingReviews, setLoadingReviews] = useState(false);

  useEffect(() => {
    fetchSentimentData();
  }, []);

  useEffect(() => {
    fetchReviews();
  }, [selectedStars, onlyComments]);

  const fetchSentimentData = async () => {
    try {
      setLoading(true);
      const res = await getSentimentOverview();
      if (res.data && res.data.success) {
        setData(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching sentiment overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchReviews = async () => {
    try {
      setLoadingReviews(true);
      const res = await searchReviews({
        stars: selectedStars.join(','),
        only_comments: onlyComments,
      });
      if (res.data && res.data.success) {
        setReviewList(res.data.data);
      }
    } catch (err) {
      console.error('Error fetching reviews:', err);
    } finally {
      setLoadingReviews(false);
    }
  };

  if (loading || !data) {
    return <LoadingSpinner message="Extracting CSAT feedback & sentiment themes..." />;
  }

  const {
    overview,
    rating_distribution,
    polarity_distribution,
    longitudinal_trend,
    negative_themes,
    segment_satisfaction,
    category_satisfaction,
  } = data;

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="inline-block text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full uppercase tracking-wider mb-2 border border-indigo-100">
          Predictive & Risk AI
        </div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Sentiment Intelligence & Customer CSAT Analytics
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Customer satisfaction benchmarks, longitudinal sentiment trends, segment CSAT, and empirical negative feedback root causes.
        </p>
      </div>

      {/* CSAT KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Average CSAT Rating"
          value={`${overview.avg_review_score.toFixed(2)} / 5.0`}
          subtitle={`${formatNum(overview.total_reviews)} verified reviews`}
          icon="⭐"
        />
        <KpiCard
          label="Positive Feedback Rate"
          value={formatPct(overview.positive_pct)}
          delta={`${formatNum(overview.positive_count)} ratings`}
          deltaDirection="positive"
          subtitle="4-5 Stars (Satisfied)"
          icon="😊"
        />
        <KpiCard
          label="Neutral Feedback Rate"
          value={formatPct(overview.neutral_pct)}
          subtitle="3 Stars (Indifferent)"
          icon="😐"
        />
        <KpiCard
          label="Negative Feedback Rate"
          value={formatPct(overview.negative_pct)}
          delta={`${formatNum(overview.negative_count)} ratings`}
          deltaDirection="negative"
          subtitle="1-2 Stars (Friction)"
          icon="⚠️"
        />
      </div>

      {/* Star Distribution and Polarity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarChartComponent
          title="Customer Review Rating Distribution (1 to 5 Stars)"
          data={rating_distribution || []}
          xKey="star_label"
          yKey="count"
          color="#0284C7"
          height={280}
        />
        <PieChartComponent
          title="Customer Sentiment Polarity Breakdown"
          data={polarity_distribution || []}
          dataKey="count"
          nameKey="name"
          height={280}
        />
      </div>

      {/* Longitudinal Sentiment Trajectory */}
      {longitudinal_trend && longitudinal_trend.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <SectionHeader
            title="Longitudinal CSAT & Sentiment Trajectory"
            subtitle="Monthly Satisfaction Tracking & Star Rating Breakdown"
          />
          <div style={{ height: 320, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={longitudinal_trend} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="review_month" tick={{ fontSize: 11, fill: '#64748B' }} angle={-20} textAnchor="end" />
                <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#64748B' }} />
                <YAxis yAxisId="right" orientation="right" domain={[1, 5]} tick={{ fontSize: 11, fill: '#4F46E5' }} />
                <Tooltip />
                <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '11px' }} />
                <Bar yAxisId="left" dataKey="pos_reviews" name="Positive Reviews (4-5★)" fill="#16A34A" stackId="a" />
                <Bar yAxisId="left" dataKey="neg_reviews" name="Negative Reviews (1-2★)" fill="#DC2626" stackId="a" />
                <Line yAxisId="right" type="monotone" dataKey="avg_score" name="Average CSAT Rating (1-5)" stroke="#4F46E5" strokeWidth={3} dot={{ r: 3 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Negative Theme Root-Cause Extraction */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="Negative Feedback Root-Cause Themes"
          subtitle="Factual Portuguese Text Extraction & Logistics Friction Drivers"
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {negative_themes.map((t, idx) => (
            <div
              key={idx}
              className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs flex flex-col justify-between"
              style={{ borderTop: `4px solid ${t.badge_color}` }}
            >
              <div>
                <div className="text-2xl mb-1">{t.icon}</div>
                <h4 className="text-xs font-bold text-slate-900 mb-1">{t.theme}</h4>
                <div className="text-xl font-extrabold mb-0.5" style={{ color: t.badge_color }}>
                  {formatNum(t.matched_count)} Reviews
                </div>
                <div className="text-[11px] text-slate-500 font-semibold mb-2">
                  {formatPct(t.share_of_negative_comments)} of low-rating comments
                </div>
                <p className="text-xs text-slate-600 font-medium leading-relaxed mb-3">{t.description}</p>
              </div>

              <div>
                {t.sample_feedback && t.sample_feedback.length > 0 && (
                  <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-[11px] text-slate-600 italic mb-2 line-clamp-2">
                    "{t.sample_feedback[0]}"
                  </div>
                )}
                <div className="text-[11.5px] font-bold text-indigo-700 bg-indigo-50/60 p-2 rounded-lg border border-indigo-100">
                  🛠️ {t.action}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Satisfaction by Segment & Product Category */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarChartComponent
          title="Average Customer CSAT Rating by RFM Segment"
          data={segment_satisfaction || []}
          xKey="rfm_segment"
          yKey="avg_csat"
          color="#16A34A"
          height={280}
        />
        <BarChartComponent
          title="Top Rated Product Categories (Min. 50 Customers)"
          data={category_satisfaction || []}
          xKey="favorite_category"
          yKey="avg_review_score"
          horizontal={true}
          color="#0284C7"
          height={280}
        />
      </div>

      {/* Verified Customer Feedback Review Explorer */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <SectionHeader
          title="Customer Feedback Review Explorer"
          subtitle="Search & Inspect Verified Review Comments"
        />

        <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-700">Filter Star Ratings:</span>
            {[1, 2, 3, 4, 5].map((star) => {
              const isSelected = selectedStars.includes(star);
              return (
                <button
                  key={star}
                  onClick={() => {
                    setSelectedStars((prev) =>
                      isSelected ? prev.filter((s) => s !== star) : [...prev, star]
                    );
                  }}
                  className={`px-2.5 py-1 rounded text-xs font-bold border transition-colors ${
                    isSelected
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-slate-600 border-slate-200'
                  }`}
                >
                  {star} ★
                </button>
              );
            })}
          </div>

          <label className="flex items-center gap-2 font-semibold text-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={onlyComments}
              onChange={(e) => setOnlyComments(e.target.checked)}
              className="accent-indigo-600 rounded"
            />
            <span>Only Show Reviews With Written Comments</span>
          </label>
        </div>

        {loadingReviews ? (
          <LoadingSpinner message="Loading customer reviews..." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                  <th className="py-2.5 px-3">Rating</th>
                  <th className="py-2.5 px-3">Sentiment</th>
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3">Review Comment Message</th>
                  <th className="py-2.5 px-3">Order ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {reviewList.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-bold text-slate-900">{r.review_score} ★</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                          r.sentiment_category === 'Positive'
                            ? 'bg-emerald-50 text-emerald-700'
                            : r.sentiment_category === 'Negative'
                            ? 'bg-rose-50 text-rose-700'
                            : 'bg-amber-50 text-amber-700'
                        }`}
                      >
                        {r.sentiment_category}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-500">{formatDate(r.review_creation_date)}</td>
                    <td className="py-2.5 px-3 text-slate-700 max-w-md">
                      {r.review_comment_message || <span className="text-slate-400 italic">No comment text</span>}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-indigo-600">{r.order_id ? `${r.order_id.substring(0, 10)}...` : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
