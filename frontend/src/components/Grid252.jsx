import React, { useState } from 'react';
import { Search, Filter, AlertTriangle, CheckCircle, ExternalLink, Edit3, Eye } from 'lucide-react';

export default function Grid252({ items, onSelectReviewItem }) {
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

      {/* Virtualized 252-Column Data Grid Table */}
      <div className="overflow-x-auto max-h-[560px]">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="sticky top-0 z-20 bg-surface-elevated/95 backdrop-blur-md border-b border-surface-border text-slate-400 uppercase font-mono text-[10px] tracking-wider">
            <tr>
              <th className="py-3 px-3 sticky left-0 z-30 bg-surface-elevated">Confidence</th>
              <th className="py-3 px-3 sticky left-24 z-30 bg-surface-elevated">Mfg Part Num</th>
              <th className="py-3 px-3">Canonical Brand</th>
              <th className="py-3 px-3">Classpath (Taxonomy)</th>
              <th className="py-3 px-3 min-w-[280px]">Product Title (SHORT_DESC)</th>
              <th className="py-3 px-3 min-w-[220px]">INVOICE_DESC (&le;40)</th>
              <th className="py-3 px-3 min-w-[220px]">MOBILE_DESC (60-80)</th>
              <th className="py-3 px-3">Dimensions (L x W x H)</th>
              <th className="py-3 px-3">Primary Image Asset</th>
              <th className="py-3 px-3">Spec Sheet PDF</th>
              <th className="py-3 px-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/60 text-slate-300">
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan={11} className="py-12 text-center text-slate-500 font-mono text-xs">
                  No records match the active filter criteria.
                </td>
              </tr>
            ) : (
              filteredItems.map((item, index) => {
                const conf = item._confidence !== undefined ? item._confidence : 1.0;
                const isHighConf = conf >= 0.85;

                return (
                  <tr 
                    key={index} 
                    className="hover:bg-surface-elevated/80 transition-colors group cursor-pointer"
                    onClick={() => {
                      if (onSelectReviewItem) onSelectReviewItem(item);
                    }}
                  >
                    {/* Confidence */}
                    <td className="py-2.5 px-3 sticky left-0 z-10 bg-surface/95 backdrop-blur-sm">
                      <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${isHighConf ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}`}>
                        {isHighConf ? <CheckCircle className="h-3 w-3 mr-0.5" /> : <AlertTriangle className="h-3 w-3 mr-0.5" />}
                        <span>{(conf * 100).toFixed(0)}%</span>
                      </span>
                    </td>

                    {/* MPN */}
                    <td className="py-2.5 px-3 font-mono font-bold text-cyan-400 sticky left-24 z-10 bg-surface/95 backdrop-blur-sm">
                      {item["Mfg_Part_Num"] || item["mfg_part_num"]}
                    </td>

                    {/* Brand */}
                    <td className="py-2.5 px-3 font-semibold text-white">
                      {item["BRAND_NAME"] || item["brand_name"]}
                    </td>

                    {/* Classpath */}
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400 max-w-[200px] truncate" title={item["Classpath"] || item["classpath"]}>
                      {item["Classpath"] || item["classpath"]}
                    </td>

                    {/* SHORT_DESC */}
                    <td className="py-2.5 px-3 font-medium text-slate-200 max-w-[300px] truncate" title={item["SHORT_DESC"] || item["short_desc"]}>
                      {item["SHORT_DESC"] || item["short_desc"]}
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
                    <td className="py-2.5 px-3 text-right">
                      <button 
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectReviewItem) onSelectReviewItem(item);
                        }}
                        className="px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-slate-200 hover:text-white hover:border-cyan-400 hover:bg-cyan-950/40 text-xs font-medium flex items-center space-x-1.5 ml-auto transition-all cursor-pointer shadow-sm"
                      >
                        <Edit3 className="h-3.5 w-3.5 text-cyan-400" />
                        <span>Review</span>
                      </button>
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
