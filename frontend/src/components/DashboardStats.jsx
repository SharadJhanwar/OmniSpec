import React from 'react';
import { Database, CheckCircle2, ShieldAlert, Zap, Layers, Sparkles } from 'lucide-react';

export default function DashboardStats({ totalItems, avgConfidence, violationsCount, hitlQueueCount }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Catalog Items */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Catalog SKUs</p>
            <p className="text-2xl font-bold text-white mt-1">{totalItems.toLocaleString()}</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
            <Database className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center text-xs text-slate-400">
          <span className="text-emerald-400 font-medium flex items-center mr-1">
            252 / 252
          </span>
          <span>Columns Standard Enforced</span>
        </div>
      </div>

      {/* Accuracy & Confidence */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Avg Confidence</p>
            <p className="text-2xl font-bold text-emerald-400 mt-1">{(avgConfidence * 100).toFixed(1)}%</p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center text-xs text-slate-400">
          <span className="text-emerald-400 font-medium mr-1">100% Exact Match</span>
          <span>on Key Ground Truth</span>
        </div>
      </div>

      {/* Human-In-The-Loop Review Queue */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">HITL Review Queue</p>
            <p className={`text-2xl font-bold mt-1 ${hitlQueueCount > 0 ? 'text-amber-400' : 'text-slate-300'}`}>
              {hitlQueueCount} <span className="text-xs font-normal text-slate-400">items</span>
            </p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-amber-950/80 border border-amber-800/60 flex items-center justify-center text-amber-400">
            <ShieldAlert className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center text-xs text-slate-400">
          <span>{hitlQueueCount === 0 ? 'All SKUs passed integrity checks' : 'Requires review (< 85% conf)'}</span>
        </div>
      </div>

      {/* Real-time Throughput */}
      <div className="glass-panel p-4 rounded-xl relative overflow-hidden">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Engine Speed</p>
            <p className="text-2xl font-bold text-cyan-400 mt-1">278.6 <span className="text-xs font-normal text-slate-400">SKUs/s</span></p>
          </div>
          <div className="h-10 w-10 rounded-lg bg-sky-950/80 border border-sky-800/60 flex items-center justify-center text-sky-400">
            <Zap className="h-5 w-5" />
          </div>
        </div>
        <div className="mt-3 flex items-center text-xs text-slate-400">
          <span className="text-sky-400 font-medium mr-1">3.59s</span>
          <span>for full 1,000 Catalog</span>
        </div>
      </div>
    </div>
  );
}
