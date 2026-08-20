import React, { useState, useEffect } from 'react';
import { GitCompare, CheckCircle2, AlertTriangle, XCircle, ArrowRightLeft, Sparkles, X, Layers, Cpu, Wrench } from 'lucide-react';

const PRESET_PRODUCTS = [
  {
    id: "tool_grinder",
    name: "DEWALT® 4-1/2 in Angle Grinder (7/8 in Arbor, 11000 RPM)",
    data: {
      "Mfg_Part_Num": "DWE402",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 4-1/2 in Small Angle Grinder 11A 7/8 in Arbor 11000 RPM",
      "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders"
    }
  },
  {
    id: "disc_milw_78",
    name: "Milwaukee® 4-1/2 in x .045 in x 7/8 in Cut-Off Disc (Matching Arbor)",
    data: {
      "Mfg_Part_Num": "49-94-0101",
      "BRAND_NAME": "Milwaukee®",
      "SHORT_DESC": "Milwaukee® 4-1/2 in x .045 in x 7/8 in Metal Cut-Off Disc",
      "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"
    }
  },
  {
    id: "disc_diablo_58",
    name: "Diablo® 4-1/2 in x .045 in x 5/8 in Cut-Off Disc (Mismatched 5/8 Arbor)",
    data: {
      "Mfg_Part_Num": "DBD045045101F-58",
      "BRAND_NAME": "Diablo®",
      "SHORT_DESC": "Diablo® 4-1/2 in x .045 in x 5/8 in Metal Cut-Off Disc",
      "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"
    }
  },
  {
    id: "drill_dewalt_20v",
    name: "DEWALT® 20V MAX* Cordless Compact Drill (20V Platform)",
    data: {
      "Mfg_Part_Num": "DCD771C2",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 20V MAX* Cordless Compact Drill Bare Tool",
      "Classpath": "Tools & Instruments>Power Tools>Drills>Cordless Drills"
    }
  },
  {
    id: "battery_dewalt_20v",
    name: "DEWALT® 20V MAX* 5.0Ah Battery Pack (Compatible)",
    data: {
      "Mfg_Part_Num": "DCB205",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 20V MAX* 5.0Ah Lithium-Ion Battery Pack",
      "Classpath": "Tools & Instruments>Power Tool Accessories>Batteries & Chargers"
    }
  },
  {
    id: "battery_milw_12v",
    name: "Milwaukee® M12 12V Compact Battery (Incompatible Voltage)",
    data: {
      "Mfg_Part_Num": "48-11-2401",
      "BRAND_NAME": "Milwaukee®",
      "SHORT_DESC": "Milwaukee® M12 12V Compact Battery Pack",
      "Classpath": "Tools & Instruments>Power Tool Accessories>Batteries & Chargers"
    }
  }
];

export default function CompatibilityMatrixModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('EVALUATOR'); // 'EVALUATOR' | 'SUBSTITUTES'
  
  // Evaluator State
  const [selectedProductA, setSelectedProductA] = useState(PRESET_PRODUCTS[0].id);
  const [selectedProductB, setSelectedProductB] = useState(PRESET_PRODUCTS[1].id);
  const [evalResult, setEvalResult] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // Substitutes State
  const [targetMpn, setTargetMpn] = useState('49-94-0101');
  const [substitutesData, setSubstitutesData] = useState(null);
  const [isLoadingSubstitutes, setIsLoadingSubstitutes] = useState(false);

  if (!isOpen) return null;

  const handleRunEvaluation = async () => {
    const prodA = PRESET_PRODUCTS.find(p => p.id === selectedProductA)?.data || {};
    const prodB = PRESET_PRODUCTS.find(p => p.id === selectedProductB)?.data || {};

    setIsEvaluating(true);
    try {
      const res = await fetch('/api/v1/compatibility/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_a: prodA, product_b: prodB })
      });
      const json = await res.json();
      if (json.success) {
        setEvalResult(json.result);
      }
    } catch (err) {
      console.error('Error evaluating compatibility:', err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleFetchSubstitutes = async (mpn) => {
    setIsLoadingSubstitutes(true);
    try {
      const res = await fetch(`/api/v1/compatibility/substitutes?mpn=${encodeURIComponent(mpn)}`);
      const json = await res.json();
      if (json.success) {
        setSubstitutesData(json.data);
      }
    } catch (err) {
      console.error('Error fetching substitutes:', err);
    } finally {
      setIsLoadingSubstitutes(false);
    }
  };

  useEffect(() => {
    handleRunEvaluation();
  }, [selectedProductA, selectedProductB]);

  useEffect(() => {
    handleFetchSubstitutes(targetMpn);
  }, [targetMpn]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-surface-elevated border border-surface-border rounded-2xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-6 border-b border-surface-border flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-purple-950 border border-purple-800 flex items-center justify-center text-purple-400 shadow-md">
              <GitCompare className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-lg font-bold text-white tracking-tight">Industrial Compatibility & Substitute Matrix</h2>
                <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-800">
                  Task 21
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Multi-domain mechanical, electrical, and dimensional constraint reasoning
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="h-8 w-8 rounded-lg bg-surface hover:bg-surface-border flex items-center justify-center text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-surface-border bg-slate-950/40 px-6 pt-3">
          <button
            onClick={() => setActiveTab('EVALUATOR')}
            className={`pb-3 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer ${
              activeTab === 'EVALUATOR'
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Wrench className="h-4 w-4" />
            <span>Pairwise Mechanical/Electrical Evaluator</span>
          </button>

          <button
            onClick={() => setActiveTab('SUBSTITUTES')}
            className={`pb-3 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer ${
              activeTab === 'SUBSTITUTES'
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <ArrowRightLeft className="h-4 w-4" />
            <span>Cross-Brand OEM Functional Substitutes</span>
          </button>
        </div>

        {/* Tab 1: Evaluator */}
        {activeTab === 'EVALUATOR' && (
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            
            {/* Product Pickers */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 rounded-xl bg-surface border border-surface-border">
                <label className="text-xs font-mono text-cyan-400 block mb-2 font-semibold">
                  Product A (Primary Tool / Fixture / Unit)
                </label>
                <select
                  value={selectedProductA}
                  onChange={(e) => setSelectedProductA(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-surface-border text-xs text-white focus:outline-none focus:border-purple-500 font-mono cursor-pointer"
                >
                  {PRESET_PRODUCTS.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                <div className="mt-3 p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] text-slate-300 font-mono">
                  {PRESET_PRODUCTS.find(p => p.id === selectedProductA)?.data.SHORT_DESC}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-surface border border-surface-border">
                <label className="text-xs font-mono text-purple-400 block mb-2 font-semibold">
                  Product B (Accessory / Consumable / Battery / Bulb)
                </label>
                <select
                  value={selectedProductB}
                  onChange={(e) => setSelectedProductB(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-surface-border text-xs text-white focus:outline-none focus:border-purple-500 font-mono cursor-pointer"
                >
                  {PRESET_PRODUCTS.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                <div className="mt-3 p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] text-slate-300 font-mono">
                  {PRESET_PRODUCTS.find(p => p.id === selectedProductB)?.data.SHORT_DESC}
                </div>
              </div>
            </div>

            {/* Evaluation Results Box */}
            {evalResult && (
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-surface-border shadow-md space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {evalResult.status === 'COMPATIBLE' ? (
                      <div className="h-9 w-9 rounded-full bg-emerald-950 border border-emerald-700 flex items-center justify-center text-emerald-400">
                        <CheckCircle2 className="h-5 w-5" />
                      </div>
                    ) : evalResult.status === 'INCOMPATIBLE' ? (
                      <div className="h-9 w-9 rounded-full bg-rose-950 border border-rose-700 flex items-center justify-center text-rose-400">
                        <XCircle className="h-5 w-5" />
                      </div>
                    ) : (
                      <div className="h-9 w-9 rounded-full bg-amber-950 border border-amber-700 flex items-center justify-center text-amber-400">
                        <AlertTriangle className="h-5 w-5" />
                      </div>
                    )}
                    <div>
                      <h3 className="font-bold text-white text-base flex items-center space-x-2">
                        <span>Compatibility Status: {evalResult.status}</span>
                      </h3>
                      <p className="text-xs text-slate-400 font-mono">
                        Calculated Match Score: {Math.round(evalResult.compatibility_score * 100)}%
                      </p>
                    </div>
                  </div>

                  <span className={`px-3 py-1 rounded-full text-xs font-mono font-semibold ${
                    evalResult.status === 'COMPATIBLE' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
                    evalResult.status === 'INCOMPATIBLE' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                    'bg-amber-950 text-amber-300 border border-amber-800'
                  }`}>
                    {evalResult.status === 'COMPATIBLE' ? '100% Fitment Verified' :
                     evalResult.status === 'INCOMPATIBLE' ? 'Physical Fitment Blocked' : 'Conditional Match'}
                  </span>
                </div>

                {/* Matched Specs */}
                {evalResult.matched_specs?.length > 0 && (
                  <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-900/50">
                    <span className="text-xs font-semibold text-emerald-400 block mb-1">
                      ✓ Harmonized Specifications & Dimensions:
                    </span>
                    <ul className="list-disc list-inside text-xs text-slate-300 space-y-0.5">
                      {evalResult.matched_specs.map((m, i) => (
                        <li key={i}>{m}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Conflict Specs */}
                {evalResult.conflict_specs?.length > 0 && (
                  <div className="p-3 rounded-xl bg-rose-950/30 border border-rose-900/50">
                    <span className="text-xs font-semibold text-rose-400 block mb-1">
                      ⚠️ Constraint Conflicts & Physical Mismatches:
                    </span>
                    <ul className="list-disc list-inside text-xs text-rose-200 space-y-0.5">
                      {evalResult.conflict_specs.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="text-xs text-slate-400 font-mono bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-slate-500 font-semibold">Engineering Note:</span> {evalResult.engineering_notes}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Substitutes */}
        {activeTab === 'SUBSTITUTES' && (
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            
            {/* Quick SKU Preset Switcher */}
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400 font-mono">Sample SKUs:</span>
              <button
                onClick={() => setTargetMpn('49-94-0101')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                  targetMpn === '49-94-0101' ? 'bg-purple-950 text-purple-300 border border-purple-700' : 'bg-surface hover:bg-surface-border text-slate-300'
                }`}
              >
                49-94-0101 (Milwaukee Cut-Off)
              </button>
              <button
                onClick={() => setTargetMpn('PDSH4816AF')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                  targetMpn === 'PDSH4816AF' ? 'bg-purple-950 text-purple-300 border border-purple-700' : 'bg-surface hover:bg-surface-border text-slate-300'
                }`}
              >
                PDSH4816AF (Frigidaire Dishwasher)
              </button>
              <button
                onClick={() => setTargetMpn('558213')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                  targetMpn === '558213' ? 'bg-purple-950 text-purple-300 border border-purple-700' : 'bg-surface hover:bg-surface-border text-slate-300'
                }`}
              >
                558213 (Philips A19 LED)
              </button>
              <button
                onClick={() => setTargetMpn('CPLG-38')}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                  targetMpn === 'CPLG-38' ? 'bg-purple-950 text-purple-300 border border-purple-700' : 'bg-surface hover:bg-surface-border text-slate-300'
                }`}
              >
                3/8 CPLG BRS (Pipe Fitting)
              </button>
            </div>

            {/* Substitutes Grid */}
            {substitutesData && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white font-mono">
                      Category: {substitutesData.category}
                    </h3>
                    <p className="text-xs text-slate-400">
                      Cross-brand equivalents for target MPN: <span className="text-cyan-400 font-mono">{substitutesData.target_mpn}</span>
                    </p>
                  </div>
                  <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 text-slate-300 border border-slate-800">
                    {substitutesData.substitutes.length} Equivalent Candidates Found
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {substitutesData.substitutes.map((sub, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-surface border border-surface-border hover:border-purple-800/80 transition-all flex flex-col justify-between space-y-3">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-bold text-xs text-purple-300 font-mono">{sub.substitute_brand}</span>
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                            sub.interchangeability_type === 'DIRECT_FORM_FIT_FUNCTION' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-blue-950 text-blue-400 border border-blue-800'
                          }`}>
                            {sub.interchangeability_type === 'DIRECT_FORM_FIT_FUNCTION' ? 'Direct Form/Fit/Function' : 'Performance Upgrade'}
                          </span>
                        </div>
                        <h4 className="text-xs font-semibold text-white line-clamp-2" title={sub.substitute_title}>
                          {sub.substitute_title}
                        </h4>
                        <div className="text-[11px] font-mono text-cyan-400 mt-1">MPN: {sub.substitute_mpn}</div>
                      </div>

                      {/* Spec Alignment Table */}
                      <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[10px] font-mono space-y-1">
                        <span className="text-slate-500 font-semibold block mb-0.5">Matched Specifications:</span>
                        {Object.entries(sub.spec_alignment).map(([k, v]) => (
                          <div key={k} className="flex justify-between text-slate-300">
                            <span className="text-slate-400">{k}:</span>
                            <span className="font-semibold text-white">{v}</span>
                          </div>
                        ))}
                      </div>

                      <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800/60 font-mono">
                        <span className="text-slate-400">Match Confidence:</span>
                        <span className="text-emerald-400 font-bold">{Math.round(sub.match_confidence * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-surface-border bg-slate-900/60 flex items-center justify-between">
          <div className="text-xs text-slate-400 flex items-center space-x-2 font-mono">
            <span>Powered by OmniSpec Physical Constraint & Substitute Reasoner</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-surface hover:bg-surface-border text-xs font-semibold text-white transition-colors cursor-pointer"
          >
            Close Matrix
          </button>
        </div>

      </div>
    </div>
  );
}
