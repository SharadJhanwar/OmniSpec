import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  Layers,
  ShieldAlert,
  Sparkles,
  GitBranch,
  Upload,
  FileSpreadsheet,
  Download,
  Menu,
  X,
  Cpu
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';

export default function Navbar() {
  const { hitlCount, items, activeBatchName, handleResetCatalog, handleExportCSV, handleExportExcel, setIsUploadOpen } = useCatalog();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    {
      name: 'Studio & Grid',
      path: '/studio',
      icon: Layers,
      badge: `${items.length}`
    },
    {
      name: 'HITL Review',
      path: '/review',
      icon: ShieldAlert,
      badge: hitlCount > 0 ? `${hitlCount}` : '0',
      badgeColor: hitlCount > 0 ? 'bg-amber-950/90 text-amber-400 border-amber-800' : 'bg-emerald-950/90 text-emerald-400 border-emerald-800'
    },
    {
      name: 'Parametric Search',
      path: '/search',
      icon: Sparkles
    },
    {
      name: 'Intelligence Hub',
      path: '/intelligence',
      icon: Cpu
    }
  ];

  return (
    <header className="sticky top-0 z-50 w-full glass-panel border-b border-surface-border/80 backdrop-blur-xl">
      <div className="max-w-[1780px] mx-auto flex items-center justify-between px-3 sm:px-6 h-16">
        
        {/* Brand / Logo */}
        <Link to="/" className="flex items-center space-x-2.5 group">
          <div className="relative flex items-center justify-center h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-sky-400 text-slate-950 font-black shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform duration-200">
            <Cpu className="h-5 w-5" />
            <div className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-emerald-400 border-2 border-surface animate-pulse" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center space-x-1.5">
              <span className="font-extrabold text-base tracking-tight text-white group-hover:text-cyan-400 transition-colors font-mono">
                OmniSpec
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-800/80 text-cyan-400 font-semibold tracking-wider uppercase">
                v2.4 Enterprise
              </span>
            </div>
            <span className="text-[11px] text-slate-400 hidden sm:inline">
              252-Col Autonomous Swarm
            </span>
          </div>
        </Link>

        {/* Center: Desktop Navigation */}
        <nav className="hidden lg:flex items-center space-x-1 bg-surface-elevated/80 p-1 rounded-xl border border-surface-border/60">
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 font-bold'
                      : 'text-slate-300 hover:text-white hover:bg-surface'
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                <span>{link.name}</span>
                {link.badge && (
                  <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full border ${link.badgeColor || 'bg-surface border-surface-border text-slate-300'}`}>
                    {link.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Right Utility Actions */}
        <div className="flex items-center space-x-2 sm:space-x-2.5">
          {/* Active Batch Indicator */}
          {activeBatchName && (
            <div className="hidden xl:flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-cyan-950/80 border border-cyan-700/60 text-cyan-300 text-[11px] font-mono">
              <span className="truncate max-w-[120px]" title={activeBatchName}>📄 {activeBatchName}</span>
              <span className="px-1 py-0.2 rounded bg-cyan-900 text-cyan-200 font-bold">{items.length}</span>
              <button 
                onClick={handleResetCatalog}
                className="ml-1 text-slate-400 hover:text-white p-0.5 rounded"
                title="Reset to full catalog"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}

          {/* Action: Upload Feed */}
          <button
            onClick={() => setIsUploadOpen(true)}
            className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-surface hover:bg-surface-elevated border border-surface-border text-xs font-medium text-slate-200 transition-all shadow-sm cursor-pointer"
            title="Batch Ingestion (CSV / Excel)"
          >
            <Upload className="h-3.5 w-3.5 text-slate-400" />
            <span className="hidden sm:inline">Upload Feed</span>
          </button>

          {/* Action: Export Excel */}
          <button
            onClick={handleExportExcel}
            className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-emerald-950/80 hover:bg-emerald-900/90 border border-emerald-700/60 text-emerald-300 font-semibold text-xs transition-all shadow-sm cursor-pointer"
            title={activeBatchName ? `Export ${items.length} uploaded items as multi-sheet Excel (.xlsx)` : "Export formatted multi-sheet Excel (.xlsx)"}
          >
            <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
            <span className="hidden md:inline">{activeBatchName ? "Export Batch (.xlsx)" : "Excel (.xlsx)"}</span>
          </button>

          {/* Action: Export CSV */}
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-semibold text-xs transition-all shadow-md shadow-cyan-500/20 cursor-pointer"
            title={activeBatchName ? `Export ${items.length} uploaded items as 252-column delivery CSV` : "Export 252-column delivery CSV"}
          >
            <Download className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">{activeBatchName ? "Export Batch CSV" : "Export CSV"}</span>
          </button>

          {/* Hamburger Menu Trigger for Mobile */}
          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden flex items-center justify-center h-9 w-9 rounded-lg bg-surface hover:bg-surface-elevated border border-surface-border text-slate-300 transition-colors cursor-pointer"
            aria-label="Toggle Navigation"
          >
            {isMobileMenuOpen ? <X className="h-5 w-5 text-cyan-400" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

      </div>

      {/* Responsive Drawer Menu for Mobile */}
      {isMobileMenuOpen && (
        <div className="lg:hidden border-t border-surface-border bg-slate-950/98 backdrop-blur-2xl px-4 py-4 space-y-2 shadow-2xl animate-in slide-in-from-top-3">
          
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-500 px-2 pb-1">
            Navigation Views
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-mono font-medium transition-all ${
                      isActive
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 shadow-sm'
                        : 'bg-surface/60 text-slate-300 hover:bg-surface border border-surface-border'
                    }`
                  }
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className="h-4 w-4 text-cyan-400" />
                    <span>{link.name}</span>
                  </div>
                  {link.badge && (
                    <span className={`text-[10px] px-2 py-0.5 rounded border font-mono ${link.badgeColor || 'bg-slate-900 text-slate-400 border-slate-800'}`}>
                      {link.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </div>

          {/* Quick Mobile Action Bar */}
          <div className="pt-3 border-t border-surface-border flex items-center justify-between gap-2 text-xs font-mono">
            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                setIsUploadOpen(true);
              }}
              className="flex-1 py-2 px-3 rounded-lg bg-surface border border-surface-border text-slate-300 text-center flex items-center justify-center space-x-1.5"
            >
              <Upload className="h-3.5 w-3.5 text-slate-400" />
              <span>Upload Feed</span>
            </button>

            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                handleExportExcel();
              }}
              className="flex-1 py-2 px-3 rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-300 text-center flex items-center justify-center space-x-1.5"
            >
              <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
              <span>Excel (.xlsx)</span>
            </button>
          </div>

        </div>
      )}
    </header>
  );
}
