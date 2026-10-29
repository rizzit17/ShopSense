import React from 'react';

export const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 bg-[#F7F6F2] border-b border-[#EAE9E4]">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#242725] text-[#F7F6F2] flex items-center justify-center font-editorial text-lg font-bold">
            S
          </div>
          <div>
            <span className="font-editorial text-xl font-bold tracking-tight text-[#242725]">ShopSense</span>
            <span className="hidden sm:inline-block ml-2 text-xs font-medium text-[#4f6955] uppercase tracking-wider">
              AI Case Study
            </span>
          </div>
        </div>

        <nav className="hidden lg:flex items-center gap-7 text-sm font-medium text-[#242725]/80">
          <a href="#overview" className="hover:text-[#242725] transition-colors">Overview</a>
          <a href="#personalities" className="hover:text-[#242725] transition-colors">Personalities</a>
          <a href="#cluster-map" className="hover:text-[#242725] transition-colors">Cluster Map</a>
          <a href="#behind-ai" className="hover:text-[#242725] transition-colors">Behind the AI</a>
          <a href="#predictor" className="hover:text-[#242725] transition-colors">Predictor</a>
          <a href="#methodology" className="hover:text-[#242725] transition-colors">Methodology</a>
        </nav>

        <div className="flex items-center gap-3">
          <a
            href="#predictor"
            className="text-xs sm:text-sm font-medium px-3.5 py-1.5 rounded-md bg-[#242725] text-[#F7F6F2] hover:bg-[#343835] transition-colors"
          >
            Try Predictor
          </a>
        </div>
      </div>
    </header>
  );
};
