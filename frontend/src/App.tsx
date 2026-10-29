import { useState, useEffect, lazy, Suspense } from 'react';
import { Navbar } from './components/Navbar';
import { SectionOverview } from './components/SectionOverview';
import { SectionPersonalities } from './components/SectionPersonalities';
const SectionClusterMap = lazy(() => import('./components/SectionClusterMap').then(m => ({ default: m.SectionClusterMap })));
const SectionBehindAI = lazy(() => import('./components/SectionBehindAI').then(m => ({ default: m.SectionBehindAI })));
import { SectionPredictor } from './components/SectionPredictor';
import { SectionMethodology } from './components/SectionMethodology';
import { Footer } from './components/Footer';

import {
  fetchOverview,
  fetchSegments,
  fetchEvaluation,
  fetchVisualization,
} from './services/api';

import type {
  DatasetOverview,
  SegmentProfile,
  EvaluationResponse,
  VisualizationResponse,
} from './types/api';

export function App() {
  const [overview, setOverview] = useState<DatasetOverview | null>(null);
  const [segments, setSegments] = useState<SegmentProfile[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationResponse | null>(null);
  const [visualization, setVisualization] = useState<VisualizationResponse | null>(null);
  const [selectedClusterId, setSelectedClusterId] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAllData() {
      setLoading(true);
      setError(null);
      try {
        const [ov, segs, ev, viz] = await Promise.all([
          fetchOverview(),
          fetchSegments(),
          fetchEvaluation(),
          fetchVisualization(5000),
        ]);
        setOverview(ov);
        setSegments(segs);
        setEvaluation(ev);
        setVisualization(viz);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to connect to ShopSense backend.');
      } finally {
        setLoading(false);
      }
    }

    loadAllData();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F6F2] text-[#242725]">
      <a href="#main" className="skip-link">Skip to content</a>
      <Navbar />

      <main id="main" className="flex-1">
        {loading ? <div role="status" className="p-12 text-center">Loading verified dataset and model results…</div> : error ? <div role="alert" className="p-12 text-center"><h1 className="font-editorial text-3xl mb-3">Analytics unavailable</h1><p className="mb-5">{error}</p><button className="px-4 py-2 border" onClick={() => window.location.reload()}>Retry connection</button></div> : <>
        <SectionOverview overview={overview} loading={loading} />
        <SectionPersonalities
          segments={segments}
          selectedClusterId={selectedClusterId}
          onSelectCluster={setSelectedClusterId}
        />
        <Suspense fallback={<p role="status" className="p-6">Loading customer explorer…</p>}>
        <SectionClusterMap
          data={visualization}
          segments={segments}
          loading={loading}
          selectedClusterId={selectedClusterId}
          onSelectCluster={setSelectedClusterId}
        />
        </Suspense>
        <Suspense fallback={<p role="status" className="p-6">Loading evaluation charts…</p>}>
        <SectionBehindAI evaluation={evaluation} segments={segments} />
        </Suspense>
        <SectionPredictor />
        <SectionMethodology overview={overview} />
        </>}
      </main>

      <Footer />
    </div>
  );
}

export default App;
