import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[#EAE9E4] bg-[#F2F1EC] py-12 text-[#242725]/75">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-editorial text-lg font-bold text-[#242725]">ShopSense</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-[#718776]/15 text-[#4f6955] font-medium">
              Academic Case Study
            </span>
          </div>
          <p className="text-xs text-[#242725]/60 max-w-md">
            Department of Artificial Intelligence &bull; School of Computer Science and Engineering &bull; Vellore Institute of Technology
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs font-medium">
          <div className="text-xs text-[#242725]/60">
            Coursework: Artificial Intelligence &bull; Unsupervised customer segmentation
          </div>
        </div>
      </div>
    </footer>
  );
};
