import React, { useState } from 'react';
import {
  Image as ImageIcon,
  ExternalLink,
  FileText,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Eye,
  X,
  Sparkles,
  Maximize2
} from 'lucide-react';

export default function VisualAssetGallery({ items = [], onInspectDbom }) {
  const [selectedImage, setSelectedImage] = useState(null);

  // Filter items that have image assets or real discovered URLs
  const visualItems = items.filter(it => it && (it['Product Image'] || it.product_image || it.Mfg_Part_Num));

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 text-cyan-400">
            <ImageIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-slate-100">Live Sourced Digital Assets & Real Image Gallery</h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-medium">
                DuckDuckGo Image Discovery
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Real product photography discovered via OEM web discovery, filtered against banned marketplaces
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Actual Sourced: {items.filter(it => it['Actual Image (Yes/No)'] === 'Yes' || (it['Product Image'] && String(it['Product Image']).startsWith('http'))).length}
          </span>
          <span className="text-slate-600">•</span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            Canonical Naming: {items.filter(it => it['Actual Image (Yes/No)'] !== 'Yes' && !(it['Product Image'] && String(it['Product Image']).startsWith('http'))).length}
          </span>
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {visualItems.slice(0, 8).map((item, idx) => {
          const imgUrl = item['Product Image'] || item.product_image || '';
          const isRealUrl = String(imgUrl).startsWith('http');
          const brand = item.BRAND_NAME || item.brand_name || 'Brand';
          const mpn = item.Mfg_Part_Num || item.mfg_part_num || item.MANUFACTURER_PART_NUMBER || 'SKU';
          const specSheet = item['Specification Sheet'] || item.specification_sheet || `${brand}_${mpn}_Specification_Sheet.pdf`;
          const actualImg = item['Actual Image (Yes/No)'] === 'Yes' || isRealUrl;

          return (
            <div
              key={idx}
              className="group rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 p-4 transition-all duration-300 flex flex-col justify-between hover:shadow-lg hover:shadow-cyan-950/20"
            >
              {/* Image Preview Container */}
              <div className="relative aspect-square w-full rounded-lg bg-slate-950 border border-slate-800/80 overflow-hidden flex items-center justify-center mb-3">
                {isRealUrl ? (
                  <img
                    src={imgUrl}
                    alt={`${brand} ${mpn}`}
                    className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = 'https://placehold.co/400x400/0f172a/38bdf8?text=' + encodeURIComponent(brand + ' ' + mpn);
                    }}
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center text-slate-500 p-4 text-center">
                    <ImageIcon className="w-10 h-10 mb-2 text-slate-600 group-hover:text-cyan-400 transition-colors" />
                    <span className="text-[11px] font-mono text-slate-400 break-all">{imgUrl || `${brand}_${mpn}.jpg`}</span>
                    <span className="text-[10px] text-slate-500 mt-1">Canonical Naming Standard</span>
                  </div>
                )}

                {/* Sourcing Badge */}
                <div className="absolute top-2 left-2">
                  {actualImg ? (
                    <span className="flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-950/90 text-emerald-400 border border-emerald-800 shadow-sm backdrop-blur-md">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      Live Sourced
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-900/90 text-slate-400 border border-slate-700 shadow-sm backdrop-blur-md">
                      Canonical Naming
                    </span>
                  )}
                </div>

                {/* Zoom Button Overlay */}
                {isRealUrl && (
                  <button
                    onClick={() => setSelectedImage({ url: imgUrl, title: `${brand} ${mpn}`, specSheet })}
                    className="absolute bottom-2 right-2 p-1.5 rounded-lg bg-slate-900/80 hover:bg-cyan-500 text-slate-300 hover:text-slate-950 transition-colors opacity-0 group-hover:opacity-100 shadow-md backdrop-blur-md"
                    title="View Full Size Image"
                  >
                    <Maximize2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Product Info */}
              <div className="space-y-2 flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-xs font-bold text-cyan-400 truncate">{brand}</span>
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">{mpn}</span>
                  </div>
                  <p className="text-xs text-slate-300 line-clamp-2 mt-1 font-medium">
                    {item.SHORT_DESC || item.short_desc || item.Part_Desc || item.part_desc || 'Industrial Product'}
                  </p>
                </div>

                {/* Asset Metadata Row */}
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                  <div className="flex items-center gap-1 truncate" title={specSheet}>
                    <FileText className="w-3 h-3 text-slate-400 flex-shrink-0" />
                    <span className="truncate max-w-[120px]">{specSheet}</span>
                  </div>

                  {onInspectDbom && (
                    <button
                      onClick={() => onInspectDbom(item)}
                      className="text-[10px] text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-0.5"
                    >
                      <ShieldCheck className="w-3 h-3" />
                      DBOM
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Lightbox Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="relative max-w-2xl w-full bg-slate-900 rounded-2xl border border-slate-700 shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h4 className="text-base font-bold text-slate-100">{selectedImage.title}</h4>
                <p className="text-xs text-slate-400 font-mono break-all">{selectedImage.url}</p>
              </div>
              <button
                onClick={() => setSelectedImage(null)}
                className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="w-full h-80 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center overflow-hidden p-4">
              <img
                src={selectedImage.url}
                alt={selectedImage.title}
                className="w-full h-full object-contain"
              />
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2 className="w-4 h-4" /> Live Web Evidence Sourced
              </span>
              <a
                href={selectedImage.url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-cyan-400 hover:underline"
              >
                Open Original Asset <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
