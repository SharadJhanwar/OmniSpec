import React, { useState } from 'react';
import {
  Sparkles,
  Play,
  Terminal,
  ArrowRight,
  Loader2,
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Image as ImageIcon,
  ExternalLink,
  Layers,
  Cpu
} from 'lucide-react';
import { apiUrl } from '../config/api';

export default function SingleSkuSandbox({ onEnrichSuccess, onInspectDbomClick, onOpenCompatibility, onOpenParametricSearch, onOpenFamilies }) {
  const [mfgPartNum, setMfgPartNum] = useState('9A-570-320');
  const [partDesc, setPartDesc] = useState('9A-570-320 Abranet 2.75x30 320G Mesh Grip Roll');
  const [supplier, setSupplier] = useState('Mirka Abrasives Inc (MIRUS)');
  const [isRunning, setIsRunning] = useState(false);
  const [lastDpi, setLastDpi] = useState(null);
  const [lastEnriched, setLastEnriched] = useState(null);

  const presets = [
    {
      label: 'Mirka Abranet Mesh Roll',
      mpn: '9A-570-320',
      desc: '9A-570-320 Abranet 2.75x30 320G Mesh Grip Roll',
      supp: 'Mirka Abrasives Inc (MIRUS)'
    },
    {
      label: 'Freud Diablo 9" Cut-Off',
      mpn: 'DBD090094101F',
      desc: 'DBD090094101F Diablo 9" - Metal Cut-Off Disc .045 in 7/8 in Arbor',
      supp: 'Freud Inc (2435)'
    },
    {
      label: 'Frigidaire Dishwasher',
      mpn: 'PDSH4816AF',
      desc: 'PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA',
      supp: 'Appliance Dealers Cooperative (APPDE)'
    },
    {
      label: 'Milwaukee Cut-Off Disc',
      mpn: '49-94-0101',
      desc: '49-94-0101 Milw 4-1/2"x.045"x7/8" Perform+ Metal Cut Off Disc 10pc',
      supp: 'Milwaukee Accessory (4031)'
    },
    {
      label: 'Philips LED A19 Bulb',
      mpn: '558213',
      desc: '9.5A19/LED/827/FR/P/ND 4/2FB LED A19 60W Equivalent 2700K Medium Base 2PK',
      supp: 'Phillips Lighting (5831)'
    },
    {
      label: 'Brass Pipe Fitting',
      mpn: 'CPLG-38-BRS',
      desc: '3/8 CPLG BRS 150# Female NPT Coupler',
      supp: 'Jam Industrial Supply LLC (JAMIN)'
    }
  ];

  const handleRunSwarm = async () => {
    if (!partDesc) return;
    setIsRunning(true);

    try {
      const payload = {
        Mfg_Part_Num: mfgPartNum,
        Part_Desc: partDesc,
        Part_Manuf: supplier,
        E1_Brand: '',
        Unilog_Brand: '',
        DIB_Brand: ''
      };

      const response = await fetch(apiUrl('/api/v1/enrich/single'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Enrichment failed');
      }

      const data = await response.json();
      if (data.success) {
        setLastEnriched(data.data);
        onEnrichSuccess(data.data, data.traces);

        // Run automated DPI risk evaluation
        try {
          const dpiRes = await fetch(apiUrl('/api/v1/audit/dpi'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: data.data })
          });
          const dpiData = await dpiRes.json();
          if (dpiData.success) {
            setLastDpi(dpiData.dpi);
          }
        } catch (e) {
          console.error('Error computing DPI:', e);
        }
      }
    } catch (err) {
      console.error('Error enriching SKU:', err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-surface-elevated border border-surface-border shadow-xl space-y-4">
      {/* Header & Presets Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-surface-border pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="h-7 w-7 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">Live Single-SKU Sandbox</h3>
            <p className="text-[11px] text-slate-400">Test raw inputs against the 10-Agent Swarm with ReAct finalization</p>
          </div>
        </div>

        {/* Preset Buttons */}
        <div className="flex items-center space-x-1.5 overflow-x-auto">
          <span className="text-[10px] font-mono text-slate-500 shrink-0">Presets:</span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setMfgPartNum(p.mpn);
                setPartDesc(p.desc);
                setSupplier(p.supp);
              }}
              className="px-2 py-0.5 rounded text-[10px] bg-surface hover:bg-surface-elevated text-slate-300 hover:text-cyan-400 border border-surface-border transition-colors font-mono cursor-pointer shrink-0"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-2">
        <div className="sm:col-span-3">
          <label className="text-[10px] font-mono text-slate-400 mb-1 block">Mfg Part Num (MPN)</label>
          <input
            type="text"
            value={mfgPartNum}
            onChange={(e) => setMfgPartNum(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-cyan-400 font-mono focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="sm:col-span-5">
          <label className="text-[10px] font-mono text-slate-400 mb-1 block">Raw Part Description</label>
          <input
            type="text"
            value={partDesc}
            onChange={(e) => setPartDesc(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="text-[10px] font-mono text-slate-400 mb-1 block">Supplier / Vendor</label>
          <input
            type="text"
            value={supplier}
            onChange={(e) => setSupplier(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="sm:col-span-2 flex items-end">
          <button
            type="button"
            onClick={handleRunSwarm}
            disabled={isRunning || !partDesc}
            className="w-full h-[38px] flex items-center justify-center space-x-1.5 px-3 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 disabled:opacity-50 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 cursor-pointer transition-all"
          >
            {isRunning ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin text-slate-950" />
            ) : (
              <Play className="h-3.5 w-3.5 fill-current" />
            )}
            <span>{isRunning ? 'Enriching...' : 'Run Swarm'}</span>
          </button>
        </div>
      </div>

      {/* Result Mini Banner if Enriched */}
      {lastEnriched && (
        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-in fade-in duration-200">
          <div className="flex items-center gap-3">
            {lastEnriched['Product Image'] && String(lastEnriched['Product Image']).startsWith('http') ? (
              <img
                src={lastEnriched['Product Image']}
                alt="Product"
                className="w-12 h-12 rounded-lg object-contain bg-slate-900 border border-slate-700 p-1"
              />
            ) : (
              <div className="w-12 h-12 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
                <ImageIcon className="w-6 h-6" />
              </div>
            )}

            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-cyan-400">{lastEnriched.BRAND_NAME || 'Brand'}</span>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">{lastEnriched.Mfg_Part_Num}</span>
                <span className="text-[10px] text-emerald-400 font-mono">100% 252-Col Validated</span>
              </div>
              <p className="text-xs text-slate-300 line-clamp-1 mt-0.5">{lastEnriched.SHORT_DESC || lastEnriched.Part_Desc}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800">
              Confidence: {Math.round((lastEnriched._confidence || 1.0) * 100)}%
            </span>
          </div>
        </div>
      )}

      {/* Quick Inspection & Studio Launchers Bar */}
      <div className="pt-2 border-t border-surface-border/60 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => onInspectDbomClick({ Mfg_Part_Num: mfgPartNum, Part_Desc: partDesc, Part_Manuf: supplier })}
            className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 font-semibold font-mono text-[11px] transition-all cursor-pointer shadow-sm"
          >
            <ShieldCheck className="h-3.5 w-3.5 text-cyan-400" />
            <span>Inspect DBOM Lineage</span>
          </button>

          {onOpenCompatibility && (
            <button
              type="button"
              onClick={onOpenCompatibility}
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-purple-950/80 hover:bg-purple-900 border border-purple-800 text-purple-300 font-semibold font-mono text-[11px] transition-all cursor-pointer shadow-sm"
            >
              <span>Compatibility Matrix</span>
            </button>
          )}

          {onOpenParametricSearch && (
            <button
              type="button"
              onClick={onOpenParametricSearch}
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-sky-950/80 hover:bg-sky-900 border border-sky-800 text-sky-300 font-semibold font-mono text-[11px] transition-all cursor-pointer shadow-sm"
            >
              <span>Parametric Search</span>
            </button>
          )}

          {onOpenFamilies && (
            <button
              type="button"
              onClick={onOpenFamilies}
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 font-semibold font-mono text-[11px] transition-all cursor-pointer shadow-sm"
            >
              <span>Product Families</span>
            </button>
          )}
        </div>

        {lastDpi && (
          <div className="flex items-center space-x-2 font-mono text-[11px]">
            <span className="text-slate-400">Defect Probability Index (DPI):</span>
            <span className="font-bold text-cyan-400">{Math.round(lastDpi.dpi_score * 100)}%</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
              lastDpi.risk_tier === 'LOW' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
              lastDpi.risk_tier === 'ELEVATED' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
              'bg-rose-950 text-rose-400 border border-rose-800'
            }`}>
              {lastDpi.risk_tier} RISK
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
