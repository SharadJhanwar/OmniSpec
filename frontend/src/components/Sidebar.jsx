import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  LayoutDashboard,
  Table,
  Search,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  GitBranch,
  Image as ImageIcon,
  History,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  Workflow,
  Sparkles,
  Database
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';

export default function Sidebar({ isCollapsed, setIsCollapsed }) {
  const { hitlCount, items } = useCatalog();

  const navigation = [
    {
      name: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
      badge: 'Live',
      badgeColor: 'bg-cyan-950 text-cyan-400 border-cyan-800'
    },
    {
      name: 'Enrichment Sheet',
      path: '/studio',
      icon: Table,
      badge: `${items.length}`,
      badgeColor: 'bg-slate-900 text-slate-400 border-slate-800'
    },
    {
      name: 'Discovery',
      path: '/search',
      icon: Search,
      badge: 'AST'
    },
    {
      name: 'Audit Engine',
      path: '/review',
      icon: ShieldAlert,
      badge: hitlCount > 0 ? `${hitlCount}` : '0',
      badgeColor: hitlCount > 0 ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-emerald-950 text-emerald-400 border-emerald-800'
    },
    {
      name: 'Evidence & Assets',
      path: '/evidence',
      icon: ImageIcon,
      badge: 'Real'
    },
    {
      name: 'Ledger (DBOM)',
      path: '/ledger',
      icon: ShieldCheck,
      badge: 'SHA-256'
    },
    {
      name: 'Intelligence Hub',
      path: '/intelligence',
      icon: Cpu,
      badge: 'Hub'
    }
  ];

  const secondaryNav = [
    { name: 'Run History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'Help & Docs', path: '/help', icon: HelpCircle }
  ];

  return (
    <aside
      className={`relative flex flex-col justify-between border-r border-slate-800/80 bg-slate-950/95 backdrop-blur-xl transition-all duration-300 z-40 select-none ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="flex items-center justify-between px-4 h-16 border-b border-slate-800/80">
          <Link to="/" className="flex items-center space-x-3 overflow-hidden">
            <div className="relative flex items-center justify-center h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-sky-400 text-slate-950 font-black shadow-lg shadow-cyan-500/20 shrink-0">
              <Workflow className="h-5 w-5" />
              <div className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 border-2 border-slate-950 animate-pulse" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col truncate">
                <span className="font-extrabold text-sm tracking-tight text-white font-mono">
                  OmniSpec AI
                </span>
                <span className="text-[10px] text-cyan-400 font-mono">
                  10-Agent Swarm
                </span>
              </div>
            )}
          </Link>

          {/* Collapse Toggle Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:flex p-1 rounded-lg hover:bg-slate-900 text-slate-400 hover:text-slate-200 transition-colors"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Primary Navigation Menu */}
        <div className="px-2.5 py-4 space-y-1">
          {!isCollapsed && (
            <div className="px-2.5 pb-2 text-[10px] font-mono uppercase tracking-wider text-slate-500">
              Intelligence Pipeline
            </div>
          )}

          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all duration-150 group ${
                    isActive
                      ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800 shadow-sm font-semibold'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60 border border-transparent'
                  }`
                }
                title={isCollapsed ? item.name : undefined}
              >
                <div className="flex items-center space-x-3 truncate">
                  <Icon className="h-4 w-4 shrink-0 text-slate-400 group-hover:text-cyan-400 transition-colors" />
                  {!isCollapsed && <span className="truncate">{item.name}</span>}
                </div>

                {!isCollapsed && item.badge && (
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded-full border ${
                      item.badgeColor || 'bg-slate-900 text-slate-400 border-slate-800'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </div>
      </div>

      {/* Secondary / Footer Navigation */}
      <div className="px-2.5 py-4 border-t border-slate-800/80 space-y-1">
        {!isCollapsed && (
          <div className="px-2.5 pb-1 text-[10px] font-mono uppercase tracking-wider text-slate-500">
            System & Support
          </div>
        )}

        {secondaryNav.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-slate-900 text-slate-100'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900/40'
                }`
              }
              title={isCollapsed ? item.name : undefined}
            >
              <Icon className="h-4 w-4 shrink-0 text-slate-500" />
              {!isCollapsed && <span className="truncate">{item.name}</span>}
            </NavLink>
          );
        })}

        {/* Status Pill */}
        {!isCollapsed && (
          <div className="pt-2 px-2">
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Swarm Engine Live</span>
              </span>
              <span className="text-cyan-400">252 Cols</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
