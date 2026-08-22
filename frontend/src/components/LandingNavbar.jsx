import React from 'react';
import { Link } from 'react-router-dom';
import {
  Workflow,
  Activity,
  Table,
  Search,
  Cpu,
  ArrowRight,
  ShieldCheck,
  Zap
} from 'lucide-react';

export default function LandingNavbar() {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl px-4 sm:px-8 flex items-center justify-between sticky top-0 z-50">
      {/* Brand Logo */}
      <Link to="/" className="flex items-center space-x-3 group">
        <div className="relative flex items-center justify-center h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-sky-400 text-slate-950 font-black shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
          <Workflow className="h-5 w-5" />
          <div className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 border-2 border-slate-950 animate-pulse" />
        </div>
        <div className="flex flex-col">
          <span className="font-extrabold text-sm tracking-tight text-white font-mono">
            OmniSpec AI
          </span>
          <span className="text-[10px] text-cyan-400 font-mono">
            10-Agent LangGraph Swarm
          </span>
        </div>
      </Link>

      {/* Navigation Links */}
      <nav className="hidden md:flex items-center space-x-6 text-xs font-medium text-slate-300">
        <Link
          to="/dashboard"
          className="hover:text-cyan-400 flex items-center space-x-1.5 transition-colors"
        >
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          <span>Command Center</span>
        </Link>
        <Link
          to="/studio"
          className="hover:text-cyan-400 flex items-center space-x-1.5 transition-colors"
        >
          <Table className="w-3.5 h-3.5 text-emerald-400" />
          <span>252 Studio</span>
        </Link>
        <Link
          to="/search"
          className="hover:text-cyan-400 flex items-center space-x-1.5 transition-colors"
        >
          <Search className="w-3.5 h-3.5 text-sky-400" />
          <span>Parametric Search</span>
        </Link>
        <Link
          to="/intelligence"
          className="hover:text-cyan-400 flex items-center space-x-1.5 transition-colors"
        >
          <Cpu className="w-3.5 h-3.5 text-purple-400" />
          <span>Intelligence Hub</span>
        </Link>
      </nav>

      {/* CTA Action Button */}
      <div className="flex items-center space-x-3">
        <Link
          to="/dashboard"
          className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-cyan-500/20 cursor-pointer"
        >
          <span>Open Command Center</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </header>
  );
}
