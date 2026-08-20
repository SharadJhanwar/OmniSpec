import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Layers,
  ShieldAlert,
  Sparkles,
  GitBranch,
  Upload,
  FileSpreadsheet,
  Download,
  Menu,
  X
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';

export default function Navbar() {
  const { hitlCount, items, handleExportCSV, handleExportExcel, setIsUploadOpen } = useCatalog();
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
      icon: GitBranch
    }
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-surface-border bg-slate-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
        
        {/* Left: Brand Logo & Title (Navigates to Landing Page "/") */}
        <div className="flex items-center space-x-3 sm:space-x-5 shrink-0 min-w-0">
          <NavLink
            to="/"
            className="flex items-center space-x-2.5 group shrink-0"
            title="Go to OmniSpec.AI Landing Page"
          >
            <div className="h-8 w-8 sm:h-9 sm:w-9 rounded-xl bg-gradient-to-tr from-cyan-600 via-sky-500 to-indigo-500 flex items-center justify-center shadow-md shadow-cyan-500/20 group-hover:scale-105 transition-transform shrink-0">
              <Layers className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-1.5">
                <span className="text-base sm:text-lg font-bold tracking-tight text-white group-hover:text-cyan-300 transition-colors truncate">
                  OmniSpec<span className="text-cyan-400">.AI</span>
                </span>
                <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-semibold hidden 2xl:inline">
                  9-Agent Swarm
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block truncate">
                Industrial Product Intelligence
              </p>
            </div>
          </NavLink>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1 shrink-0">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.path}
                  to={link.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold font-mono transition-all shrink-0 ${
                      isActive
                        ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/90 shadow-sm'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-surface'
                    }`
                  }
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{link.name}</span>
                  {link.badge && (
                    <span className={`text-[9px] px-1.5 py-0.2 rounded border font-mono ${link.badgeColor || 'bg-slate-900 text-slate-400 border-slate-800'}`}>
                      {link.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Right: Actions & Mobile Hamburger */}
        <div className="flex items-center space-x-2 shrink-0">
          
          {/* Action: Upload Feed */}
          <button
            onClick={() => setIsUploadOpen(true)}
            className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-surface hover:bg-surface-elevated border border-surface-border text-xs font-medium text-slate-200 transition-all shadow-sm cursor-pointer"
            title="Batch Ingestion (CSV)"
          >
            <Upload className="h-3.5 w-3.5 text-slate-400" />
            <span className="hidden sm:inline">Upload Feed</span>
          </button>

          {/* Action: Export Excel */}
          <button
            onClick={handleExportExcel}
            className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-emerald-950/80 hover:bg-emerald-900/90 border border-emerald-700/60 text-emerald-300 font-semibold text-xs transition-all shadow-sm cursor-pointer"
            title="Export formatted multi-sheet Excel (.xlsx)"
          >
            <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
            <span className="hidden md:inline">Excel (.xlsx)</span>
          </button>

          {/* Action: Export CSV */}
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-semibold text-xs transition-all shadow-md shadow-cyan-500/20 cursor-pointer"
            title="Export 252-column delivery CSV"
          >
            <Download className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Export CSV</span>
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
