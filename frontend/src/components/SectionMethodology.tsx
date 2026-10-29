import React from 'react';
import type { DatasetOverview } from '../types/api';
import { Database, FileText, ShieldCheck, ExternalLink } from 'lucide-react';

interface Props {
  overview: DatasetOverview | null;
}

export const SectionMethodology: React.FC<Props> = ({ overview }) => {
  return (
    <section id="methodology" className="py-12">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <div className="max-w-3xl mb-8">
          <span className="text-xs font-bold uppercase tracking-wider text-[#4f6955] mb-2 block">
            Academic Reproducibility
          </span>
          <h2 className="font-editorial text-3xl sm:text-4xl text-[#242725] font-bold tracking-tight mb-4">
            Dataset & Cleaning Audit Trail
          </h2>
          <p className="text-sm text-[#242725]/75 leading-relaxed font-normal">
            Academic credibility requires complete transparency into how raw records were inspected, filtered,
            and transformed. Every excluded row is accounted for in the table below.
          </p>
        </div>

        <ol aria-label="Methodology workflow" className="flex flex-wrap gap-2 mb-8">
          {['Dataset', 'Cleaning', 'RFM', 'Log1p + scaling', 'K-Means', 'Evaluation', 'Segments'].map((step, i) => <li key={step} className="text-xs border border-[#deddd5] bg-white px-3 py-2"><span className="text-[#4f6955] mr-2">{i + 1}</span>{step}</li>)}
        </ol>
        {/* Cleaning Audit Table */}
        <div className="rounded-md bg-white border border-[#EAE9E4] overflow-hidden  mb-10">
          <div className="p-5 bg-[#FAF9F5] border-b border-[#EAE9E4] flex flex-wrap items-center justify-between gap-4">
            <div>
              <h3 className="font-editorial text-base font-bold text-[#242725]">
                Sequential Cleaning Audit
              </h3>
              <p className="text-xs text-[#242725]/60">
                UCI Online Retail Dataset ID 352 &bull; Original row count: {overview?.total_raw_rows.toLocaleString() ?? '—'}
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="px-2.5 py-1 rounded-full bg-[#718776]/10 text-[#4f6955] font-semibold">
                Retention: {overview?.retention_rate_pct ?? '—'}%
              </span>
              <span className="px-2.5 py-1 rounded-full bg-[#242725]/5 text-[#242725]/70 font-semibold">
                Valid Customers: {overview?.total_customers.toLocaleString() ?? '—'}
              </span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAF9F5] text-[#242725]/70 uppercase font-bold border-b border-[#EAE9E4]">
                <tr>
                  <th className="py-3 px-5">Filter Step</th>
                  <th className="py-3 px-5">Excluded Rows</th>
                  <th className="py-3 px-5">Remaining Rows</th>
                  <th className="py-3 px-5">Academic Justification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F0EFEA]">
                {overview?.cleaning_steps.map((step) => (
                  <tr key={step.step} className="hover:bg-[#FAF9F5]/60 transition-colors">
                    <td className="py-3 px-5 font-semibold text-[#242725]">
                      Step {step.step}: {step.name}
                    </td>
                    <td className="py-3 px-5 text-[#91563f] font-semibold">
                      -{step.excluded.toLocaleString()}
                    </td>
                    <td className="py-3 px-5 text-[#242725] font-mono">
                      {step.remaining.toLocaleString()}
                    </td>
                    <td className="py-3 px-5 text-[#242725]/70">
                      {step.description}
                    </td>
                  </tr>
                ))}
                <tr className="bg-[#FAF9F5] font-bold">
                  <td className="py-3.5 px-5 text-[#242725]">
                    Final Clean Transactions
                  </td>
                  <td className="py-3.5 px-5 text-[#91563f]">
                    -{((overview?.total_raw_rows ?? 0) - (overview?.total_clean_rows ?? 0)).toLocaleString()} Total Excluded
                  </td>
                  <td className="py-3.5 px-5 text-[#2E5A44] font-mono">
                    {overview?.total_clean_rows.toLocaleString() ?? '—'} Rows
                  </td>
                  <td className="py-3.5 px-5 text-[#2E5A44]">
                    Aggregated into {overview?.total_customers.toLocaleString()} customer RFM profiles
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* 3-Column Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-lg bg-white border border-[#EAE9E4] ">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#4f6955] mb-3">
              <Database className="w-4 h-4" /> Dataset Attribution
            </div>
            <h4 className="font-editorial text-base font-bold text-[#242725] mb-2">
              UCI Machine Learning Repository
            </h4>
            <p className="text-xs text-[#242725]/70 leading-relaxed mb-4">
              Daqing Chen (2015), Online Retail, DOI: 10.24432/C5BW33. CC BY 4.0. Non-store online retail giftware dataset from the UK,
              spanning Dec 1, 2010 to Dec 9, 2011.
            </p>
            <a
              href="https://archive.ics.uci.edu/dataset/352/online+retail"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-[#4f6955] font-semibold hover:underline"
            >
              Official Dataset Source <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>

          <div className="p-6 rounded-lg bg-white border border-[#EAE9E4] ">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#4f6955] mb-3">
              <FileText className="w-4 h-4" /> Feature Formulations
            </div>
            <h4 className="font-editorial text-base font-bold text-[#242725] mb-2">
              Standardized RFM Metrics
            </h4>
            <ul className="text-xs text-[#242725]/70 space-y-1.5 leading-relaxed">
              <li><strong>Recency:</strong> Reference Date (10 Dec 2011) - Max InvoiceDate</li>
              <li><strong>Frequency:</strong> Count of unique completed invoice IDs</li>
              <li><strong>Monetary:</strong> Sum of (Quantity &times; UnitPrice) in GBP</li>
            </ul>
          </div>

          <div className="p-6 rounded-lg bg-white border border-[#EAE9E4] ">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#4f6955] mb-3">
              <ShieldCheck className="w-4 h-4" /> Academic Integrity
            </div>
            <h4 className="font-editorial text-base font-bold text-[#242725] mb-2">
              Traceable results
            </h4>
            <p className="text-xs text-[#242725]/70 leading-relaxed">
              Every customer profile, centroid, silhouette metric, and chart point originates directly from the
              underlying 23.7 MB Excel dataset processed locally via Pandas and Scikit-learn.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
