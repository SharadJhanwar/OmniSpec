import React, { useState, useEffect } from 'react';
import {
  GitBranch,
  Layers,
  GitCompare,
  BookOpen,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Search,
  ArrowRight,
  ShieldCheck,
  Box,
  Wrench,
  Cpu,
  ArrowRightLeft,
  Sparkles,
  Zap
} from 'lucide-react';
import KnowledgeBaseExplorer from '../components/KnowledgeBaseExplorer';

const PRESET_PAIRINGS = [
  {
    label: "DEWALT Grinder + Milwaukee 7/8\" Disc (Matching Arbor)",
    prodA: {
      "Mfg_Part_Num": "DWE402",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 4-1/2 in Small Angle Grinder 11A 7/8 in Arbor 11000 RPM",
      "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders"
    },
    prodB: {
      "Mfg_Part_Num": "49-94-0101",
      "BRAND_NAME": "Milwaukee®",
      "SHORT_DESC": "Milwaukee® 4-1/2 in x .045 in x 7/8 in Metal Cut-Off Disc 13300 RPM",
      "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"
    }
  },
  {
    label: "DEWALT Grinder + Diablo 5/8\" Disc (Mismatched Arbor Fit)",
    prodA: {
      "Mfg_Part_Num": "DWE402",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 4-1/2 in Small Angle Grinder 11A 7/8 in Arbor 11000 RPM",
      "Classpath": "Tools & Instruments>Power Tools>Grinders>Angle Grinders"
    },
    prodB: {
      "Mfg_Part_Num": "DBD045045101F-58",
      "BRAND_NAME": "Diablo®",
      "SHORT_DESC": "Diablo® 4-1/2 in x .045 in x 5/8 in Metal Cut-Off Disc",
      "Classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels"
    }
  },
  {
    label: "DEWALT 20V Drill + DEWALT 20V Battery (Platform Match)",
    prodA: {
      "Mfg_Part_Num": "DCD771C2",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 20V MAX* Cordless Compact Drill Bare Tool",
      "Classpath": "Tools & Instruments>Power Tools>Drills>Cordless Drills"
    },
    prodB: {
      "Mfg_Part_Num": "DCB205",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 20V MAX* 5.0Ah Lithium-Ion Battery Pack",
      "Classpath": "Tools & Instruments>Power Tool Accessories>Batteries & Chargers"
    }
  },
  {
    label: "DEWALT 20V Drill + Milwaukee M12 12V Battery (Incompatible Voltage)",
    prodA: {
      "Mfg_Part_Num": "DCD771C2",
      "BRAND_NAME": "DEWALT®",
      "SHORT_DESC": "DEWALT® 20V MAX* Cordless Compact Drill Bare Tool",
      "Classpath": "Tools & Instruments>Power Tools>Drills>Cordless Drills"
    },
    prodB: {
      "Mfg_Part_Num": "48-11-2401",
      "BRAND_NAME": "Milwaukee®",
      "SHORT_DESC": "Milwaukee® M12 12V Compact Battery Pack",
      "Classpath": "Tools & Instruments>Power Tool Accessories>Batteries & Chargers"
    }
  }
];

const OEM_SUBSTITUTES_PRESETS = [
  {
    targetMpn: '49-94-0101',
    targetTitle: 'Milwaukee® 4-1/2" x .045" x 7/8" Metal Cut-Off Disc',
    substitutes: [
      {
        mpn: 'DW8062',
        brand: 'DEWALT®',
        title: 'DEWALT® 4-1/2 in x .045 in x 7/8 in Thin Metal Cutting Wheel',
        matchScore: 98,
        matchType: 'DIRECT_EQUIVALENT',
        reasons: ['Exact 4-1/2 in Diameter', 'Matching 7/8 in Arbor', 'Aluminum Oxide Abrasive']
      },
      {
        mpn: 'DBD045045101F',
        brand: 'Diablo®',
        title: 'Diablo® 4-1/2 in x .045 in x 7/8 in Thin Kerf Metal Cut-Off Disc',
        matchScore: 96,
        matchType: 'PREMIUM_ALTERNATIVE',
        reasons: ['Exact 4-1/2 in Diameter', 'Matching 7/8 in Arbor', 'Premium Ceramic Blend']
      },
      {
        mpn: 'B-46159',
        brand: 'Makita®',
        title: 'Makita® 4-1/2 in x 3/64 in x 7/8 in Thin Cut-Off Wheel Stainless',
        matchScore: 94,
        matchType: 'DIRECT_EQUIVALENT',
        reasons: ['Exact 4-1/2 in Diameter', 'Matching 7/8 in Arbor', 'Stainless/Inox Parity']
      }
    ]
  },
  {
    targetMpn: 'PDSH4816AF',
    targetTitle: 'FRIGIDAIRE® Professional 24 in Built-In Dishwasher 47dBA',
    substitutes: [
      {
        mpn: 'WDTS7024RZ',
        brand: 'Whirlpool®',
        title: 'Whirlpool® Eco Series 24 in Built-in Dishwasher Stainless Steel 41dBA',
        matchScore: 96,
        matchType: 'DIRECT_EQUIVALENT',
        reasons: ['Matching 24 in Width', '120V 15A Circuit Match', 'Quieter 41 dBA Rating']
      },
      {
        mpn: 'SHX78B75UC',
        brand: 'Bosch®',
        title: 'Bosch® 800 Series 24 in Top Control Dishwasher Stainless 42dBA',
        matchScore: 95,
        matchType: 'PREMIUM_ALTERNATIVE',
        reasons: ['Matching 24 in Cutout', '120V Standard Circuit', 'PrecisionWash System']
      }
    ]
  }
];

export default function IntelligencePage() {
  const [activeTab, setActiveTab] = useState('FAMILIES'); // 'FAMILIES', 'COMPATIBILITY', 'KB'

  // Families State
  const [familiesData, setFamiliesData] = useState(null);
  const [selectedFamilyId, setSelectedFamilyId] = useState(null);
  const [selectedAxisValues, setSelectedAxisValues] = useState({});
  const [isFamiliesLoading, setIsFamiliesLoading] = useState(false);

  // Compatibility Evaluator State
  const [selectedPairingIdx, setSelectedPairingIdx] = useState(0);
  const [prodA, setProdA] = useState(PRESET_PAIRINGS[0].prodA);
  const [prodB, setProdB] = useState(PRESET_PAIRINGS[0].prodB);
  const [compatResult, setCompatResult] = useState(null);
  const [isEvaluatingCompat, setIsEvaluatingCompat] = useState(false);

  // Substitutes State
  const [selectedSubPresetIdx, setSelectedSubPresetIdx] = useState(0);

  // Load Families on mount
  useEffect(() => {
    setIsFamiliesLoading(true);
    fetch('/api/v1/families')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.data) {
          setFamiliesData(data.data);
          if (data.data.families.length > 0) {
            setSelectedFamilyId(data.data.families[0].family_id);
            const firstFam = data.data.families[0];
            const defaults = {};
            firstFam.variant_axes.forEach(ax => {
              if (ax.values.length > 0) defaults[ax.name] = ax.values[0];
            });
            setSelectedAxisValues(defaults);
          }
        }
      })
      .catch(err => console.error('Error loading families:', err))
      .finally(() => setIsFamiliesLoading(false));
  }, []);

  // Run initial compatibility evaluation on mount or preset switch
  const handleRunEvaluation = async (productA = prodA, productB = prodB) => {
    setIsEvaluatingCompat(true);
    try {
      const res = await fetch('/api/v1/compatibility/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_a: productA,
          product_b: productB
        })
      });
      const data = await res.json();
      if (data.success) {
        setCompatResult(data.result);
      }
    } catch (err) {
      console.error('Error evaluating compatibility:', err);
    } finally {
      setIsEvaluatingCompat(false);
    }
  };

  useEffect(() => {
    handleRunEvaluation(prodA, prodB);
  }, [selectedPairingIdx]);

  const families = familiesData?.families || [];
  const activeFamily = families.find(f => f.family_id === selectedFamilyId) || families[0];

  const handleSelectFamily = (fam) => {
    setSelectedFamilyId(fam.family_id);
    const defaults = {};
    fam.variant_axes.forEach(ax => {
      if (ax.values.length > 0) defaults[ax.name] = ax.values[0];
    });
    setSelectedAxisValues(defaults);
  };

  const handleAxisSelect = (axisName, val) => {
    setSelectedAxisValues(prev => ({
      ...prev,
      [axisName]: val
    }));
  };

  const activeVariant = activeFamily?.variants.find(v => {
    return Object.entries(selectedAxisValues).every(([k, val]) => v.axis_values[k] === val);
  }) || activeFamily?.variants[0];

  return (
    <div className="space-y-6 pb-12">
      
      {/* Intelligence Hub Header & Tab Switcher */}
      <div className="p-6 rounded-2xl bg-surface-elevated border border-surface-border shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-indigo-950 border border-indigo-800 flex items-center justify-center text-indigo-400 shadow-md">
              <GitBranch className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">Industrial Product Intelligence Hub</h1>
              <p className="text-xs text-slate-400">
                Product Families • Compatibility & Substitutes Matrix • 27K UniCat Knowledge Graph
              </p>
            </div>
          </div>

          {/* Sub-Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-1 bg-surface p-1 rounded-xl border border-surface-border">
            <button
              onClick={() => setActiveTab('FAMILIES')}
              className={`flex items-center space-x-2 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-lg text-xs font-mono font-semibold transition-all cursor-pointer ${
                activeTab === 'FAMILIES'
                  ? 'bg-indigo-950 text-indigo-300 border border-indigo-700 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Layers className="h-4 w-4" />
              <span>Product Families</span>
            </button>

            <button
              onClick={() => setActiveTab('COMPATIBILITY')}
              className={`flex items-center space-x-2 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-lg text-xs font-mono font-semibold transition-all cursor-pointer ${
                activeTab === 'COMPATIBILITY'
                  ? 'bg-purple-950 text-purple-300 border border-purple-700 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <GitCompare className="h-4 w-4" />
              <span>Compatibility Matrix</span>
            </button>

            <button
              onClick={() => setActiveTab('KB')}
              className={`flex items-center space-x-2 px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-lg text-xs font-mono font-semibold transition-all cursor-pointer ${
                activeTab === 'KB'
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-700 shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <BookOpen className="h-4 w-4" />
              <span>UniCat KB Explorer</span>
            </button>
          </div>
        </div>
      </div>

      {/* TAB 1: PRODUCT FAMILIES & VARIANT INDUCTION */}
      {activeTab === 'FAMILIES' && (
        <div className="rounded-2xl border border-surface-border bg-surface-elevated overflow-hidden shadow-xl">
          <div className="grid grid-cols-1 md:grid-cols-12 divide-y md:divide-y-0 md:divide-x divide-surface-border min-h-[600px]">
            
            {/* Left: Families List */}
            <div className="md:col-span-4 p-4 overflow-y-auto max-h-[260px] md:max-h-none bg-slate-950/40 space-y-2.5">
              <div className="flex items-center justify-between pb-2 border-b border-surface-border text-xs font-mono text-slate-400">
                <span>Discovered Families ({families.length})</span>
                <span>{familiesData?.total_child_skus_clustered || 0} Child SKUs</span>
              </div>

              {families.map((fam) => {
                const isSelected = fam.family_id === activeFamily?.family_id;
                const hasGaps = fam.detected_gaps && fam.detected_gaps.length > 0;
                return (
                  <div
                    key={fam.family_id}
                    onClick={() => handleSelectFamily(fam)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-1.5 ${
                      isSelected
                        ? 'bg-indigo-950/40 border-indigo-600 shadow-md'
                        : 'bg-surface border-surface-border hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-white font-mono">{fam.brand_name}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-indigo-300 border border-indigo-900">
                        {fam.total_variants} Variants
                      </span>
                    </div>

                    <h4 className="text-xs font-semibold text-slate-200">
                      {fam.family_name}
                    </h4>

                    <div className="text-[10px] font-mono text-slate-400 truncate">
                      Base Series: <span className="text-indigo-400 font-semibold">{fam.base_series_mpn}</span>
                    </div>

                    {hasGaps && (
                      <div className="pt-1 flex items-center space-x-1 text-[10px] font-mono text-amber-400">
                        <AlertTriangle className="h-3 w-3" />
                        <span>{fam.detected_gaps.length} Assortment Gap Detected</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Right: Interactive Parent PDP & Variant Switcher */}
            <div className="md:col-span-8 p-6 overflow-y-auto space-y-6 bg-slate-950/20">
              {activeFamily ? (
                <>
                  {/* Parent Series Card */}
                  <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-indigo-400">{activeFamily.brand_name} Master Series</span>
                      <span className="text-[11px] font-mono px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                        Parent ID: {activeFamily.family_id}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-white tracking-tight">
                      {activeFamily.family_name}
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Category: {activeFamily.category_path}
                    </p>
                  </div>

                  {/* Assortment Gap Warning */}
                  {activeFamily.detected_gaps && activeFamily.detected_gaps.map((gap, i) => (
                    <div key={i} className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/60 text-xs font-mono space-y-2">
                      <div className="flex items-center justify-between text-amber-400">
                        <div className="flex items-center space-x-2 font-bold">
                          <AlertTriangle className="h-4 w-4" />
                          <span>Assortment Sequence Gap: Missing {gap.missing_sizes.join(', ')}</span>
                        </div>
                        <span className="px-2 py-0.5 rounded bg-amber-950 text-[10px] border border-amber-800">
                          {gap.confidence_level}
                        </span>
                      </div>
                      <p className="text-slate-300 text-[11px]">
                        {gap.evidence_notes}
                      </p>
                      <div className="flex items-center space-x-2 text-[10px] pt-1">
                        <span className="text-emerald-400 font-semibold">In Catalog:</span>
                        <span className="text-slate-400">{gap.present_sizes.join(' ➔ ')}</span>
                      </div>
                    </div>
                  ))}

                  {/* Multi-Axis Variant Selector */}
                  <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
                    <div className="flex items-center space-x-2 text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
                      <Layers className="h-4 w-4 text-indigo-400" />
                      <span>Select Variant Configuration</span>
                    </div>

                    {activeFamily.variant_axes.map((axis) => (
                      <div key={axis.name} className="space-y-2">
                        <label className="text-xs font-mono text-slate-400">
                          {axis.name}:
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {axis.values.map((val) => {
                            const isSelected = selectedAxisValues[axis.name] === val;
                            return (
                              <button
                                key={val}
                                type="button"
                                onClick={() => handleAxisSelect(axis.name, val)}
                                className={`px-3.5 py-1.5 rounded-lg text-xs font-mono border transition-all cursor-pointer ${
                                  isSelected
                                    ? 'bg-indigo-950 text-indigo-200 border-indigo-500 shadow-sm'
                                    : 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
                                }`}
                              >
                                {val}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Active Variant SKU Card */}
                  {activeVariant && (
                    <div className="p-5 rounded-xl bg-indigo-950/20 border border-indigo-800/50 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          <span className="text-xs font-bold text-white font-mono">
                            Active Variant SKU: <span className="text-indigo-400">{activeVariant.mpn}</span>
                          </span>
                        </div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                          Resolved Variant SKU
                        </span>
                      </div>

                      <h4 className="text-sm font-semibold text-slate-100">
                        {activeVariant.short_desc}
                      </h4>

                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 text-[11px] font-mono">
                        {Object.entries(activeVariant.axis_values).map(([k, v]) => (
                          <div key={k} className="p-2 rounded bg-slate-950 border border-slate-800">
                            <span className="text-slate-500 block text-[10px]">{k}</span>
                            <span className="text-slate-200 font-semibold">{v}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Child Variant Matrix Table */}
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                      Full Sibling Variant Matrix ({activeFamily.variants.length} SKUs)
                    </h4>
                    <div className="rounded-xl border border-surface-border overflow-hidden">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-slate-900 border-b border-surface-border text-slate-400 text-[11px]">
                          <tr>
                            <th className="p-3">MPN</th>
                            <th className="p-3">Specification</th>
                            <th className="p-3">Attributes</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-surface-border bg-surface">
                          {activeFamily.variants.map((v, idx) => (
                            <tr key={`${v.mpn}-${idx}`} className="hover:bg-surface-elevated transition-colors">
                              <td className="p-3 font-bold text-cyan-300">{v.mpn}</td>
                              <td className="p-3 text-slate-200">{v.short_desc}</td>
                              <td className="p-3 text-slate-400">
                                {Object.entries(v.axis_values).map(([k, val]) => `${k}: ${val}`).join(' | ')}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-12 text-center text-xs text-slate-500 font-mono">
                  Select a Product Family from the left to view the interactive matrix.
                </div>
              )}
            </div>

          </div>
        </div>
      )}

      {/* TAB 2: INDUSTRIAL COMPATIBILITY & SUBSTITUTES MATRIX */}
      {activeTab === 'COMPATIBILITY' && (
        <div className="space-y-8">
          
          {/* SECTION A: PAIRWISE MECHANICAL & ELECTRICAL EVALUATOR */}
          <div className="p-6 rounded-2xl bg-surface-elevated border border-surface-border space-y-5 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
              <div className="flex items-center space-x-2.5">
                <div className="h-9 w-9 rounded-xl bg-purple-950 border border-purple-800 flex items-center justify-center text-purple-400 shadow-md">
                  <GitCompare className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                    Pairwise Multi-Domain Compatibility Evaluator
                  </h2>
                  <p className="text-xs text-slate-400">
                    Evaluates mechanical mounts, arbor sizing, voltage platform parity, and kinetic safety boundaries.
                  </p>
                </div>
              </div>

              <button
                onClick={() => handleRunEvaluation(prodA, prodB)}
                disabled={isEvaluatingCompat}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400 text-white font-bold text-xs shadow-md shadow-purple-500/20 cursor-pointer transition-all shrink-0"
              >
                {isEvaluatingCompat ? 'Evaluating Physics & Specs...' : 'Evaluate Pairwise Fit'}
              </button>
            </div>

            {/* Presets Selector */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-1">
              <span className="text-[11px] font-mono text-slate-400 shrink-0">Sample Test Scenarios:</span>
              {PRESET_PAIRINGS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setSelectedPairingIdx(idx);
                    setProdA(p.prodA);
                    setProdB(p.prodB);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono border transition-all cursor-pointer shrink-0 ${
                    selectedPairingIdx === idx
                      ? 'bg-purple-950 text-purple-200 border-purple-500 shadow-sm'
                      : 'bg-surface hover:bg-surface-elevated text-slate-400 border-surface-border hover:text-slate-200'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Pairwise Product Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-cyan-400">Product A (Tool / Host / Master)</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                    MPN: {prodA.Mfg_Part_Num || 'DWE402'}
                  </span>
                </div>
                <input
                  type="text"
                  value={prodA.SHORT_DESC || ''}
                  onChange={(e) => setProdA({ ...prodA, SHORT_DESC: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-purple-400">Product B (Accessory / Disc / Mate)</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                    MPN: {prodB.Mfg_Part_Num || '49-94-0101'}
                  </span>
                </div>
                <input
                  type="text"
                  value={prodB.SHORT_DESC || ''}
                  onChange={(e) => setProdB({ ...prodB, SHORT_DESC: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>

            {/* Live Evaluation Result Card */}
            {compatResult ? (
              <div className={`p-5 rounded-xl border space-y-3 font-mono text-xs shadow-md transition-all ${
                compatResult.is_compatible
                  ? 'bg-emerald-950/25 border-emerald-800/80'
                  : 'bg-rose-950/30 border-rose-800/80'
              }`}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2.5">
                    {compatResult.is_compatible ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
                    ) : (
                      <XCircle className="h-5 w-5 text-rose-400 shrink-0" />
                    )}
                    <span className="text-sm font-bold text-white">
                      Evaluation Outcome: <span className={compatResult.is_compatible ? 'text-emerald-400' : 'text-rose-400'}>{compatResult.compatibility_status}</span>
                    </span>
                  </div>
                  <span className="text-xs text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    Domain: <span className="text-slate-200 font-semibold">{compatResult.domain || 'MECHANICAL_FIT'}</span>
                  </span>
                </div>

                <p className="text-slate-300 text-xs leading-relaxed">
                  {compatResult.reasoning}
                </p>

                {compatResult.constraint_checks && compatResult.constraint_checks.length > 0 && (
                  <div className="pt-3 space-y-2 border-t border-slate-800/80">
                    <span className="text-slate-400 font-bold block text-[11px] uppercase tracking-wider">
                      Evaluated Physical Constraints & Bounds:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      {compatResult.constraint_checks.map((c, i) => (
                        <div key={i} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-[11px]">
                          <span className="text-slate-300 font-semibold">{c.constraint_name}</span>
                          <span className={`font-bold ${c.passed ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {c.passed ? '✓ PASSED' : '❌ FAILED'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 rounded-xl bg-slate-950 border border-surface-border text-center text-xs text-slate-500 font-mono">
                Click "Evaluate Pairwise Fit" or select a preset scenario above to execute the compatibility check.
              </div>
            )}
          </div>

          {/* SECTION B: DIRECT CROSS-BRAND OEM SUBSTITUTES & EQUIVALENTS */}
          <div className="p-6 rounded-2xl bg-surface-elevated border border-surface-border space-y-5 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
              <div className="flex items-center space-x-2.5">
                <div className="h-9 w-9 rounded-xl bg-teal-950 border border-teal-800 flex items-center justify-center text-teal-400 shadow-md">
                  <ArrowRightLeft className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                    Direct Cross-Brand OEM Functional Substitutes
                  </h2>
                  <p className="text-xs text-slate-400">
                    Discovers direct Form-Fit-Function equivalents for contractor supply chain resilience.
                  </p>
                </div>
              </div>

              {/* Preset Selector */}
              <div className="flex items-center space-x-1.5 bg-surface p-1 rounded-xl border border-surface-border">
                {OEM_SUBSTITUTES_PRESETS.map((sub, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setSelectedSubPresetIdx(idx)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all cursor-pointer ${
                      selectedSubPresetIdx === idx
                        ? 'bg-teal-950 text-teal-300 border border-teal-700 shadow-sm'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    MPN: {sub.targetMpn}
                  </button>
                ))}
              </div>
            </div>

            {/* Target Product Reference */}
            <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-1">
              <span className="text-[10px] font-mono uppercase text-slate-400 block font-bold">
                Target Master SKU to Replace:
              </span>
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white font-mono">
                  {OEM_SUBSTITUTES_PRESETS[selectedSubPresetIdx].targetTitle}
                </h3>
                <span className="text-xs font-mono text-cyan-400 font-bold px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800">
                  Target MPN: {OEM_SUBSTITUTES_PRESETS[selectedSubPresetIdx].targetMpn}
                </span>
              </div>
            </div>

            {/* Substitutes Cards List */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {OEM_SUBSTITUTES_PRESETS[selectedSubPresetIdx].substitutes.map((sub, i) => (
                <div
                  key={i}
                  className="p-4 rounded-xl bg-surface border border-surface-border hover:border-teal-700/80 transition-all space-y-3 shadow-md flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-white font-mono">{sub.brand}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold">
                        {sub.matchScore}% Match
                      </span>
                    </div>

                    <h4 className="text-xs font-bold text-slate-200 font-mono">
                      {sub.mpn}
                    </h4>

                    <p className="text-xs text-slate-400 leading-snug">
                      {sub.title}
                    </p>
                  </div>

                  <div className="space-y-1 pt-2 border-t border-surface-border">
                    <span className="text-[10px] font-mono text-slate-500 block uppercase">
                      Parity Evidence:
                    </span>
                    {sub.reasons.map((r, idx) => (
                      <div key={idx} className="text-[11px] font-mono text-teal-300 flex items-center space-x-1">
                        <span>• {r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

          </div>

        </div>
      )}

      {/* TAB 3: UNICAT KNOWLEDGE BASE EXPLORER */}
      {activeTab === 'KB' && (
        <KnowledgeBaseExplorer />
      )}

    </div>
  );
}
