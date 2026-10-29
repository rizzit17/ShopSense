import React from 'react';
import { Users, CreditCard, ShoppingBag, PieChart, ArrowUpRight, Calendar, Database } from 'lucide-react';
import type { DatasetOverview } from '../types/api';

interface Props {
  overview: DatasetOverview | null;
  loading: boolean;
}

export const SectionOverview: React.FC<Props> = ({ overview, loading }) => {
  return (
    <section id="overview" className="pt-12 pb-16 border-b border-[#EAE9E4]">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header Block */}
        <div className="max-w-3xl mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#718776]/15 text-[#4f6955] text-xs font-semibold uppercase tracking-wider mb-4">
            B.Tech AI Coursework &bull; Unsupervised Learning Case Study
          </div>
          <h1 className="font-editorial text-3xl sm:text-4xl lg:text-5xl text-[#242725] font-bold tracking-tight leading-[1.15] mb-6">
            Every purchase tells a story.
          </h1>
          <p className="text-base sm:text-lg text-[#242725]/75 leading-relaxed font-normal">
            ShopSense demonstrates how unsupervised K-Means clustering, combined with Recency, Frequency,
            and Monetary (RFM) behavioral analysis, discovers distinct shopping personalities from real transaction logs
            without predefined labels.
          </p>
        </div>

        {/* Real KPI Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Stat 1 */}
          <div className="p-6 rounded-lg bg-white/70 border border-[#EAE9E4] ">
            <div className="flex items-center justify-between text-[#4f6955] mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-[#242725]/60">Valid Customers</span>
              <Users className="w-4 h-4" />
            </div>
            <div className="text-3xl font-bold font-editorial text-[#242725] mb-1">
              {loading || !overview ? '—' : overview.total_customers.toLocaleString()}
            </div>
            <p className="text-xs text-[#242725]/60">
              Aggregated from {loading || !overview ? '—' : overview.total_clean_rows.toLocaleString()} valid transaction lines
            </p>
          </div>

          {/* Stat 2 */}
          <div className="p-6 rounded-lg bg-white/70 border border-[#EAE9E4] ">
            <div className="flex items-center justify-between text-[#4f6955] mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-[#242725]/60">Recorded Spending</span>
              <CreditCard className="w-4 h-4" />
            </div>
            <div className="text-3xl font-bold font-editorial text-[#242725] mb-1">
              {loading || !overview ? '—' : `£${(overview.total_revenue_gbp / 1_000_000).toFixed(2)}M`}
            </div>
            <p className="text-xs text-[#242725]/60">
              Total transaction value in British Pounds (GBP)
            </p>
          </div>

          {/* Stat 3 */}
          <div className="p-6 rounded-lg bg-white/70 border border-[#EAE9E4] ">
            <div className="flex items-center justify-between text-[#4f6955] mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-[#242725]/60">Completed Orders</span>
              <ShoppingBag className="w-4 h-4" />
            </div>
            <div className="text-3xl font-bold font-editorial text-[#242725] mb-1">
              {loading || !overview ? '—' : overview.total_orders.toLocaleString()}
            </div>
            <p className="text-xs text-[#242725]/60">
              Distinct completed non-cancelled purchase invoices
            </p>
          </div>

          {/* Stat 4 */}
          <div className="p-6 rounded-lg bg-white/70 border border-[#EAE9E4] ">
            <div className="flex items-center justify-between text-[#91563f] mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-[#242725]/60">Discovered Clusters</span>
              <PieChart className="w-4 h-4" />
            </div>
            <div className="text-3xl font-bold font-editorial text-[#242725] mb-1">
              {loading || !overview ? '—' : overview.discovered_segments_count}
            </div>
            <p className="text-xs text-[#242725]/60">
              Interpretable granularity after evaluating K=2–8
            </p>
          </div>
        </div>

        {/* Dataset Metadata Strip */}
        <div className="p-4 rounded-md bg-[#F2F1EC] border border-[#E5E4DE] flex flex-wrap items-center justify-between gap-4 text-xs text-[#242725]/75">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-[#4f6955]" />
            <span>Dataset: <strong>UCI Online Retail (Dataset ID 352)</strong> &bull; Non-store online giftware retailer</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-[#4f6955]" />
            <span>Recorded Period: <strong>01 Dec 2010 – 09 Dec 2011</strong> &bull; Fixed Reference Horizon: <strong>10 Dec 2011</strong></span>
          </div>
          <a
            href="https://archive.ics.uci.edu/dataset/352/online+retail"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-[#4f6955] hover:text-[#242725] font-semibold underline underline-offset-2"
          >
            UCI Archive <ArrowUpRight className="w-3 h-3" />
          </a>
        </div>
      </div>
    </section>
  );
};
