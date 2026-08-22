import React from 'react';
import { 
  FileText, 
  Tag, 
  GitFork, 
  Ruler, 
  Globe, 
  Grid3X3, 
  FileSignature, 
  Image as ImageIcon, 
  Sparkles,
  ShieldCheck, 
  ChevronRight,
  Loader2
} from 'lucide-react';

const AGENTS = [
  { id: 1, name: 'Ingestion & De-Noise', icon: FileText, desc: 'Placeholder strip & tokenization' },
  { id: 2, name: 'Entity Resolution', icon: Tag, desc: '27K UniCat Brand (®, ™) match' },
  { id: 3, name: 'Taxonomy & UNSPSC', icon: GitFork, desc: '4-Tier Classpath leaf assignment' },
  { id: 4, name: 'Spec & UOM Parser', icon: Ruler, desc: '63-fraction decimal converter' },
  { id: 5, name: 'OEM Sourcing RAG', icon: Globe, desc: 'Official URL discovery & CRAG' },
  { id: 6, name: 'Constrained LOV', icon: Grid3X3, desc: '150-Col structured EAV binder' },
  { id: 7, name: 'Multi-Channel Copy', icon: FileSignature, desc: 'Invoice <=40 & Mobile 60-80 copy' },
  { id: 8, name: 'Digital Asset Synthesizer', icon: ImageIcon, desc: 'DuckDuckGo image discovery' },
  { id: 9, name: 'ReAct Attribute Finalizer', icon: Sparkles, desc: '5-Loop dense 50-triple miner' },
  { id: 10, name: 'Quality Audit & HITL', icon: ShieldCheck, desc: '12-Rule audit & 5-pillar conf' },
];

export default function AgentSwarmVisualizer({ activeItem, isEnriching, traces }) {
  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className={`h-2.5 w-2.5 rounded-full ${isEnriching ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'}`}></div>
          <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
            <span>Decoupled 10-Agent Swarm Orchestrator</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono lowercase">
              react cognitive dag
            </span>
          </h3>
        </div>
        <div className="flex items-center space-x-3 text-xs font-mono">
          {isEnriching ? (
            <span className="text-amber-400 flex items-center">
              <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
              <span>Agents executing in parallel DAG...</span>
            </span>
          ) : (
            <span className="text-slate-400">
              Active SKU: <span className="text-cyan-400 font-semibold">{activeItem ? (activeItem.Mfg_Part_Num || activeItem.mfg_part_num || activeItem.MANUFACTURER_PART_NUMBER || 'None') : 'None'}</span>
            </span>
          )}
        </div>
      </div>

      {/* 10-Agent Stepper Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-10 gap-2.5">
        {AGENTS.map((agent, index) => {
          const Icon = agent.icon;
          const matchingTrace = traces && traces[index];

          return (
            <div 
              key={agent.id}
              className={`p-3 rounded-xl border transition-all flex flex-col justify-between relative group ${
                isEnriching 
                  ? 'bg-cyan-950/30 border-cyan-500/50 animate-pulse' 
                  : agent.id === 9 
                    ? 'bg-indigo-950/40 border-indigo-700/60 hover:border-indigo-400'
                    : 'bg-slate-900/80 border-slate-800 hover:border-cyan-500/50'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-cyan-400 font-extrabold">A{agent.id}</span>
                  <div className={`h-6 w-6 rounded-md flex items-center justify-center ${agent.id === 9 ? 'bg-indigo-900/80 text-indigo-300 border border-indigo-700' : 'bg-slate-800/80 text-cyan-400 border border-slate-700'}`}>
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                </div>
                <p className="text-xs font-semibold text-slate-200 line-clamp-1" title={agent.name}>{agent.name}</p>
                <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">{agent.desc}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-[9px] font-mono text-emerald-400">● Live</span>
                <span className="text-[9px] font-mono text-slate-400">
                  {matchingTrace ? `${matchingTrace.execution_time_ms}ms` : '~0.5ms'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
