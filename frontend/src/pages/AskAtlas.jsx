import React, { useState } from 'react';
import { askGroundedQuestion } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Badge from '../components/common/Badge';
import { Sparkles, Send, CheckCircle, AlertCircle, ShieldAlert, ArrowRight } from 'lucide-react';

export default function AskAtlas() {
  const [query, setQuery] = useState('');
  const [contextCid, setContextCid] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);

  const sampleQueries = [
    { text: '🚨 Which customers are high-value and high-risk?', prompt: 'Which customers are high-value and high-risk?' },
    { text: '📊 Which segment generates the most revenue?', prompt: 'Which segment generates the most revenue?' },
    { text: '🔄 What is our repeat customer purchase rate?', prompt: 'What is our repeat customer purchase rate?' },
    { text: '💎 What is the 12-month forward CLV benchmark?', prompt: 'What is the 12-month forward CLV benchmark?' },
    { text: '🗺️ Which geographic regions drive top demand?', prompt: 'Which geographic regions drive top demand?' },
    { text: '📈 What are our macro customer metrics?', prompt: 'What are our macro customer metrics?' },
  ];

  const handleAsk = async (promptToUse) => {
    const activeQuery = promptToUse || query;
    if (!activeQuery.trim()) return;

    try {
      setLoading(true);
      const res = await askGroundedQuestion({
        query: activeQuery,
        customer_id: contextCid || undefined,
      });
      if (res.data && res.data.success) {
        setAnswer(res.data.data);
      }
    } catch (err) {
      console.error('Error asking grounded AI:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-indigo-900 rounded-2xl p-6 sm:p-8 text-white shadow-lg relative overflow-hidden">
        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-200 border border-indigo-400/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Deterministic Natural-Language Intelligence</span>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight">Ask CustomerAtlas — Grounded Decision Support</h1>
          <p className="text-xs sm:text-sm text-indigo-100 max-w-2xl leading-relaxed">
            Interrogate macro revenue, retention vulnerabilities, segment economics, and individual customer risks.
            Every response is <strong>100% mathematically grounded in verified database records</strong> with zero hallucinations or unconstrained code execution.
          </p>
        </div>
      </div>

      {/* Suggested Quick Queries */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          Suggested Decision Inquiries
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
          {sampleQueries.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(sq.prompt);
                handleAsk(sq.prompt);
              }}
              className="text-left p-3 rounded-lg border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-xs font-semibold text-slate-700 transition-all flex items-center justify-between"
            >
              <span>{sq.text}</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* Query Input Box */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk(query);
          }}
          className="space-y-3"
        >
          <div>
            <label className="text-xs font-bold text-slate-700 block mb-1.5">
              Enter Question or Decision Inquiry
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. Which customers are high-value and high-risk? or Explain risk for customer"
                className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-xs font-medium focus:outline-none focus:border-indigo-600 focus:bg-white transition-all"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-5 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Ask AI</span>
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <span className="text-[11.5px] font-semibold text-slate-500">Optional Customer Context ID:</span>
            <input
              type="text"
              placeholder="32-char Customer ID (optional)"
              value={contextCid}
              onChange={(e) => setContextCid(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs font-mono w-64"
            />
          </div>
        </form>
      </div>

      {/* Answer Output */}
      {loading ? (
        <LoadingSpinner message="Interrogating verified customer records & synthesizing evidence..." />
      ) : answer ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-5 animate-fadeIn">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {answer.confidence_rating}
                </span>
                <span className="text-xs text-slate-400 font-mono">Intent: {answer.intent}</span>
              </div>
              <h2 className="text-base font-extrabold text-slate-900 tracking-tight">{answer.headline}</h2>
            </div>
          </div>

          {/* Detailed Synthesized Answer */}
          <div className="text-xs leading-relaxed text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-200/80">
            <p className="font-medium">{answer.detailed_answer}</p>
          </div>

          {/* Metric Highlights */}
          {answer.metrics && Object.keys(answer.metrics).length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {Object.entries(answer.metrics).map(([key, val], idx) => (
                <div key={idx} className="bg-white border border-slate-200 rounded-lg p-3">
                  <div className="text-[10.5px] font-bold text-slate-500 uppercase tracking-wider mb-0.5 truncate">
                    {key.replace(/_/g, ' ')}
                  </div>
                  <div className="text-base font-extrabold text-indigo-700 font-mono">
                    {typeof val === 'number' ? val.toLocaleString() : String(val)}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Evidence Citations */}
          {answer.evidence_points && answer.evidence_points.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Verifiable Grounding Evidence:
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-600 bg-slate-50/50 p-3 rounded-lg border border-slate-100">
                {answer.evidence_points.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommended Action */}
          {answer.recommended_action && (
            <div className="bg-indigo-50/60 border border-indigo-200 rounded-xl p-4 flex items-start gap-3">
              <span className="text-xl">💡</span>
              <div className="text-xs text-indigo-950">
                <strong className="block font-bold text-indigo-900 mb-0.5">Recommended Operational Action:</strong>
                <p className="font-medium">{answer.recommended_action}</p>
              </div>
            </div>
          )}

          {/* Limitation Disclaimer */}
          <div className="text-[11px] text-slate-400 italic pt-2 border-t border-slate-100">
            <strong>Data Governance Notice: </strong>{answer.limitations_disclaimer}
          </div>
        </div>
      ) : null}
    </div>
  );
}
