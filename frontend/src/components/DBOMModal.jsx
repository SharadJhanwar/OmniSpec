import React, { useState } from 'react';
import { ShieldCheck, FileText, Link, Search, CheckCircle2, AlertTriangle, Hash, ExternalLink, X, Database, Layers, Sparkles } from 'lucide-react';

export default function DBOMModal({ isOpen, onClose, dbomData, isLoading }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSource, setFilterSource] = useState('ALL');

  if (!isOpen) return null;

  const dbom = dbomData?.dbom || {};
  const riskEval = dbomData?.risk_evaluation || {};
  const cells = dbom?.provenance_cells || {};

  const cellList = Object.values(cells).filter(cell => {
    const matchesSearch = cell.column_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          String(cell.value).toLowerCase().includes(searchTerm.toLowerCase()) ||
                          cell.rule_applied.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSource = filterSource === 'ALL' || cell.source_type === filterSource;
    return matchesSearch && matchesSource;
  });

  const getSourceBadge = (sourceType) => {
    switch (sourceType) {
      case 'OEM_SPEC_SHEET_PDF':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-950 text-purple-300 border border-purple-800">OEM PDF Datasheet</span>;
      case 'OEM_OFFICIAL_URL':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-950 text-blue-300 border border-blue-800">OEM Verified URL</span>;
      case 'UNICAT_BRAND_KB':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800">UniCat Brand (27K)</span>;
      case 'UNICAT_LOV_KB':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800">UniCat LOV (161K)</span>;
      case 'FORMULA_DERIVED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800">Formula Derived</span>;
      case 'SUPPLIER_RAW_FEED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">Raw Supplier Feed</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400">{sourceType}</span>;
    }
  };

  const getRiskBadge = (tier) => {
    switch (tier) {
      case 'LOW':
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800 flex items-center space-x-1"><CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Low Risk (Auto-Approve)</span>;
      case 'ELEVATED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950 text-amber-400 border border-amber-800 flex items-center space-x-1"><AlertTriangle className="h-3.5 w-3.5 mr-1" /> Elevated Risk (Audit)</span>;
      case 'CRITICAL':
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950 text-rose-400 border border-rose-800 flex items-center space-x-1"><AlertTriangle className="h-3.5 w-3.5 mr-1" /> Critical (HITL Required)</span>;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-surface-elevated border border-surface-border rounded-2xl w-full max-w-6xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-6 border-b border-surface-border flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400 shadow-md">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-lg font-bold text-white tracking-tight">Data Bill of Materials (DBOM) & Lineage Explorer</h2>
                <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold">
                  SHA-256 Cryptographic Lineage
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Cell-level evidentiary provenance, extraction method audit, and Defect Probability Index (DPI)
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

        {/* Product Identity & KPI Banner */}
        <div className="p-5 border-b border-surface-border bg-slate-950/40 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-3 rounded-xl bg-surface border border-surface-border">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Target Product Master</span>
            <div className="font-bold text-white text-sm truncate">{dbom.brand_name} {dbom.mpn}</div>
            <div className="text-xs text-slate-400 truncate">{dbom.manufacturer_name}</div>
          </div>

          <div className="p-3 rounded-xl bg-surface border border-surface-border">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Defect Probability Index (DPI)</span>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold font-mono text-cyan-400">
                {Math.round((dbom.defect_probability_index || 0) * 100)}%
              </span>
              {getRiskBadge(dbom.risk_tier)}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-surface border border-surface-border">
            <span className="text-[11px] font-mono text-slate-400 block mb-1">Attributes & Verified Sources</span>
            <div className="flex items-center space-x-4">
              <div>
                <span className="text-xs text-slate-500">Tracked:</span> <span className="font-bold text-white text-sm font-mono">{dbom.total_attributes_tracked || 0}</span>
              </div>
              <div>
                <span className="text-xs text-slate-500">OEM Sources:</span> <span className="font-bold text-emerald-400 text-sm font-mono">{dbom.verified_oem_sources_count || 0}</span>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-surface border border-surface-border">
            <span className="text-[11px] font-mono text-slate-400 block mb-1 flex items-center">
              <Hash className="h-3 w-3 mr-1 text-slate-500" /> Lineage Hash (SHA-256)
            </span>
            <div className="text-[10px] font-mono text-slate-400 truncate bg-slate-900/80 p-1 rounded border border-slate-800" title={dbom.lineage_hash}>
              {dbom.lineage_hash ? `${dbom.lineage_hash.slice(0, 16)}...${dbom.lineage_hash.slice(-8)}` : 'Generating...'}
            </div>
          </div>
        </div>

        {/* Risk Factors Banner if any */}
        {riskEval?.top_risk_factors?.length > 0 && (
          <div className="px-6 py-2.5 bg-cyan-950/20 border-b border-cyan-900/30 flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2 text-cyan-300">
              <Sparkles className="h-4 w-4 text-cyan-400 shrink-0" />
              <span className="font-semibold">Top Risk Analysis Factors:</span>
              <span className="text-slate-300">{riskEval.top_risk_factors.join(' • ')}</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-900/40 text-cyan-300">
              Action: {riskEval.recommended_action}
            </span>
          </div>
        )}

        {/* Filter Controls */}
        <div className="p-4 border-b border-surface-border flex flex-wrap items-center justify-between gap-3 bg-surface/50">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search column name, value, or governance rule..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-surface border border-surface-border text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">Filter Source:</span>
            <select
              value={filterSource}
              onChange={(e) => setFilterSource(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono cursor-pointer"
            >
              <option value="ALL">All Source Types ({Object.keys(cells).length})</option>
              <option value="OEM_SPEC_SHEET_PDF">OEM PDF Datasheet</option>
              <option value="OEM_OFFICIAL_URL">OEM Verified URL</option>
              <option value="UNICAT_BRAND_KB">UniCat Brand KB</option>
              <option value="UNICAT_LOV_KB">UniCat LOV KB</option>
              <option value="FORMULA_DERIVED">Formula Derived</option>
              <option value="SUPPLIER_RAW_FEED">Supplier Raw Feed</option>
            </select>
          </div>
        </div>

        {/* Cell Provenance Table */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="border border-surface-border rounded-xl overflow-hidden shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/90 border-b border-surface-border text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                  <th className="py-2.5 px-3">Column Name</th>
                  <th className="py-2.5 px-3">Enriched Value</th>
                  <th className="py-2.5 px-3">Source Type</th>
                  <th className="py-2.5 px-3">Source Reference / Locator</th>
                  <th className="py-2.5 px-3">Extraction Agent & Method</th>
                  <th className="py-2.5 px-3">Governance Rule Applied</th>
                  <th className="py-2.5 px-3 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border text-xs">
                {cellList.length > 0 ? (
                  cellList.map((cell, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/50 transition-colors">
                      <td className="py-2.5 px-3 font-mono font-semibold text-cyan-300 whitespace-nowrap">
                        {cell.column_name}
                      </td>
                      <td className="py-2.5 px-3 text-white font-medium max-w-[220px] truncate" title={cell.value}>
                        {cell.value}
                      </td>
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        {getSourceBadge(cell.source_type)}
                      </td>
                      <td className="py-2.5 px-3 text-slate-300 max-w-[240px]">
                        <div className="text-[11px] text-slate-200 truncate" title={cell.source_ref}>
                          {cell.source_ref}
                        </div>
                        {cell.locator && (
                          <div className="text-[10px] font-mono text-slate-500 truncate" title={cell.locator}>
                            📍 {cell.locator}
                          </div>
                        )}
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="text-[11px] font-mono text-slate-300">{cell.agent_name}</div>
                        <div className="text-[10px] text-slate-500 font-mono">{cell.extraction_method}</div>
                      </td>
                      <td className="py-2.5 px-3 text-[11px] text-slate-300 max-w-[220px]">
                        <span className="line-clamp-2" title={cell.rule_applied}>
                          {cell.rule_applied}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono font-semibold">
                        <span className={cell.confidence >= 0.95 ? "text-emerald-400" : "text-amber-400"}>
                          {Math.round(cell.confidence * 100)}%
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="py-8 text-center text-slate-500">
                      No provenance cells match your search criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-surface-border bg-slate-900/60 flex items-center justify-between">
          <div className="text-xs text-slate-400 flex items-center space-x-2 font-mono">
            <span>Showing {cellList.length} of {Object.keys(cells).length} tracked delivery cells</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-surface hover:bg-surface-border text-xs font-semibold text-white transition-colors cursor-pointer"
          >
            Close Inspector
          </button>
        </div>

      </div>
    </div>
  );
}
