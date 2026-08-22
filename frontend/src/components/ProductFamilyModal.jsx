import React, { useState, useEffect } from 'react';
import { Layers, GitBranch, AlertTriangle, CheckCircle2, X, Box, Tag, Zap, ArrowRight, ShieldCheck, ChevronRight } from 'lucide-react';
import { apiUrl } from '../config/api';

export default function ProductFamilyModal({ isOpen, onClose }) {
  const [familiesData, setFamiliesData] = useState(null);
  const [selectedFamilyId, setSelectedFamilyId] = useState(null);
  const [selectedAxisValues, setSelectedAxisValues] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      fetch(apiUrl('/api/v1/families'))
        .then(res => res.json())
        .then(data => {
          if (data.success && data.data) {
            setFamiliesData(data.data);
            if (data.data.families.length > 0) {
              setSelectedFamilyId(data.data.families[0].family_id);
              // Init default selected axis values for first family
              const firstFam = data.data.families[0];
              const defaults = {};
              firstFam.variant_axes.forEach(ax => {
                if (ax.values.length > 0) defaults[ax.name] = ax.values[0];
              });
              setSelectedAxisValues(defaults);
            }
          }
        })
        .catch(err => console.error('Error loading product families:', err))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

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

  // Find active variant matching selected axis values
  const activeVariant = activeFamily?.variants.find(v => {
    return Object.entries(selectedAxisValues).every(([k, val]) => v.axis_values[k] === val);
  }) || activeFamily?.variants[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-surface-elevated border border-surface-border rounded-2xl w-full max-w-6xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-surface-border flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-indigo-950 border border-indigo-800 flex items-center justify-center text-indigo-400 shadow-md">
              <GitBranch className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-lg font-bold text-white tracking-tight">Parent Product Family & Variant Induction Studio</h2>
                <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-indigo-950 text-indigo-400 border border-indigo-800 font-semibold">
                  Matrix Induction & Gap Detector
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Deterministic MPN Series Decomposition, Multi-Axis Variant Induction & Evidence-Backed Assortment Gap Detection
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

        {/* Main Content: 2-Column Split (Sidebar vs Parent PDP) */}
        <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-12 divide-y md:divide-y-0 md:divide-x divide-surface-border">
          
          {/* Left Sidebar: Discovered Product Families List */}
          <div className="md:col-span-4 lg:col-span-4 p-4 overflow-y-auto bg-slate-950/40 space-y-2.5">
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
                    Base MPN: <span className="text-indigo-400">{fam.base_series_mpn}</span>
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

          {/* Right Main View: Interactive Parent PDP & Variant Switcher */}
          <div className="md:col-span-8 lg:col-span-8 p-6 overflow-y-auto space-y-6 bg-slate-950/20">
            {activeFamily ? (
              <>
                {/* Parent Family Banner */}
                <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-indigo-400">{activeFamily.brand_name} Master Series</span>
                    <span className="text-[11px] font-mono px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                      Parent ID: {activeFamily.family_id}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-white tracking-tight">
                    {activeFamily.family_name}
                  </h3>
                  <div className="text-xs text-slate-400 font-mono">
                    Category: {activeFamily.category_path}
                  </div>
                </div>

                {/* Assortment Gap Warning (If Detected) */}
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

                {/* Interactive Multi-Axis Variant Switcher */}
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

                {/* Child Matrix Table */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                    Full Sibling Variant Matrix ({activeFamily.variants.length} SKUs)
                  </h4>
                  <div className="rounded-xl border border-surface-border overflow-hidden">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-900 border-b border-surface-border text-slate-400 text-[11px]">
                        <tr>
                          <th className="p-3">MPN</th>
                          <th className="p-3">Variant Specification</th>
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
                Select a Product Family from the left to view the interactive variant matrix.
              </div>
            )}
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-surface-border bg-slate-900/60 flex items-center justify-between">
          <div className="text-xs text-slate-400 font-mono">
            Powered by OmniSpec Product Family Clustering & Variant Induction Engine
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-surface hover:bg-surface-border text-xs font-semibold text-white transition-colors cursor-pointer"
          >
            Close Family Studio
          </button>
        </div>

      </div>
    </div>
  );
}
