import React, { useState } from 'react';
import { Sparkles, Play, Terminal, ArrowRight, Loader2 } from 'lucide-react';

export default function SingleSkuSandbox({ onEnrichSuccess }) {
  const [mfgPartNum, setMfgPartNum] = useState('PDSH4816AF');
  const [partDesc, setPartDesc] = useState('PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA');
  const [supplier, setSupplier] = useState('Appliance Dealers Cooperative (APPDE)');
  const [isRunning, setIsRunning] = useState(false);

  const presets = [
    {
      label: 'Frigidaire Dishwasher',
      mpn: 'PDSH4816AF',
      desc: 'PDSH4816AF Dishwasher SS - Display Only 24 in W x 24.25 in D 120V 15A 47dBA',
      supp: 'Appliance Dealers Cooperative (APPDE)'
    },
    {
      label: 'Milwaukee Cut-Off Disc',
      mpn: '49-94-0013',
      desc: '49-94-0013 Milw 5"x.045"x7/8" Metal Cut Off Disc',
      supp: 'Milwaukee Accessory (4031)'
    },
    {
      label: 'Philips LED A19 Bulb',
      mpn: '558213',
      desc: '9.5A19/LED/827/FR/P/ND 4/2FB LED A19 60W Equivalent 2700K Medium Base 2PK',
      supp: 'Phillips Lighting (5831)'
    },
    {
      label: 'DEWALT Miter Saw',
      mpn: 'DCS361B',
      desc: 'DCS361B DEWALT 20V MAX 7-1/4 IN Cordless Sliding Miter Saw Brushless',
      supp: 'Black & Decker/dewlt (2585)'
    },
    {
      label: 'Trex Decking Board',
      mpn: '1513720',
      desc: '1nx6-16\' Honey Grove Grooved - Trex Enhance Naturals Decking',
      supp: 'Boise Cascade Building Materials (BOICA)'
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

      const response = await fetch('/api/v1/enrich/single', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      if (data && data.delivery_record) {
        const enrichedItem = {
          ...data.delivery_record,
          _confidence: data.overall_confidence || 1.0,
          _needs_hitl: data.needs_hitl_review || false,
          _traces: data.traces || []
        };
        onEnrichSuccess(enrichedItem, data.traces);
      }
    } catch (err) {
      console.error('Error running swarm:', err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="glass-panel p-4 rounded-xl border border-cyan-500/30">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">Live Single-SKU Sandbox</h3>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center space-x-1.5 overflow-x-auto w-full sm:w-auto">
          <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">Presets:</span>
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
            placeholder="e.g. PDSH4816AF"
            className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-cyan-400 font-mono focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="sm:col-span-5">
          <label className="text-[10px] font-mono text-slate-400 mb-1 block">Raw Part Description (Messy tokens)</label>
          <input
            type="text"
            value={partDesc}
            onChange={(e) => setPartDesc(e.target.value)}
            placeholder="e.g. 1nx6-16' Honey Grove Grooved Decking"
            className="w-full px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="text-[10px] font-mono text-slate-400 mb-1 block">Supplier / Vendor</label>
          <input
            type="text"
            value={supplier}
            onChange={(e) => setSupplier(e.target.value)}
            placeholder="e.g. BOICA"
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
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin text-slate-950" />
                <span>Running...</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Run Swarm</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
