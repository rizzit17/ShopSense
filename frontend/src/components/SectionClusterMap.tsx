import React, { useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { VisualizationResponse, SegmentProfile, ScatterPoint } from '../types/api';
import { Info, Filter } from 'lucide-react';

interface Props {
  data: VisualizationResponse | null;
  segments: SegmentProfile[];
  loading: boolean;
  selectedClusterId: number | null;
  onSelectCluster: (clusterId: number | null) => void;
}

  // Custom Tooltip
  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: readonly { payload: ScatterPoint }[] }) => {
    if (active && payload && payload.length) {
      const pt = payload[0].payload;
      return (
        <div className="bg-[#242725] text-white p-3.5 rounded-lg  text-xs space-y-1.5 border border-[#3A3E3B] max-w-[220px]">
          <div className="font-bold flex items-center justify-between border-b border-[#3A3E3B] pb-1 mb-1">
            <span style={{ color: "#dce7dc" }}>{pt.segment_name}</span>
            <span className="text-gray-400 font-mono">#{pt.customer_id}</span>
          </div>
          <div className="text-gray-300 flex justify-between">
            <span>Recency:</span>
            <strong className="text-white">{pt.recency} days</strong>
          </div>
          <div className="text-gray-300 flex justify-between">
            <span>Frequency:</span>
            <strong className="text-white">{pt.frequency} orders</strong>
          </div>
          <div className="text-gray-300 flex justify-between">
            <span>Monetary:</span>
            <strong className="text-white">£{Number(pt.monetary).toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
          </div>
          <div className="text-[10px] text-gray-400 pt-1 border-t border-[#3A3E3B]">
            PCA: ({pt.pca1.toFixed(2)}, {pt.pca2.toFixed(2)})
          </div>
        </div>
      );
    }
    return null;
  };

export const SectionClusterMap: React.FC<Props> = ({
  data,
  segments,
  loading,
  selectedClusterId,
  onSelectCluster,
}) => {
  // Group points by cluster
  const pointsByCluster = useMemo(() => {
    if (!data?.points) return {};
    const map: Record<number, ScatterPoint[]> = {};
    for (const p of data.points) {
      if (!map[p.cluster_id]) map[p.cluster_id] = [];
      map[p.cluster_id].push(p);
    }
    return map;
  }, [data]);


  return (
    <section id="cluster-map" className="py-12 border-b border-[#EAE9E4]">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#4f6955] mb-2 block">
              Dimensionality Reduction
            </span>
            <h2 className="font-editorial text-3xl sm:text-4xl text-[#242725] font-bold tracking-tight">
              Interactive Cluster Projection (2D PCA)
            </h2>
          </div>
          <p className="text-sm text-[#242725]/70 max-w-md mt-3 md:mt-0 font-normal">
            Principal Component Analysis reduces the 3D RFM space into 2 dimensions for visualization,
            capturing <strong>{data?.pca_variance_pct ?? '—'}%</strong> of aggregate behavioral variance.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 mb-6">
          <span className="text-xs font-medium text-[#242725]/60 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Filter by:
          </span>
          <button
            onClick={() => onSelectCluster(null)}
            className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all ${
              selectedClusterId === null
                ? 'bg-[#242725] text-white '
                : 'bg-white border border-[#EAE9E4] text-[#242725]/70 hover:border-[#D0CEBE]'
            }`}
          >
            All Clusters ({data?.total_points ?? 0} customers)
          </button>
          {segments.map((seg) => {
            const isSelected = selectedClusterId === seg.cluster_id;
            return (
              <button
                key={seg.cluster_id}
                onClick={() => onSelectCluster(isSelected ? null : seg.cluster_id)}
                className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all flex items-center gap-1.5 ${
                  isSelected
                    ? 'ring-2 ring-offset-1 text-white '
                    : 'bg-white border border-[#EAE9E4] text-[#242725]/80 hover:border-[#D0CEBE]'
                }`}
                style={{
                  backgroundColor: isSelected ? seg.color : 'white',
                  borderColor: isSelected ? seg.color : '#EAE9E4',
                }}
              >
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: isSelected ? 'white' : seg.color }}
                ></span>
                {seg.name}
              </button>
            );
          })}
        </div>

        {/* Scatter Chart Container */}
        <div className="rounded-md bg-white border border-[#EAE9E4] p-6  relative">
          {loading ? (
            <div className="h-[440px] flex items-center justify-center text-sm text-[#242725]/60">
              Loading coordinate projection...
            </div>
          ) : (
            <div className="w-full h-[460px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F0EFEA" />
                  <XAxis
                    type="number"
                    dataKey="pca1"
                    name="Principal Component 1"
                    tick={{ fill: '#7A8288', fontSize: 11 }}
                    axisLine={{ stroke: '#EAE9E4' }}
                    tickLine={{ stroke: '#EAE9E4' }}
                    label={{
                      value: `PC1 (${((data?.pca_explained_variance_ratio[0] ?? 0) * 100).toFixed(1)}%)`,
                      position: 'insideBottom',
                      offset: -10,
                      fill: '#7A8288',
                      fontSize: 11,
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey="pca2"
                    name="Principal Component 2"
                    tick={{ fill: '#7A8288', fontSize: 11 }}
                    axisLine={{ stroke: '#EAE9E4' }}
                    tickLine={{ stroke: '#EAE9E4' }}
                    label={{
                      value: `PC2 (${((data?.pca_explained_variance_ratio[1] ?? 0) * 100).toFixed(1)}%)`,
                      angle: -90,
                      position: 'insideLeft',
                      offset: 10,
                      fill: '#7A8288',
                      fontSize: 11,
                    }}
                  />
                  <ZAxis range={[25, 25]} />
                  <Tooltip content={<CustomTooltip />} />

                  {segments.map((seg) => {
                    const pts = pointsByCluster[seg.cluster_id] || [];
                    const isDimmed = selectedClusterId !== null && selectedClusterId !== seg.cluster_id;
                    return (
                      <Scatter
                        isAnimationActive={false}
                        key={seg.cluster_id}
                        name={seg.name}
                        data={pts}
                        fill={seg.color}
                        opacity={isDimmed ? 0.08 : 0.65}
                      />
                    );
                  })}
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Educational Callout Footer */}
          <div className="mt-4 pt-4 border-t border-[#F0EFEA] flex items-start gap-2.5 text-xs text-[#242725]/65">
            <Info className="w-4 h-4 text-[#4f6955] shrink-0 mt-0.5" />
            <p>
              <strong>Academic Method Note:</strong> PCA is utilized strictly for 2D visualization of high-dimensional geometries.
              The primary K-Means model is trained on the three standardized, log-transformed RFM features (R, F, M).
              Hover over any point to inspect that customer&apos;s real RFM metrics.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
