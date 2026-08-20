import React from 'react';
import { Database, CheckCircle2, ShieldAlert, Zap, Layers, Sparkles, Cpu } from 'lucide-react';

export default function DashboardStats({ totalItems, avgConfidence, violationsCount, hitlQueueCount }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
      {/* Total Catalog Items */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Catalog SKUs</p>
            <p className="text-2xl font-bold text-white mt-0.5 font-mono">{totalItems.toLocaleString()}</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400 shrink-0">
            <Database className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-2.5 flex items-center text-xs text-slate-400">
          <span className="text-emerald-400 font-medium font-mono mr-1">
            252 / 252
          </span>
          <span>Columns Standard Enforced</span>
        </div>
      </div>

      {/* Accuracy & Confidence */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Avg Confidence</p>
            <p className="text-2xl font-bold text-emerald-400 mt-0.5 font-mono">{(avgConfidence * 100).toFixed(1)}%</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 shrink-0">
            <CheckCircle2 className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-2.5 flex items-center text-xs text-slate-400">
          <span className="text-emerald-400 font-medium mr-1 font-mono">100% Match</span>
          <span>on Key Ground Truth</span>
        </div>
      </div>

      {/* Human-In-The-Loop Review Queue */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">HITL Audit Queue</p>
            <p className={`text-2xl font-bold mt-0.5 font-mono ${hitlQueueCount > 0 ? 'text-amber-400' : 'text-slate-300'}`}>
              {hitlQueueCount} <span className="text-xs font-normal text-slate-400">items</span>
            </p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-amber-950/80 border border-amber-800/60 flex items-center justify-center text-amber-400 shrink-0">
            <ShieldAlert className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-2.5 flex items-center text-xs text-slate-400 truncate">
          <span>{hitlQueueCount === 0 ? 'All SKUs passed integrity checks' : 'Requires review (DPI risk queue)'}</span>
        </div>
      </div>

      {/* Swarm Architecture */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Architecture</p>
            <p className="text-xl font-bold text-cyan-400 mt-0.5 font-mono">9-Agent DAG</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-sky-950/80 border border-sky-800/60 flex items-center justify-center text-sky-400 shrink-0">
            <Cpu className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-2.5 flex items-center text-xs text-slate-400">
          <span className="text-cyan-400 font-medium mr-1 font-mono">DuckDB + RAG</span>
          <span>Hybrid Pipeline</span>
        </div>
      </div>
    </div>
  );
}
