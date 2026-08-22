import React, { useState } from 'react';
import { ShieldAlert, CheckCircle2, AlertTriangle, ArrowRight, Save, Check, RefreshCw, Sparkles, BookOpen, Layers } from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';
import { apiUrl } from '../config/api';

export default function ReviewPage() {
  const { items, handleSaveReviewedItem, handleOpenDbom } = useCatalog();

  // Filter items needing review or display full catalog with filter
  const [filterMode, setFilterMode] = useState('ALL'); // 'ALL' or 'PENDING'
  const [searchTerm, setSearchTerm] = useState('');
  
  const pendingItems = items.filter(it => (it._confidence !== undefined ? it._confidence : 1.0) < 0.90 || it._needs_hitl);
  const displayedItems = (filterMode === 'PENDING' ? pendingItems : items).filter(it => {
    const q = searchTerm.toLowerCase();
    const mpn = (it.Mfg_Part_Num || it.mfg_part_num || '').toLowerCase();
    const brand = (it.BRAND_NAME || it.brand_name || '').toLowerCase();
    const desc = (it.Part_Desc || it.SHORT_DESC || '').toLowerCase();
    return mpn.includes(q) || brand.includes(q) || desc.includes(q);
  });

  const [selectedMpn, setSelectedMpn] = useState(displayedItems[0]?.Mfg_Part_Num || items[0]?.Mfg_Part_Num || '');
  const activeItem = items.find(it => (it.Mfg_Part_Num || it.mfg_part_num) === selectedMpn) || displayedItems[0] || items[0];

  // Editable Fields
  const [formData, setFormData] = useState({
    BRAND_NAME: activeItem?.BRAND_NAME || activeItem?.brand_name || '',
    SHORT_DESC: activeItem?.SHORT_DESC || activeItem?.short_desc || '',
    INVOICE_DESC: activeItem?.INVOICE_DESC || activeItem?.invoice_desc || '',
    MOBILE_DESC: activeItem?.MOBILE_DESC || activeItem?.mobile_desc || '',
    Classpath: activeItem?.Classpath || activeItem?.classpath || '',
    LENGTH: activeItem?.LENGTH || activeItem?.length || '',
    WIDTH: activeItem?.WIDTH || activeItem?.width || '',
    HEIGHT: activeItem?.HEIGHT || activeItem?.height || ''
  });

  const [feedbackNotes, setFeedbackNotes] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Sync form data when activeItem changes
  React.useEffect(() => {
    if (activeItem) {
      setFormData({
        BRAND_NAME: activeItem.BRAND_NAME || activeItem.brand_name || '',
        SHORT_DESC: activeItem.SHORT_DESC || activeItem.short_desc || '',
        INVOICE_DESC: activeItem.INVOICE_DESC || activeItem.invoice_desc || '',
        MOBILE_DESC: activeItem.MOBILE_DESC || activeItem.mobile_desc || '',
        Classpath: activeItem.Classpath || activeItem.classpath || '',
        LENGTH: activeItem.LENGTH || activeItem.length || '',
        WIDTH: activeItem.WIDTH || activeItem.width || '',
        HEIGHT: activeItem.HEIGHT || activeItem.height || ''
      });
      setSaveSuccess(false);
      setFeedbackNotes('');
    }
  }, [activeItem?.Mfg_Part_Num]);

  const handleSelectSKU = (item) => {
    setSelectedMpn(item.Mfg_Part_Num || item.mfg_part_num);
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleApprove = async () => {
    setIsSaving(true);
    const updated = {
      ...activeItem,
      ...formData,
      _confidence: 1.0,
      _needs_hitl: false
    };

    try {
      // Send active learning override to backend
      await fetch(apiUrl('/api/v1/hitl/override'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mpn: activeItem.Mfg_Part_Num || activeItem.mfg_part_num || '',
          brand_name: formData.BRAND_NAME || '',
          manufacturer_name: activeItem.MANUFACTURER_NAME || activeItem.manufacturer_name || activeItem.Part_Manuf || '',
          override_data: formData,
          reviewer_notes: feedbackNotes || 'Approved in HITL Review Station'
        })
      });

      handleSaveReviewedItem(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);

      // Auto-advance to next pending item if available
      const nextPending = pendingItems.find(it => (it.Mfg_Part_Num || it.mfg_part_num) !== (activeItem.Mfg_Part_Num || activeItem.mfg_part_num));
      if (nextPending) {
        setSelectedMpn(nextPending.Mfg_Part_Num || nextPending.mfg_part_num);
      }
    } catch (err) {
      console.error('Error saving review override:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const invoiceLength = formData.INVOICE_DESC.length;
  const mobileLength = formData.MOBILE_DESC.length;
  const isInvoiceValid = invoiceLength <= 40;
  const isMobileValid = mobileLength >= 60 && mobileLength <= 80;

  return (
    <div className="space-y-4 pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-5 rounded-2xl bg-surface-elevated border border-surface-border">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-amber-950 border border-amber-800 flex items-center justify-center text-amber-400 shadow-md">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">HITL Quality & Governance Review Hub</h1>
            <p className="text-xs text-slate-400">
              Active Learning Rule Correction • Character Boundary Verification • 1-Click Approval
            </p>
          </div>
        </div>

        {/* Filter Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setFilterMode('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-colors cursor-pointer ${
              filterMode === 'ALL'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                : 'bg-surface text-slate-400 border border-surface-border hover:text-white'
            }`}
          >
            All Catalog ({items.length})
          </button>
          <button
            onClick={() => setFilterMode('PENDING')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-colors cursor-pointer ${
              filterMode === 'PENDING'
                ? 'bg-amber-950 text-amber-300 border border-amber-800'
                : 'bg-surface text-slate-400 border border-surface-border hover:text-white'
            }`}
          >
            Audit Queue ({pendingItems.length})
          </button>
        </div>
      </div>

      {/* Main Review Layout: 2-Column Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: SKU Review Queue List */}
        <div className="lg:col-span-4 space-y-3">
          <div className="p-3.5 rounded-xl bg-surface-elevated border border-surface-border space-y-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search MPN, brand, or title..."
              className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 placeholder-slate-500 font-mono focus:outline-none focus:border-cyan-500"
            />
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1">
              <span>Queue: {displayedItems.length} SKUs</span>
              <span>{pendingItems.length} Needs Review</span>
            </div>
          </div>

          <div className="space-y-2 max-h-[260px] lg:max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
            {displayedItems.map((it, idx) => {
              const mpn = it.Mfg_Part_Num || it.mfg_part_num || `item-${idx}`;
              const isSelected = mpn === (activeItem?.Mfg_Part_Num || activeItem?.mfg_part_num);
              const conf = it._confidence !== undefined ? it._confidence : 1.0;
              const needsReview = conf < 0.90 || it._needs_hitl;

              return (
                <div
                  key={`${mpn}-${idx}`}
                  onClick={() => handleSelectSKU(it)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-1.5 ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500 shadow-md'
                      : 'bg-surface-elevated border-surface-border hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-cyan-300 font-mono">{mpn}</span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                      needsReview
                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                        : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}>
                      {needsReview ? 'HITL Flagged' : 'Verified (1.0)'}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-slate-200 line-clamp-1">
                    {it.Part_Desc || it.SHORT_DESC}
                  </h4>

                  <div className="text-[10px] font-mono text-slate-400 truncate">
                    Brand: <span className="text-slate-300">{it.BRAND_NAME || it.brand_name || 'Generic'}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Full Interactive Review Station */}
        <div className="lg:col-span-8 space-y-4">
          {activeItem ? (
            <div className="p-6 rounded-2xl bg-surface-elevated border border-surface-border space-y-5 shadow-xl">
              
              {/* Active SKU Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-surface-border">
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-base font-bold text-white font-mono">{activeItem.Mfg_Part_Num || activeItem.mfg_part_num}</h2>
                    <span className="text-xs font-mono text-cyan-400 font-bold">{activeItem.BRAND_NAME || activeItem.brand_name}</span>
                  </div>
                  <p className="text-xs text-slate-400 pt-0.5">
                    Original Source: <span className="text-slate-300">{activeItem.Part_Manuf || 'Raw Supplier Feed'}</span>
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleOpenDbom(activeItem)}
                    className="px-3 py-1.5 rounded-lg bg-cyan-950 text-cyan-300 border border-cyan-800 text-xs font-mono font-semibold hover:bg-cyan-900 transition-colors cursor-pointer"
                  >
                    Inspect DBOM
                  </button>
                </div>
              </div>

              {/* Character Limit Governance Meters */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className={`p-3.5 rounded-xl border ${isInvoiceValid ? 'bg-slate-900/80 border-surface-border' : 'bg-rose-950/40 border-rose-800'}`}>
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-300 font-bold">INVOICE_DESC Limit (≤ 40 chars)</span>
                    <span className={`font-bold ${isInvoiceValid ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {invoiceLength} / 40
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden mt-2 border border-slate-800">
                    <div
                      className={`h-full transition-all ${isInvoiceValid ? 'bg-emerald-500' : 'bg-rose-500'}`}
                      style={{ width: `${Math.min(100, (invoiceLength / 40) * 100)}%` }}
                    />
                  </div>
                </div>

                <div className={`p-3.5 rounded-xl border ${isMobileValid ? 'bg-slate-900/80 border-surface-border' : 'bg-amber-950/40 border-amber-800'}`}>
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-300 font-bold">MOBILE_DESC Bounds (60–80 chars)</span>
                    <span className={`font-bold ${isMobileValid ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {mobileLength} / 60-80
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden mt-2 border border-slate-800">
                    <div
                      className={`h-full transition-all ${isMobileValid ? 'bg-emerald-500' : 'bg-amber-500'}`}
                      style={{ width: `${Math.min(100, (mobileLength / 80) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Editable Fields Form */}
              <div className="space-y-4 pt-1">
                
                {/* Brand & Taxonomy */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">BRAND_NAME (UniCat Canonical + ®/™)</label>
                    <input
                      type="text"
                      value={formData.BRAND_NAME}
                      onChange={(e) => handleChange('BRAND_NAME', e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">4-Tier Taxonomical Classpath</label>
                    <input
                      type="text"
                      value={formData.Classpath}
                      onChange={(e) => handleChange('Classpath', e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                {/* Descriptions */}
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">SHORT_DESC (Customer Catalog Title)</label>
                    <input
                      type="text"
                      value={formData.SHORT_DESC}
                      onChange={(e) => handleChange('SHORT_DESC', e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">INVOICE_DESC (ERP Invoice Summary - Max 40)</label>
                    <input
                      type="text"
                      value={formData.INVOICE_DESC}
                      onChange={(e) => handleChange('INVOICE_DESC', e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-cyan-300 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">MOBILE_DESC (E-Commerce Mobile Summary - 60 to 80)</label>
                    <input
                      type="text"
                      value={formData.MOBILE_DESC}
                      onChange={(e) => handleChange('MOBILE_DESC', e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                {/* Dimensions */}
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">LENGTH</label>
                    <input
                      type="text"
                      value={formData.LENGTH}
                      onChange={(e) => handleChange('LENGTH', e.target.value)}
                      placeholder="e.g. 24-1/4"
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">WIDTH</label>
                    <input
                      type="text"
                      value={formData.WIDTH}
                      onChange={(e) => handleChange('WIDTH', e.target.value)}
                      placeholder="e.g. 24"
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-slate-400 block mb-1">HEIGHT</label>
                    <input
                      type="text"
                      value={formData.HEIGHT}
                      onChange={(e) => handleChange('HEIGHT', e.target.value)}
                      placeholder="e.g. 33-7/16"
                      className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                {/* Reviewer Feedback Notes for Active Learning */}
                <div>
                  <label className="text-xs font-mono text-slate-400 block mb-1">
                    Active Learning Feedback Notes (Persisted to DuckDB Overrides Table)
                  </label>
                  <input
                    type="text"
                    value={feedbackNotes}
                    onChange={(e) => setFeedbackNotes(e.target.value)}
                    placeholder="e.g. Adjusted length abbreviation to standard fractional format..."
                    className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>

              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-surface-border flex items-center justify-between">
                <div className="text-xs font-mono text-slate-400">
                  {saveSuccess && <span className="text-emerald-400 font-bold flex items-center space-x-1"><Check className="h-4 w-4" /><span>Approved & Persisted!</span></span>}
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={handleApprove}
                    disabled={isSaving}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 cursor-pointer flex items-center space-x-2 transition-all"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    <span>{isSaving ? 'Persisting...' : 'Approve & Save to Master'}</span>
                  </button>
                </div>
              </div>

            </div>
          ) : (
            <div className="p-12 text-center text-xs text-slate-500 font-mono bg-surface-elevated rounded-2xl border border-surface-border">
              Select a SKU from the review queue to start auditing.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
