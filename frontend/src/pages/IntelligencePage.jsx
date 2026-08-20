import React, { useState, useEffect } from 'react';
import { GitBranch, Layers, GitCompare, BookOpen, AlertTriangle, CheckCircle2, Search, ArrowRight, ShieldCheck, Box } from 'lucide-react';
import KnowledgeBaseExplorer from '../components/KnowledgeBaseExplorer';

export default function IntelligencePage() {
  const [activeTab, setActiveTab] = useState('FAMILIES'); // 'FAMILIES', 'COMPATIBILITY', 'KB'

  // Families State
  const [familiesData, setFamiliesData] = useState(null);
  const [selectedFamilyId, setSelectedFamilyId] = useState(null);
  const [selectedAxisValues, setSelectedAxisValues] = useState({});
  const [isFamiliesLoading, setIsFamiliesLoading] = useState(false);

  // Compatibility State
  const [prodA, setProdA] = useState({
    title: 'DEWALT 20V MAX 4-1/2 in Angle Grinder DCG413B',
    arbor: '7/8 in',
    voltage: '20V',
    rpm: '9000',
    type: 'Tool'
  });
  const [prodB, setProdB] = useState({
    title: 'Milwaukee 4-1/2 in x .045 in x 7/8 in Metal Cut-Off Wheel 49-94-0101',
    arbor: '7/8 in',
    voltage: 'N/A',
    rpm: '13300',
    type: 'Abrasive Wheel'
  });
  const [compatResult, setCompatResult] = useState(null);
  const [isEvaluatingCompat, setIsEvaluatingCompat] = useState(false);

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

  // Evaluate Compatibility
  const handleEvaluateCompatibility = async () => {
    setIsEvaluatingCompat(true);
    try {
      const res = await fetch('/api/v1/compatibility/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_a: { SHORT_DESC: prodA.title, Part_Desc: prodA.title },
          product_b: { SHORT_DESC: prodB.title, Part_Desc: prodB.title }
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
                          {activeFamily.variants.map((v) => (
                            <tr key={v.mpn} className="hover:bg-surface-elevated transition-colors">
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
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-surface-elevated border border-surface-border space-y-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-surface-border pb-3">
              <div className="flex items-center space-x-2.5">
                <GitCompare className="h-5 w-5 text-purple-400" />
                <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">Pairwise Multi-Domain Compatibility Evaluator</h2>
              </div>
              <button
                onClick={handleEvaluateCompatibility}
                disabled={isEvaluatingCompat}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400 text-white font-bold text-xs shadow-md shadow-purple-500/20 cursor-pointer transition-all"
              >
                {isEvaluatingCompat ? 'Evaluating...' : 'Evaluate Pairwise Compatibility'}
              </button>
            </div>

            {/* Pairwise Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <span className="text-xs font-mono font-bold text-cyan-400">Product A (Tool / Host / Master)</span>
                <input
                  type="text"
                  value={prodA.title}
                  onChange={(e) => setProdA({ ...prodA, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <span className="text-xs font-mono font-bold text-purple-400">Product B (Accessory / Disc / Mate)</span>
                <input
                  type="text"
                  value={prodB.title}
                  onChange={(e) => setProdB({ ...prodB, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>

            {/* Compatibility Result Breakdown */}
            {compatResult && (
              <div className="p-5 rounded-xl bg-slate-950 border border-surface-border space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {compatResult.is_compatible ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-rose-400" />
                    )}
                    <span className="text-sm font-bold text-white">
                      Status: {compatResult.compatibility_status}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">Domain: {compatResult.domain}</span>
                </div>

                <p className="text-slate-300 text-xs">
                  {compatResult.reasoning}
                </p>

                {compatResult.constraint_checks && compatResult.constraint_checks.length > 0 && (
                  <div className="pt-2 space-y-1.5 border-t border-slate-800">
                    <span className="text-slate-400 font-bold block text-[11px]">Evaluated Physical Constraints:</span>
                    {compatResult.constraint_checks.map((c, i) => (
                      <div key={i} className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-300">{c.constraint_name}</span>
                        <span className={c.passed ? 'text-emerald-400' : 'text-rose-400'}>
                          {c.passed ? '✓ PASSED' : '❌ FAILED'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
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
