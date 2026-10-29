import React from 'react';
import type { SegmentProfile } from '../types/api';
import { CheckCircle2, Clock, ShoppingCart, PoundSterling, Sparkles, ChevronRight } from 'lucide-react';

interface Props {
  segments: SegmentProfile[];
  selectedClusterId: number | null;
  onSelectCluster: (clusterId: number | null) => void;
}

export const SectionPersonalities: React.FC<Props> = ({
  segments,
  selectedClusterId,
  onSelectCluster,
}) => {
  const inspectedCluster = segments.find(s => s.cluster_id === selectedClusterId) ?? null;

  const handleCardClick = (seg: SegmentProfile) => {
    if (selectedClusterId === seg.cluster_id) {
      onSelectCluster(null);

    } else {
      onSelectCluster(seg.cluster_id);

    }
  };

  return (
    <section id="personalities" className="py-12 border-b border-[#EAE9E4]">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#4f6955] mb-2 block">
              Discovered Archetypes
            </span>
            <h2 className="font-editorial text-3xl sm:text-4xl text-[#242725] font-bold tracking-tight">
              Shopping Personality Profiles
            </h2>
          </div>
          <p className="text-sm text-[#242725]/70 max-w-md mt-3 md:mt-0 font-normal">
            Clusters emerge from measured purchase cadence, recency, and spending. Names and insights
            are assigned only after examining empirical medians.
          </p>
        </div>

        {/* Personality Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {segments.map((seg) => {
            const isSelected = selectedClusterId === seg.cluster_id;
            return (
              <div
                key={seg.cluster_id}
                role="button"
                tabIndex={0}
                aria-pressed={isSelected}
                aria-label={`Inspect ${seg.name}`}
                onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); handleCardClick(seg); } }}
                onClick={() => handleCardClick(seg)}
                className={`group relative rounded-md bg-white p-6 transition-all duration-200 cursor-pointer border ${
                  isSelected
                    ? 'ring-2 ring-[#242725] border-transparent '
                    : 'border-[#EAE9E4] hover:border-[#D0CEBE] hover:'
                }`}
              >
                {/* Color Pill & Badge */}
                <div className="flex items-center justify-between mb-4">
                  <span
                    className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full"
                    style={{ backgroundColor: `${seg.color}15`, color: seg.color }}
                  >
                    {seg.badge}
                  </span>
                  <span className="text-xs text-[#242725]/65 font-medium">
                    Cluster {seg.cluster_id}
                  </span>
                </div>

                {/* Personality Name */}
                <h3 className="font-editorial text-xl font-bold text-[#242725] mb-2 group-hover:text-[#4f6955] transition-colors">
                  {seg.name}
                </h3>

                {/* Short Description */}
                <p className="text-xs text-[#242725]/70 leading-relaxed mb-6 min-h-[48px]">
                  {seg.description}
                </p>

                {/* Population Share */}
                <div className="flex items-center justify-between py-2 border-t border-b border-[#F0EFEA] mb-4 text-xs">
                  <span className="text-[#242725]/60">Population Share</span>
                  <span className="font-bold text-[#242725]">
                    {seg.count.toLocaleString()} ({seg.percentage}%)
                  </span>
                </div>

                {/* 3 Metric Pills */}
                <div className="space-y-2.5 text-xs">
                  <div className="flex items-center justify-between text-[#242725]/75">
                    <span className="flex items-center gap-1.5 text-[#242725]/60">
                      <Clock className="w-3.5 h-3.5 text-[#4f6955]" /> Recency:
                    </span>
                    <span className="font-semibold text-[#242725]">{seg.Recency_median.toFixed(0)} days</span>
                  </div>

                  <div className="flex items-center justify-between text-[#242725]/75">
                    <span className="flex items-center gap-1.5 text-[#242725]/60">
                      <ShoppingCart className="w-3.5 h-3.5 text-[#4f6955]" /> Frequency:
                    </span>
                    <span className="font-semibold text-[#242725]">{seg.Frequency_median.toFixed(0)} orders</span>
                  </div>

                  <div className="flex items-center justify-between text-[#242725]/75">
                    <span className="flex items-center gap-1.5 text-[#242725]/60">
                      <PoundSterling className="w-3.5 h-3.5 text-[#4f6955]" /> Median Spend:
                    </span>
                    <span className="font-bold text-[#242725]">£{seg.Monetary_median.toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                  </div>
                </div>

                {/* Card Action Link */}
                <div className="mt-5 pt-3 border-t border-[#F0EFEA] flex items-center justify-between text-xs text-[#4f6955] font-medium">
                  <span>{isSelected ? 'Selected in Map' : 'Click to inspect'}</span>
                  <ChevronRight className={`w-3.5 h-3.5 transition-transform ${isSelected ? 'rotate-90' : 'group-hover:translate-x-0.5'}`} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Cluster Deep Inspection Drawer */}
        {inspectedCluster && (
          <div className="rounded-md bg-[#F0EFEA] border border-[#E0DED7] p-6 lg:p-8 animate-fadeIn">
            <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
              <div className="max-w-2xl">
                <div className="flex items-center gap-3 mb-2">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: inspectedCluster.color }}
                  ></span>
                  <span className="text-xs font-bold uppercase tracking-wider text-[#242725]/60">
                    Inspecting {inspectedCluster.badge}
                  </span>
                </div>
                <h3 className="font-editorial text-2xl sm:text-3xl font-bold text-[#242725] mb-3">
                  {inspectedCluster.name}
                </h3>
                <p className="text-sm text-[#242725]/80 leading-relaxed mb-6">
                  {inspectedCluster.description}
                </p>

                {/* Distinguishing Characteristics */}
                <div className="mb-6">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#242725]/70 mb-3">
                    Measured Characteristics vs Population
                  </h4>
                  <ul className="space-y-2">
                    {inspectedCluster.characteristics.map((char, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-xs text-[#242725]/85">
                        <CheckCircle2 className="w-4 h-4 text-[#4f6955] shrink-0 mt-0.5" />
                        <span>{char}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Business Insight Callout */}
              <div className="lg:max-w-sm w-full bg-white p-6 rounded-lg border border-[#E0DED7] ">
                <div className="flex items-center gap-2 text-xs font-bold text-[#91563f] uppercase tracking-wider mb-2">
                  <Sparkles className="w-4 h-4" />
                  <span>Strategic Business Insight</span>
                </div>
                <p className="text-xs text-[#242725]/80 leading-relaxed mb-4">
                  {inspectedCluster.business_insight}
                </p>
                <div className="text-[11px] text-[#242725]/65 border-t border-[#F0EFEA] pt-3">
                  Note: Business insights are illustrative operational perspectives and are non-prescriptive.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
