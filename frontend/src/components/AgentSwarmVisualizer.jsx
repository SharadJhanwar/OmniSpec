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
  ShieldCheck, 
  ChevronRight,
  Sparkles
} from 'lucide-react';

const AGENTS = [
  { id: 1, name: 'Ingestion & De-Noising', icon: FileText, desc: 'Placeholder strip & tokenization' },
  { id: 2, name: 'UniCat Entity Resolution', icon: Tag, desc: '27K MFR/Brand fuzzy matching' },
  { id: 3, name: 'Taxonomy & UNSPSC', icon: GitFork, desc: '4-Tier Classpath leaf node tree' },
  { id: 4, name: 'Spec, Dim & UOM Parser', icon: Ruler, desc: '63-fraction decimal conversion' },
  { id: 5, name: 'OEM Sourcing RAG', icon: Globe, desc: 'Official spec sheet & approvals' },
  { id: 6, name: 'Constrained LOV Mapper', icon: Grid3X3, desc: '150-Col structured EAV grid' },
  { id: 7, name: 'Multi-Channel Copy', icon: FileSignature, desc: 'Invoice <=40 & Mobile 60-80 copy' },
  { id: 8, name: 'Digital Asset Synthesizer', icon: ImageIcon, desc: 'Canonical <Brand>_<MPN> naming' },
  { id: 9, name: 'Quality Audit & HITL', icon: ShieldCheck, desc: '12-Point integrity & confidence' },
];

export default function AgentSwarmVisualizer({ activeItem, isEnriching }) {
  return (
    <div className="glass-panel p-5 rounded-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-ping"></div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">LangGraph 9-Agent DAG Swarm Pipeline</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {activeItem ? `Active SKU: ${activeItem.Mfg_Part_Num || 'None'}` : 'Idle • Ready for Batch / Single Enrichment'}
        </span>
      </div>

      {/* 9-Agent Stepper Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-9 gap-2">
        {AGENTS.map((agent, index) => {
          const Icon = agent.icon;
          const isCompleted = !isEnriching || index < 9;

          return (
            <div 
              key={agent.id}
              className="p-3 rounded-lg bg-surface/90 border border-surface-border hover:border-cyan-500/50 transition-all flex flex-col justify-between relative group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-cyan-400 font-bold">A{agent.id}</span>
                  <div className="h-6 w-6 rounded-md bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                </div>
                <p className="text-xs font-semibold text-slate-200 line-clamp-1">{agent.name}</p>
                <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">{agent.desc}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-surface-border/60 flex items-center justify-between">
                <span className="text-[9px] font-mono text-emerald-400">● 100% Valid</span>
                <span className="text-[9px] font-mono text-slate-500">~0.4ms</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
