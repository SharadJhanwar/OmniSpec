import React from 'react';
import { Layers, Cpu, ShieldCheck, Sparkles, Download, Upload, FileSpreadsheet, GitCompare } from 'lucide-react';

export default function Navbar({ onUploadClick, onExportClick, onExportExcelClick, onCompatibilityClick, isProcessing, totalRows }) {
  return (
    <header className="sticky top-0 z-40 border-b border-surface-border glass-panel">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-sky-400 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Layers className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white">OmniSpec<span className="text-cyan-400">.AI</span></span>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold">
                LangGraph 9-Agent DAG
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Industrial Product Intelligence • 252-Column Master Truth</p>
          </div>
        </div>

        {/* Live Swarm Status & Actions */}
        <div className="flex items-center space-x-2.5">
          <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-xs font-mono text-slate-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>DuckDB + RapidFuzz Engine</span>
            <span className="text-slate-500">|</span>
            <span className="text-cyan-400 font-medium">154 SKUs/s</span>
          </div>

          <button
            onClick={onCompatibilityClick}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-purple-950/80 hover:bg-purple-900/90 border border-purple-700/60 text-purple-300 font-semibold text-xs transition-all shadow-sm cursor-pointer"
            title="Open Industrial Compatibility & Cross-Brand Substitute Matrix"
          >
            <GitCompare className="h-4 w-4 text-purple-400" />
            <span className="hidden sm:inline">Compatibility Matrix</span>
          </button>

          <button
            onClick={onUploadClick}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-surface hover:bg-surface-elevated border border-surface-border text-xs font-medium text-slate-200 transition-all shadow-sm cursor-pointer"
          >
            <Upload className="h-4 w-4 text-slate-400" />
            <span className="hidden sm:inline">Upload Feed</span>
          </button>

          <button
            onClick={onExportExcelClick}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-emerald-950/80 hover:bg-emerald-900/90 border border-emerald-700/60 text-emerald-300 font-semibold text-xs transition-all shadow-sm cursor-pointer"
            title="Export formatted multi-sheet Excel workbook with frozen panes and compliance audit"
          >
            <FileSpreadsheet className="h-4 w-4 text-emerald-400" />
            <span>Excel (.xlsx)</span>
          </button>

          <button
            onClick={onExportClick}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-semibold text-xs transition-all shadow-md shadow-cyan-500/20 cursor-pointer"
          >
            <Download className="h-4 w-4" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>
    </header>
  );
}
