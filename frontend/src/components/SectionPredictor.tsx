import React, { useState } from 'react';
import { predictPersonality } from '../services/api';
import type { PredictResponse } from '../types/api';
import { ArrowRight, AlertCircle, Info, Sparkles } from 'lucide-react';

export const SectionPredictor: React.FC = () => {
  const [recency, setRecency] = useState<string>('12');
  const [frequency, setFrequency] = useState<string>('6');
  const [monetary, setMonetary] = useState<string>('1800');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setResult(null);

    const r = parseFloat(recency);
    const f = Number(frequency);
    const m = parseFloat(monetary);

    if (!Number.isFinite(r) || r < 0) {
      setError('Please provide a valid non-negative number of days for Recency.');
      return;
    }
    if (!Number.isSafeInteger(f) || f < 1) {
      setError('Please provide at least 1 completed purchase order.');
      return;
    }
    if (!Number.isFinite(m) || m <= 0) {
      setError('Please provide a positive total spending amount in GBP (£).');
      return;
    }

    setLoading(true);
    try {
      const res = await predictPersonality({ recency: r, frequency: f, monetary: m });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to predict segment.');
    } finally {
      setLoading(false);
    }
  };

  const setPreset = (r: number, f: number, m: number) => {
    setRecency(r.toString());
    setFrequency(f.toString());
    setMonetary(m.toString());
    setError(null);
    setResult(null);
  };

  return (
    <section id="predictor" className="py-12 border-b border-[#EAE9E4]">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="max-w-3xl mb-10">
          <span className="text-xs font-bold uppercase tracking-wider text-[#91563f] mb-2 block">
            Real-Time Inference
          </span>
          <h2 className="font-editorial text-3xl sm:text-4xl text-[#242725] font-bold tracking-tight mb-3">
            Find Your Shopping Personality
          </h2>
          <p className="text-sm text-[#242725]/75 leading-relaxed font-normal">
            Input hypothetical or real transaction metrics to test how the trained K-Means pipeline transforms
            features and maps your profile to the discovered shopping clusters.
          </p>
        </div>

        {/* Preset Buttons */}
        <div className="flex flex-wrap items-center gap-2 mb-8">
          <span className="text-xs font-medium text-[#242725]/60 mr-1">Quick Test Scenarios:</span>
          <button
            type="button"
            onClick={() => setPreset(6, 12, 4500)}
            className="text-xs px-3 py-1 rounded-md bg-white border border-[#EAE9E4] text-[#242725] hover:border-[#718776] hover:bg-[#FAF9F5] transition-colors"
          >
            Loyal Champion (6d, 12 orders, £4.5k)
          </button>
          <button
            type="button"
            onClick={() => setPreset(18, 2, 480)}
            className="text-xs px-3 py-1 rounded-md bg-white border border-[#EAE9E4] text-[#242725] hover:border-[#718776] hover:bg-[#FAF9F5] transition-colors"
          >
            Active Regular (18d, 2 orders, £480)
          </button>
          <button
            type="button"
            onClick={() => setPreset(65, 4, 1400)}
            className="text-xs px-3 py-1 rounded-md bg-white border border-[#EAE9E4] text-[#242725] hover:border-[#718776] hover:bg-[#FAF9F5] transition-colors"
          >
            At-Risk Spender (65d, 4 orders, £1.4k)
          </button>
          <button
            type="button"
            onClick={() => setPreset(210, 1, 190)}
            className="text-xs px-3 py-1 rounded-md bg-white border border-[#EAE9E4] text-[#242725] hover:border-[#718776] hover:bg-[#FAF9F5] transition-colors"
          >
            Dormant Buyer (210d, 1 order, £190)
          </button>
          <button
            type="button"
            onClick={() => setPreset(10, 15, 350000)}
            className="text-xs px-3 py-1 rounded-md bg-white border border-[#EAE9E4] text-[#91563f] hover:border-[#C77D5C] hover:bg-[#FAF5F2] transition-colors"
          >
            Outlier Test (&gt;£300k)
          </button>
        </div>

        {/* Main Grid: Form + Result */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Input Form */}
          <div className="lg:col-span-5 bg-white p-6 sm:p-8 rounded-md border border-[#EAE9E4] ">
            <form onSubmit={handlePredict} className="space-y-5">
              <div>
                <label htmlFor="recency" className="block text-xs font-bold uppercase tracking-wider text-[#242725]/70 mb-2">
                  1. Days Since Last Purchase (Recency)
                </label>
                <div className="relative">
                  <input
                    type="number"
                    disabled={loading}
                    min="0"
                    step="1"
                    id="recency"
                    value={recency}
                    onChange={(e) => { setRecency(e.target.value); setResult(null); }}
                    placeholder="e.g. 15"
                    className="w-full px-3.5 py-2.5 rounded-lg border border-[#D5D3C8] text-sm focus:outline-none focus:ring-2 focus:ring-[#718776] focus:border-transparent bg-[#FAF9F5]"
                    required
                  />
                  <span className="absolute right-3.5 top-2.5 text-xs text-[#242725]/40">days</span>
                </div>
                <p className="text-[11px] text-[#242725]/65 mt-1">
                  How many days elapsed since your most recent completed transaction.
                </p>
              </div>

              <div>
                <label htmlFor="frequency" className="block text-xs font-bold uppercase tracking-wider text-[#242725]/70 mb-2">
                  2. Total Completed Orders (Frequency)
                </label>
                <div className="relative">
                  <input
                    type="number"
                    disabled={loading}
                    min="1"
                    step="1"
                    id="frequency"
                    value={frequency}
                    onChange={(e) => { setFrequency(e.target.value); setResult(null); }}
                    placeholder="e.g. 4"
                    className="w-full px-3.5 py-2.5 rounded-lg border border-[#D5D3C8] text-sm focus:outline-none focus:ring-2 focus:ring-[#718776] focus:border-transparent bg-[#FAF9F5]"
                    required
                  />
                  <span className="absolute right-3.5 top-2.5 text-xs text-[#242725]/40">orders</span>
                </div>
                <p className="text-[11px] text-[#242725]/65 mt-1">
                  Number of distinct purchase invoices completed within the dataset observation window.
                </p>
              </div>

              <div>
                <label htmlFor="monetary" className="block text-xs font-bold uppercase tracking-wider text-[#242725]/70 mb-2">
                  3. Total Spending in GBP (£) (Monetary)
                </label>
                <div className="relative">
                  <span className="absolute left-3.5 top-2.5 text-sm text-[#242725]/65">£</span>
                  <input
                    type="number"
                    disabled={loading}
                    min="0.01"
                    step="0.01"
                    id="monetary"
                    value={monetary}
                    onChange={(e) => { setMonetary(e.target.value); setResult(null); }}
                    placeholder="e.g. 1200"
                    className="w-full pl-8 pr-3.5 py-2.5 rounded-lg border border-[#D5D3C8] text-sm focus:outline-none focus:ring-2 focus:ring-[#718776] focus:border-transparent bg-[#FAF9F5]"
                    required
                  />
                </div>
                <p className="text-[11px] text-[#242725]/65 mt-1">
                  Spending within the same observation window, excluding cancellations.
                </p>
              </div>

              {error && (
                <div className="p-3 rounded-md bg-[#FAF5F2] border border-[#F0D5CB] text-[#91563f] text-xs flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-lg bg-[#242725] text-white text-xs font-bold uppercase tracking-wider hover:bg-[#383C39] active:bg-[#1A1C1A] transition-all flex items-center justify-center gap-2 "
              >
                {loading ? (
                  <span>Processing ML Pipeline...</span>
                ) : (
                  <>
                    <span>Discover My Segment</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Result Panel */}
          <div className="lg:col-span-7">
            {result ? (
              <div className="bg-white rounded-md border border-[#EAE9E4] p-6 sm:p-8  animate-fadeIn">
                <div className="flex items-center justify-between mb-4">
                  <span
                    className="text-xs font-bold px-3 py-1 rounded-full"
                    style={{ backgroundColor: `${result.color}15`, color: result.color }}
                  >
                    {result.badge}
                  </span>
                  <span className="text-xs text-[#242725]/65 font-medium">
                    Cluster {result.cluster_id} Discovered
                  </span>
                </div>

                <h3 className="font-editorial text-2xl sm:text-3xl font-bold text-[#242725] mb-2">
                  {result.segment_name}
                </h3>

                <p className="text-sm text-[#242725]/80 leading-relaxed mb-6">
                  {result.description}
                </p>

                {/* Outlier Warning if any */}
                {result.is_outlier && (
                  <div className="mb-6 p-4 rounded-lg bg-[#FFF8F0] border border-[#FFE4C4] text-xs text-[#8A5020] flex items-start gap-2.5">
                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-[#91563f]" />
                    <div>
                      <strong>Training Distribution Outlier Alert:</strong> {result.outlier_warning}
                      <p className="mt-1 text-[11px] text-[#8A5020]/80">
                        The pipeline normalized the input, but the extreme value lies beyond the historical retail training horizon.
                      </p>
                    </div>
                  </div>
                )}

                {/* Metric Comparison to Cluster Medians */}
                <div className="mb-6">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#242725]/60 mb-3">
                    Comparison to {result.segment_name} Medians
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="p-3.5 rounded-lg bg-[#FAF9F5] border border-[#EAE9E4] text-xs">
                      <span className="text-[10px] text-[#242725]/65 block">Your Recency</span>
                      <strong className="text-sm text-[#242725]">{result.input_values.recency}d</strong>
                      <span className="text-[11px] text-[#4f6955] block mt-1">
                        Median: {result.cluster_medians.recency}d
                      </span>
                      <span className="text-[10px] text-[#242725]/60 block mt-0.5">
                        {result.comparison.recency_comparison}
                      </span>
                    </div>

                    <div className="p-3.5 rounded-lg bg-[#FAF9F5] border border-[#EAE9E4] text-xs">
                      <span className="text-[10px] text-[#242725]/65 block">Your Frequency</span>
                      <strong className="text-sm text-[#242725]">{result.input_values.frequency} orders</strong>
                      <span className="text-[11px] text-[#4f6955] block mt-1">
                        Median: {result.cluster_medians.frequency} orders
                      </span>
                      <span className="text-[10px] text-[#242725]/60 block mt-0.5">
                        {result.comparison.frequency_comparison}
                      </span>
                    </div>

                    <div className="p-3.5 rounded-lg bg-[#FAF9F5] border border-[#EAE9E4] text-xs">
                      <span className="text-[10px] text-[#242725]/65 block">Your Spending</span>
                      <strong className="text-sm text-[#242725]">£{result.input_values.monetary.toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
                      <span className="text-[11px] text-[#4f6955] block mt-1">
                        Median: £{result.cluster_medians.monetary.toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </span>
                      <span className="text-[10px] text-[#242725]/60 block mt-0.5 font-medium text-[#4f6955]">
                        {result.comparison.monetary_comparison}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Business Recommendation */}
                <div className="p-4 rounded-lg bg-[#F5F4EE] border border-[#E5E4DE] text-xs mb-6">
                  <div className="flex items-center gap-2 font-bold text-[#242725] uppercase tracking-wider mb-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-[#91563f]" />
                    <span>Recommended Retail Strategy</span>
                  </div>
                  <p className="text-[#242725]/80 leading-relaxed">
                    {result.business_insight}
                  </p>
                </div>

                {/* Academic Disclaimer */}
                <div className="text-[11px] text-[#242725]/65 flex items-start gap-2 border-t border-[#F0EFEA] pt-4">
                  <Info className="w-3.5 h-3.5 text-[#4f6955] shrink-0 mt-0.5" />
                  <p>
                    <strong>Academic Demonstration Note:</strong> This prediction is generated by applying the saved
                    Scikit-learn StandardScaler and K-Means model to historical retail transaction data (2010–2011).
                    It represents a mathematical classification and is not an assessment of personal character or psychology.
                  </p>
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[380px] rounded-md border border-dashed border-[#D5D3C8] bg-white/40 p-8 flex flex-col items-center justify-center text-center">
                <div className="w-12 h-12 rounded-full bg-[#FAF9F5] border border-[#EAE9E4] flex items-center justify-center text-[#4f6955] mb-4">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h4 className="font-editorial text-xl font-bold text-[#242725] mb-2">
                  Ready to Infer Shopping Segment
                </h4>
                <p className="text-xs text-[#242725]/60 max-w-sm leading-relaxed mb-6">
                  Fill in the three inputs on the left or click one of the quick test scenarios above to see how the model categorizes shopping behavior.
                </p>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handlePredict()}
                  className="text-xs font-semibold px-4 py-2 rounded-md bg-[#FAF9F5] border border-[#EAE9E4] text-[#242725] hover:bg-white transition-colors"
                >
                  Run Default Scenario (12d, 6 orders, £1,800)
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};
