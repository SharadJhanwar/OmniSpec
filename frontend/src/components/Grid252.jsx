import React, { useState } from 'react';
import { Search, Filter, AlertTriangle, CheckCircle, ExternalLink, Edit3, Eye, ShieldCheck } from 'lucide-react';

export default function Grid252({ items, onSelectReviewItem, onInspectDbom }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMode, setFilterMode] = useState('ALL'); // ALL, HIGH_CONF, NEEDS_REVIEW

  const filteredItems = items.filter(item => {
    const mpn = (item["Mfg_Part_Num"] || item["mfg_part_num"] || '').toLowerCase();
    const brand = (item["BRAND_NAME"] || item["brand_name"] || '').toLowerCase();
    const desc = (item["Part_Desc"] || item["part_desc"] || '').toLowerCase();
    const matchesSearch = mpn.includes(searchTerm.toLowerCase()) || 
                          brand.includes(searchTerm.toLowerCase()) || 
                          desc.includes(searchTerm.toLowerCase());

    const conf = item._confidence !== undefined ? item._confidence : 1.0;
    if (filterMode === 'NEEDS_REVIEW') return matchesSearch && conf < 0.85;
    if (filterMode === 'HIGH_CONF') return matchesSearch && conf >= 0.85;
    return matchesSearch;
  });

  return (
    <div className="glass-panel rounded-xl overflow-hidden flex flex-col">
      {/* Table Controls Bar */}
      <div className="p-4 border-b border-surface-border flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by MPN, Brand, or Keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto">
          <button
            type="button"
            onClick={() => setFilterMode('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${filterMode === 'ALL' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-surface text-slate-400 hover:text-slate-200'}`}
          >
            All Items ({items.length})
          </button>
          <button
            type="button"
            onClick={() => setFilterMode('HIGH_CONF')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${filterMode === 'HIGH_CONF' ? 'bg-emerald-500 text-slate-950 font-bold' : 'bg-surface text-slate-400 hover:text-slate-200'}`}
          >
            Verified (100%)
          </button>
          <button
            type="button"
            onClick={() => setFilterMode('NEEDS_REVIEW')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${filterMode === 'NEEDS_REVIEW' ? 'bg-amber-500 text-slate-950 font-bold' : 'bg-surface text-slate-400 hover:text-slate-200'}`}
          >
            HITL Review Queue
          </button>
        </div>
      </div>

      {/* Grid Table Container */}
      <div className="overflow-x-auto max-h-[520px]">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-900/90 border-b border-surface-border text-[11px] font-mono text-slate-400 uppercase tracking-wider sticky top-0 z-20 backdrop-blur-md">
              <th className="py-3 px-3 w-12 text-center">Status</th>
              <th className="py-3 px-3 min-w-[140px]">MPN</th>
              <th className="py-3 px-3 min-w-[150px]">Brand (®, ™)</th>
              <th className="py-3 px-3 min-w-[180px]">Manufacturer</th>
              <th className="py-3 px-3 min-w-[240px]">Classpath (4-Tier)</th>
              <th className="py-3 px-3 min-w-[220px]">Invoice Desc (≤40)</th>
              <th className="py-3 px-3 min-w-[220px]">Mobile Desc (60-80)</th>
              <th className="py-3 px-3 min-w-[140px]">Dimensions (L×W×H)</th>
              <th className="py-3 px-3 min-w-[160px]">Product Image</th>
              <th className="py-3 px-3 min-w-[180px]">Specification Sheet</th>
              <th className="py-3 px-3 min-w-[150px] text-right sticky right-0 bg-slate-900/95 z-30">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border text-xs">
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan="11" className="py-12 text-center text-slate-500">
                  No products match the selected criteria.
                </td>
              </tr>
            ) : (
              filteredItems.map((item, idx) => {
                const conf = item._confidence !== undefined ? item._confidence : 1.0;
                const isVerified = conf >= 0.85;

                return (
                  <tr 
                    key={idx}
                    className="hover:bg-slate-900/50 transition-colors group cursor-default"
                  >
                    {/* Status Badge */}
                    <td className="py-2.5 px-3 text-center">
                      {isVerified ? (
                        <div className="flex items-center justify-center text-emerald-400" title="100% Verified Ground Truth">
                          <CheckCircle className="h-4 w-4" />
                        </div>
                      ) : (
                        <div className="flex items-center justify-center text-amber-400" title="Flagged for HITL Review">
                          <AlertTriangle className="h-4 w-4" />
                        </div>
                      )}
                    </td>

                    {/* MPN */}
                    <td className="py-2.5 px-3 font-mono font-bold text-cyan-400">
                      {item["Mfg_Part_Num"] || item["mfg_part_num"] || item["PART_NUMBER"] || '—'}
                    </td>

                    {/* Brand */}
                    <td className="py-2.5 px-3 font-semibold text-white">
                      {item["BRAND_NAME"] || item["brand_name"] || '—'}
                    </td>

                    {/* Manufacturer */}
                    <td className="py-2.5 px-3 text-slate-300">
                      {item["MANUFACTURER_NAME"] || item["manufacturer_name"] || '—'}
                    </td>

                    {/* Classpath */}
                    <td className="py-2.5 px-3 text-slate-400 text-[11px] max-w-[240px] truncate" title={item["Classpath"] || item["classpath"]}>
                      {item["Classpath"] || item["classpath"] || '—'}
                    </td>

                    {/* INVOICE_DESC */}
                    <td className="py-2.5 px-3 font-mono text-[11px] text-amber-300 max-w-[220px] truncate">
                      {item["INVOICE_DESC"] || item["invoice_desc"]}
                    </td>

                    {/* MOBILE_DESC */}
                    <td className="py-2.5 px-3 text-slate-300 max-w-[220px] truncate">
                      {item["MOBILE_DESC"] || item["mobile_desc"]}
                    </td>

                    {/* Dimensions */}
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">
                      {item["LENGTH"] || item["length"] ? `${item["LENGTH"] || item["length"]} x ${item["WIDTH"] || item["width"] || '0'} x ${item["HEIGHT"] || item["height"] || '0'} in` : '—'}
                    </td>

                    {/* Product Image */}
                    <td className="py-2.5 px-3 font-mono text-[11px] text-cyan-400">
                      {item["Product Image"] || item["product_image"]}
                    </td>

                    {/* Spec Sheet PDF */}
                    <td className="py-2.5 px-3 font-mono text-[11px] text-sky-400">
                      {item["Specification Sheet"] || item["specification_sheet"]}
                    </td>

                    {/* Actions */}
                    <td className="py-2.5 px-3 text-right sticky right-0 bg-slate-950/90 group-hover:bg-slate-900/90 transition-colors z-10">
                      <div className="flex items-center justify-end space-x-1.5">
                        {onInspectDbom && (
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              onInspectDbom(item);
                            }}
                            className="px-2 py-1.5 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 text-xs font-mono font-semibold flex items-center space-x-1 transition-all cursor-pointer"
                            title="Inspect Data Bill of Materials (DBOM) and Lineage"
                          >
                            <ShieldCheck className="h-3.5 w-3.5" />
                            <span>DBOM</span>
                          </button>
                        )}
                        <button 
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onSelectReviewItem) onSelectReviewItem(item);
                          }}
                          className="px-2.5 py-1.5 rounded-lg bg-surface border border-surface-border text-slate-200 hover:text-white hover:border-cyan-400 hover:bg-cyan-950/40 text-xs font-medium flex items-center space-x-1 transition-all cursor-pointer shadow-sm"
                        >
                          <Edit3 className="h-3.5 w-3.5 text-cyan-400" />
                          <span>Review</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
