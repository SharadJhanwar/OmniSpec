import React from 'react';
import {
  Upload,
  FileSpreadsheet,
  Download,
  Menu,
  X,
  Sparkles,
  Workflow
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';

export default function TopHeader({ onToggleMobileMenu, isMobileMenuOpen }) {
  const {
    items,
    activeBatchName,
    handleResetCatalog,
    handleExportCSV,
    handleExportExcel,
    setIsUploadOpen
  } = useCatalog();

  return (
    <header className="h-14 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-xl px-4 sm:px-6 flex items-center justify-between z-30 sticky top-0">
      {/* Left: Clean Brand & Mobile Toggle */}
      <div className="flex items-center space-x-3">
        <button
          type="button"
          onClick={onToggleMobileMenu}
          className="lg:hidden p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
        >
          {isMobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </button>

        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span className="text-slate-200 font-semibold">OmniSpec AI</span>
          <span className="text-slate-600 hidden sm:inline">•</span>
          <span className="text-slate-400 hidden sm:inline">252-Column Industrial Catalog Intelligence</span>
        </div>
      </div>

      {/* Right: Clean Action Buttons */}
      <div className="flex items-center space-x-2 sm:space-x-3 text-xs">
        {activeBatchName && (
          <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-cyan-950/80 border border-cyan-700/60 text-cyan-300 text-[11px] font-mono">
            <span className="truncate max-w-[120px]" title={activeBatchName}>📄 {activeBatchName}</span>
            <span className="px-1 rounded bg-cyan-900 text-cyan-200 font-bold">{items.length}</span>
            <button 
              onClick={handleResetCatalog}
              className="ml-1 text-slate-400 hover:text-white p-0.5 rounded cursor-pointer"
              title="Reset to full catalog"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        )}

        {/* Upload Feed Button */}
        <button
          type="button"
          onClick={() => setIsUploadOpen(true)}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-200 text-xs font-medium transition-all shadow-sm cursor-pointer"
          title="Upload Catalog (CSV / Excel)"
        >
          <Upload className="w-3.5 h-3.5 text-slate-400" />
          <span className="hidden sm:inline">Upload Feed</span>
        </button>

        {/* Export Excel Button */}
        <button
          type="button"
          onClick={handleExportExcel}
          className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900/90 border border-emerald-700/60 text-emerald-300 text-xs font-medium transition-all shadow-sm cursor-pointer"
          title="Export formatted multi-sheet Excel (.xlsx)"
        >
          <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
          <span>Export Excel</span>
        </button>

        {/* Export CSV Button */}
        <button
          type="button"
          onClick={handleExportCSV}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-cyan-500/20 cursor-pointer"
          title="Export 252-Column Delivery CSV"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export CSV</span>
        </button>
      </div>
    </header>
  );
}
