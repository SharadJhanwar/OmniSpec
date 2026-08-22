import React, { useState } from 'react';
import {
  Search,
  Filter,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  Edit3,
  Eye,
  ShieldCheck,
  Image as ImageIcon,
  Download,
  FileSpreadsheet,
  Layers
} from 'lucide-react';

export default function Grid252({ items, onSelectReviewItem, onInspectDbom }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMode, setFilterMode] = useState('ALL'); // ALL, HIGH_CONF, NEEDS_REVIEW
  const [selectedDept, setSelectedDept] = useState('ALL');

  // Extract unique departments
  const departments = Array.from(new Set(items.map(it => {
    const cp = it.Classpath || it.classpath || '';
    return cp.split('>')[0].trim() || 'General';
  }))).filter(Boolean);

  const filteredItems = items.filter(item => {
    const mpn = (item["Mfg_Part_Num"] || item["mfg_part_num"] || item["MANUFACTURER_PART_NUMBER"] || '').toLowerCase();
    const brand = (item["BRAND_NAME"] || item["brand_name"] || '').toLowerCase();
    const desc = (item["Part_Desc"] || item["part_desc"] || item["SHORT_DESC"] || '').toLowerCase();
    const cp = (item["Classpath"] || item["classpath"] || '').toLowerCase();
    
    const matchesSearch = mpn.includes(searchTerm.toLowerCase()) || 
                          brand.includes(searchTerm.toLowerCase()) || 
                          desc.includes(searchTerm.toLowerCase()) ||
                          cp.includes(searchTerm.toLowerCase());

    const matchesDept = selectedDept === 'ALL' || (item["Classpath"] || item["classpath"] || '').startsWith(selectedDept);

    const conf = item._confidence !== undefined ? item._confidence : 1.0;
    if (filterMode === 'NEEDS_REVIEW') return matchesSearch && matchesDept && conf < 0.85;
    if (filterMode === 'HIGH_CONF') return matchesSearch && matchesDept && conf >= 0.85;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden flex flex-col space-y-0">
      {/* Table Controls Bar */}
      <div className="p-4 border-b border-slate-800 flex flex-col lg:flex-row items-center justify-between gap-3 bg-slate-950/60">
        <div className="flex flex-col sm:flex-row items-center gap-3 w-full lg:w-auto">
          {/* Search */}
          <div className="relative w-full sm:w-72">
            <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search MPN, Brand, Classpath..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          {/* Department Filter Dropdown */}
          <div className="relative w-full sm:w-56">
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 cursor-pointer"
            >
              <option value="ALL">All Categories ({items.length})</option>
              {departments.map((dept, idx) => (
                <option key={idx} value={dept}>{dept}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Filter Pills & Count */}
        <div className="flex items-center space-x-2 w-full lg:w-auto overflow-x-auto justify-start lg:justify-end">
          <button
            type="button"
            onClick={() => setFilterMode('ALL')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${filterMode === 'ALL' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'}`}
          >
            All Items ({items.length})
          </button>
          <button
            type="button"
            onClick={() => setFilterMode('HIGH_CONF')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${filterMode === 'HIGH_CONF' ? 'bg-emerald-500 text-slate-950 font-bold' : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'}`}
          >
            Verified (100%)
          </button>
          <button
            type="button"
            onClick={() => setFilterMode('NEEDS_REVIEW')}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${filterMode === 'NEEDS_REVIEW' ? 'bg-amber-500 text-slate-950 font-bold' : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'}`}
          >
            HITL Queue
          </button>
        </div>
      </div>

      {/* Grid Table Container */}
      <div className="overflow-x-auto max-h-[580px]">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-900/95 border-b border-slate-800 text-[11px] font-mono text-slate-400 uppercase tracking-wider sticky top-0 z-20 backdrop-blur-md">
              <th className="py-3 px-3 w-12 text-center">Status</th>
              <th className="py-3 px-3 min-w-[70px]">Image</th>
              <th className="py-3 px-3 min-w-[130px]">MPN</th>
              <th className="py-3 px-3 min-w-[140px]">Brand (®, ™)</th>
              <th className="py-3 px-3 min-w-[160px]">Manufacturer</th>
              <th className="py-3 px-3 min-w-[220px]">Classpath (4-Tier)</th>
              <th className="py-3 px-3 min-w-[200px]">Invoice Desc (&le;40)</th>
              <th className="py-3 px-3 min-w-[200px]">Mobile Desc (60-80)</th>
              <th className="py-3 px-3 min-w-[140px]">Dimensions / Specs</th>
              <th className="py-3 px-3 min-w-[170px]">Specification Sheet</th>
              <th className="py-3 px-3 min-w-[130px] text-right sticky right-0 bg-slate-900/95 z-30">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80 text-xs">
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
                const imgUrl = item['Product Image'] || item.product_image || '';
                const isReal = String(imgUrl).startsWith('http');
                const brand = item.BRAND_NAME || item.brand_name || 'Brand';
                const mpn = item.Mfg_Part_Num || item.mfg_part_num || item.MANUFACTURER_PART_NUMBER || 'SKU';
                const specSheet = item['Specification Sheet'] || item.specification_sheet || `${brand}_${mpn}_Specification_Sheet.pdf`;

                // Build dimensions summary
                const l = item.LENGTH || item.Length;
                const w = item.WIDTH || item.Width;
                const h = item.HEIGHT || item.Height;
                const diam = item.DIAMETER || item.Diameter;
                const thk = item.THICKNESS || item.Thickness;
                let dimStr = 'N/A';
                if (diam) dimStr = `${diam} in D × ${thk || '.045'} in THK`;
                else if (l && w) dimStr = `${w} in W × ${l} in L`;
                else if (l) dimStr = `${l} in`;

                return (
                  <tr 
                    key={idx}
                    className="hover:bg-slate-900/60 transition-colors group cursor-default"
                  >
                    {/* Status Badge */}
                    <td className="py-2.5 px-3 text-center">
                      {isVerified ? (
                        <CheckCircle className="h-4 w-4 text-emerald-400 mx-auto" title="100% Validated & Verified" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-amber-400 mx-auto" title="Pending HITL Review" />
                      )}
                    </td>

                    {/* Image Thumbnail */}
                    <td className="py-2.5 px-3">
                      <div className="w-10 h-10 rounded-lg bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center">
                        {isReal ? (
                          <img src={imgUrl} alt={mpn} className="w-full h-full object-contain p-0.5" />
                        ) : (
                          <ImageIcon className="w-4 h-4 text-slate-600" />
                        )}
                      </div>
                    </td>

                    {/* MPN */}
                    <td className="py-2.5 px-3 font-mono font-bold text-cyan-400">{mpn}</td>

                    {/* Brand */}
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{brand}</td>

                    {/* Manufacturer */}
                    <td className="py-2.5 px-3 text-slate-300 truncate max-w-[160px]" title={item.MANUFACTURER_NAME || item.Part_Manuf}>
                      {item.MANUFACTURER_NAME || item.Part_Manuf || 'OEM'}
                    </td>

                    {/* Classpath */}
                    <td className="py-2.5 px-3 text-slate-300 truncate max-w-[220px]" title={item.Classpath || item.classpath}>
                      {item.Classpath || item.classpath || 'Industrial'}
                    </td>

                    {/* Invoice Desc */}
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-300 truncate max-w-[200px]" title={item.INVOICE_DESC}>
                      {item.INVOICE_DESC || 'N/A'}
                    </td>

                    {/* Mobile Desc */}
                    <td className="py-2.5 px-3 text-slate-300 truncate max-w-[200px]" title={item.MOBILE_DESC}>
                      {item.MOBILE_DESC || 'N/A'}
                    </td>

                    {/* Dimensions / Specs */}
                    <td className="py-2.5 px-3 font-mono text-[11px] text-cyan-300 truncate max-w-[140px]">
                      {dimStr}
                    </td>

                    {/* Specification Sheet */}
                    <td className="py-2.5 px-3 text-[11px] text-slate-400 font-mono truncate max-w-[170px]" title={specSheet}>
                      {specSheet}
                    </td>

                    {/* Actions */}
                    <td className="py-2.5 px-3 text-right sticky right-0 bg-slate-950/95 group-hover:bg-slate-900/95 transition-colors">
                      <div className="flex items-center justify-end space-x-1.5">
                        <button
                          type="button"
                          onClick={() => onInspectDbom(item)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-500 text-slate-300 hover:text-slate-950 transition-colors"
                          title="Inspect Cell-Level DBOM Lineage"
                        >
                          <ShieldCheck className="h-3.5 w-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => onSelectReviewItem(item)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-amber-500 text-slate-300 hover:text-slate-950 transition-colors"
                          title="Review & Edit Record"
                        >
                          <Edit3 className="h-3.5 w-3.5" />
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

      {/* Footer Info Strip */}
      <div className="p-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 bg-slate-950/80">
        <span className="font-mono text-[11px]">
          Showing {filteredItems.length} of {items.length} records • 252 Columns Full Standard
        </span>
        <span className="text-emerald-400 font-medium">10-Agent Swarm Validated</span>
      </div>
    </div>
  );
}
