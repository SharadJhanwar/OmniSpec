import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, ShieldCheck, FileText, ArrowRight, Save, Sparkles } from 'lucide-react';

export default function HITLReviewModal({ item, onClose, onSave }) {
  if (!item) return null;

  const [invoiceDesc, setInvoiceDesc] = useState('');
  const [mobileDesc, setMobileDesc] = useState('');
  const [shortDesc, setShortDesc] = useState('');
  const [brandName, setBrandName] = useState('');
  const [mfrName, setMfrName] = useState('');
  const [reviewerNotes, setReviewerNotes] = useState('Manual verification in HITL Studio');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (item) {
      setInvoiceDesc(item["INVOICE_DESC"] || item["invoice_desc"] || '');
      setMobileDesc(item["MOBILE_DESC"] || item["mobile_desc"] || '');
      setShortDesc(item["SHORT_DESC"] || item["short_desc"] || '');
      setBrandName(item["BRAND_NAME"] || item["brand_name"] || '');
      setMfrName(item["MANUFACTURER_NAME"] || item["manufacturer_name"] || '');
    }
  }, [item]);

  const conf = item._confidence !== undefined ? item._confidence : 1.0;
  const isHighConf = conf >= 0.85;

  const handleSave = async () => {
    setIsSaving(true);
    const mpn = item["Mfg_Part_Num"] || item["mfg_part_num"] || '';

    // Active Learning Feedback Loop: Persist override in DuckDB
    try {
      await fetch('/api/v1/hitl/override', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mpn: mpn,
          brand_name: brandName,
          manufacturer_name: mfrName,
          trade_name: item["TRADE_NAME"] || item["trade_name"] || '',
          reviewer_notes: reviewerNotes,
          override_data: {
            INVOICE_DESC: invoiceDesc,
            MOBILE_DESC: mobileDesc,
            SHORT_DESC: shortDesc
          }
        })
      });
    } catch (e) {
      console.warn('Could not persist override to backend:', e);
    }

    const updated = {
      ...item,
      "BRAND_NAME": brandName,
      "MANUFACTURER_NAME": mfrName,
      "INVOICE_DESC": invoiceDesc,
      "MOBILE_DESC": mobileDesc,
      "SHORT_DESC": shortDesc,
      _confidence: 1.0 // Promoted to verified by human operator
    };

    setIsSaving(false);
    onSave(updated);
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="glass-panel-elevated w-full max-w-4xl rounded-2xl shadow-2xl border border-cyan-500/40 overflow-hidden flex flex-col max-h-[90vh] bg-surface text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 border-b border-surface-border flex items-center justify-between bg-surface-elevated">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">HITL Master Data Studio</h3>
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold ${isHighConf ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}`}>
                  {(conf * 100).toFixed(0)}% Confidence
                </span>
                <span className="text-[10px] font-mono uppercase bg-cyan-950 text-cyan-400 border border-cyan-800 px-2 py-0.5 rounded">
                  Active Learning Enabled
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">SKU / MPN: <span className="text-cyan-400 font-semibold">{item["Mfg_Part_Num"] || item["mfg_part_num"]}</span></p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-surface transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-200">
          {/* Side-by-Side Diff Section */}
          <div>
            <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider font-mono mb-2">1. Input vs. Enriched Master Data</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-4 rounded-xl bg-surface-elevated border border-surface-border">
                <p className="text-[10px] uppercase font-mono text-slate-400 font-bold mb-1">Raw Supplier Input</p>
                <p className="text-xs text-slate-200 font-mono bg-surface p-2.5 rounded-lg border border-surface-border">
                  {item["Part_Desc"] || item["part_desc"] || 'No raw description available'}
                </p>
                <div className="mt-3 text-[11px] text-slate-400 space-y-1 font-mono">
                  <p><span className="text-slate-500">Supplier:</span> {item["Part_Manuf"] || item["part_manuf"] || '—'}</p>
                  <p><span className="text-slate-500">Raw MPN:</span> {item["Mfg_Part_Num"] || item["mfg_part_num"] || '—'}</p>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-800/60">
                <p className="text-[10px] uppercase font-mono text-cyan-400 font-bold mb-1">Canonical Brand & Classpath</p>
                <div className="space-y-2">
                  <div>
                    <label className="text-[10px] text-slate-400 block font-mono">Approved Brand Name (with ®, ™)</label>
                    <input
                      type="text"
                      value={brandName}
                      onChange={(e) => setBrandName(e.target.value)}
                      className="w-full px-2.5 py-1.5 rounded bg-surface border border-surface-border text-xs text-white font-bold font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-400 block font-mono">Legal Manufacturer Name</label>
                    <input
                      type="text"
                      value={mfrName}
                      onChange={(e) => setMfrName(e.target.value)}
                      className="w-full px-2.5 py-1.5 rounded bg-surface border border-surface-border text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>
                <p className="text-[11px] text-slate-300 font-mono mt-2"><span className="text-slate-500">Classpath:</span> {item["Classpath"] || item["classpath"]}</p>
              </div>
            </div>
          </div>

          {/* Multi-Channel Editable Copy Form */}
          <div>
            <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider font-mono mb-2">2. Multi-Channel Copy Editor (Constraint Enforced)</h4>
            <div className="space-y-4 bg-surface-elevated p-4 rounded-xl border border-surface-border">
              {/* Invoice Desc */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[11px] font-bold text-slate-300 font-mono">INVOICE_DESC (Till Receipt)</label>
                  <span className={`text-[11px] font-mono px-2 py-0.5 rounded ${invoiceDesc.length <= 40 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800 font-bold'}`}>
                    {invoiceDesc.length} / 40 chars
                  </span>
                </div>
                <input
                  type="text"
                  value={invoiceDesc}
                  onChange={(e) => setInvoiceDesc(e.target.value.toUpperCase())}
                  className="w-full px-3.5 py-2.5 rounded-lg bg-surface border border-surface-border text-xs font-mono text-amber-300 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Mobile Desc */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[11px] font-bold text-slate-300 font-mono">MOBILE_DESC (Mobile Warehouse App)</label>
                  <span className={`text-[11px] font-mono px-2 py-0.5 rounded ${mobileDesc.length >= 60 && mobileDesc.length <= 80 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}`}>
                    {mobileDesc.length} chars (Target: 60-80)
                  </span>
                </div>
                <input
                  type="text"
                  value={mobileDesc}
                  onChange={(e) => setMobileDesc(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              {/* Product Title / Short Desc */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[11px] font-bold text-slate-300 font-mono">SHORT_DESC (E-Commerce PDP Title)</label>
                </div>
                <textarea
                  rows={2}
                  value={shortDesc}
                  onChange={(e) => setShortDesc(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

          {/* Active Learning Notes */}
          <div>
            <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider font-mono mb-2">3. Reviewer Feedback & Active Learning Notes</h4>
            <input
              type="text"
              value={reviewerNotes}
              onChange={(e) => setReviewerNotes(e.target.value)}
              placeholder="e.g. Verified brand against OEM manufacturer portal"
              className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-300 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-surface-border bg-surface-elevated flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-surface hover:bg-surface-border border border-surface-border text-xs font-medium text-slate-300 cursor-pointer"
          >
            Cancel
          </button>

          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all cursor-pointer disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            <span>{isSaving ? 'Persisting to Knowledge Base...' : 'Approve & Teach Swarm (100%)'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
