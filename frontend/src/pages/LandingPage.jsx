import React from 'react';
import { Link } from 'react-router-dom';
import {
  Layers,
  Sparkles,
  Zap,
  ShieldCheck,
  Cpu,
  Search,
  GitBranch,
  FileSpreadsheet,
  FileText,
  CheckCircle2,
  ArrowRight,
  Database,
  Sliders,
  ShieldAlert,
  GitCompare,
  Terminal,
  Activity,
  Boxes,
  Workflow,
  Lock,
  Image as ImageIcon,
  Compass,
  Play
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';

export default function LandingPage() {
  const { items, avgConfidence, hitlCount, setIsUploadOpen } = useCatalog();

  const capabilities = [
    {
      icon: Search,
      color: 'from-cyan-500 to-sky-500',
      badgeColor: 'bg-cyan-950 text-cyan-400 border-cyan-800',
      title: 'Parametric Engineering Search',
      badge: 'AST Compiler Engine',
      desc: 'Translates natural language contractor queries like "Dishwasher under 48 dBA stainless steel 120V" into physical constraint ASTs and executes sub-2ms DuckDB SQL queries with Qualified vs. Disqualified trade-off explainers.',
      link: '/search'
    },
    {
      icon: GitBranch,
      color: 'from-indigo-500 to-purple-500',
      badgeColor: 'bg-indigo-950 text-indigo-400 border-indigo-800',
      title: 'Product Family & Variant Induction',
      badge: 'Assortment Gap Detector',
      desc: 'Decomposes flat, fragmented SKUs into canonical Parent PDPs with multi-axis variant matrices and flags missing fractional contractor sizes in distributor assortments.',
      link: '/intelligence'
    },
    {
      icon: ShieldAlert,
      color: 'from-amber-500 to-orange-500',
      badgeColor: 'bg-amber-950 text-amber-400 border-amber-800',
      title: 'Defect Probability Index (DPI)',
      badge: 'Risk-Ranked HITL Gate',
      desc: 'Multivariate defect scoring across brand confidence, trademark marks, character bounds, and 12-rule deterministic audits for intelligent review queue routing.',
      link: '/review'
    },
    {
      icon: ShieldCheck,
      color: 'from-emerald-500 to-teal-500',
      badgeColor: 'bg-emerald-950 text-emerald-400 border-emerald-800',
      title: 'Cell-Level DBOM & Cryptographic Lineage',
      badge: 'SHA-256 Verified Ledger',
      desc: 'Full cell-by-cell data bill of materials across all 252 delivery columns with agent attribution, source locator coordinates, confidence calibration, and immutable hashes.',
      link: '/ledger'
    },
    {
      icon: GitCompare,
      color: 'from-purple-500 to-pink-500',
      badgeColor: 'bg-purple-950 text-purple-400 border-purple-800',
      title: 'Compatibility & Cross-Brand Substitute Matrix',
      badge: 'Multi-Domain Engine',
      desc: 'Evaluates mechanical, electrical, and dimensional constraints (arbor size matching, battery voltage platforms, NPT threads) and discovers direct OEM functional alternatives.',
      link: '/intelligence'
    },
    {
      icon: FileSpreadsheet,
      color: 'from-teal-500 to-emerald-500',
      badgeColor: 'bg-teal-950 text-teal-400 border-teal-800',
      title: 'Excel (.xlsx) & PDF Submittal Generator',
      badge: '1-Click Deliverables',
      desc: 'Autonomous generation of formatted multi-sheet Excel workbooks with frozen header panes (C2) and 1-page contractor-ready submittal PDF specification cut-sheets.',
      link: '/studio'
    }
  ];

  const agentNodes = [
    { num: '01', name: 'Ingestion & Tokenizer', tag: 'MPN Cleaning' },
    { num: '02', name: 'Entity Resolution', tag: '27K UniCat Brands' },
    { num: '03', name: 'Taxonomy Classifier', tag: '4-Tier Classpath' },
    { num: '04', name: 'Spec & UOM Normalizer', tag: '63-Fraction Conversion' },
    { num: '05', name: 'OEM Sourcing RAG', tag: 'DuckDB + Vision' },
    { num: '06', name: 'LOV Standardization', tag: '161K Vocabularies' },
    { num: '07', name: 'Copy Synthesis', tag: 'Rules & Bounds' },
    { num: '08', name: 'Digital Asset Engine', tag: 'Real Photo & PDF Sourcing' },
    { num: '09', name: 'ReAct Attribute Finalizer', tag: '50-Slot Triples & ANSI' },
    { num: '10', name: 'Quality & Audit Gate', tag: '12-Rule Audit & DBOM' }
  ];

  return (
    <div className="space-y-16 pb-16 font-sans text-slate-200">
      
      {/* 1. HERO SECTION */}
      <section className="relative pt-6 pb-10 overflow-hidden">
        {/* Glow backdrop blur */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-tr from-cyan-600/15 via-indigo-600/15 to-sky-400/10 blur-[130px] pointer-events-none rounded-full" />

        <div className="relative text-center max-w-4xl mx-auto space-y-6">
          
          {/* Top Operational Badge */}
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-slate-900/90 border border-cyan-800/80 shadow-lg shadow-cyan-500/10">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs font-mono text-cyan-300 font-semibold tracking-wide">
              10-Agent LangGraph Swarm • 252-Column Master Standard
            </span>
          </div>

          {/* Main Hero Title */}
          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-[1.12]">
            Autonomous Industrial Catalog Intelligence & <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
              252-Column Master Truth
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Transform messy, fragmented supplier feeds into structured, validated, enriched, traceable, and commerce-ready product master records with zero metadata leakage.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-3.5 pt-2">
            <Link
              to="/dashboard"
              className="px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-extrabold text-sm shadow-xl shadow-cyan-500/25 flex items-center space-x-2 transition-all hover:scale-[1.02] cursor-pointer"
            >
              <Activity className="h-4 w-4 fill-current" />
              <span>Command Center Dashboard</span>
              <ArrowRight className="h-4 w-4" />
            </Link>

            <Link
              to="/studio"
              className="px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-200 hover:text-white font-semibold text-sm transition-all hover:border-cyan-700/80 flex items-center space-x-2 cursor-pointer shadow-md"
            >
              <Database className="h-4 w-4 text-cyan-400" />
              <span>252 Studio & Grid</span>
            </Link>
          </div>
        </div>

        {/* Live Metrics Showcase Ticker */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto mt-12">
          <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 text-center space-y-1 shadow-lg">
            <span className="text-3xl sm:text-4xl font-extrabold text-cyan-400 font-mono">10 Nodes</span>
            <p className="text-xs text-slate-400 font-mono">LangGraph Agent Swarm</p>
          </div>
          <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 text-center space-y-1 shadow-lg">
            <span className="text-3xl sm:text-4xl font-extrabold text-emerald-400 font-mono">252 Cols</span>
            <p className="text-xs text-slate-400 font-mono">Standard Delivery Schema</p>
          </div>
          <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 text-center space-y-1 shadow-lg">
            <span className="text-3xl sm:text-4xl font-extrabold text-purple-400 font-mono">27,000+</span>
            <p className="text-xs text-slate-400 font-mono">UniCat Registered Brands</p>
          </div>
          <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 text-center space-y-1 shadow-lg">
            <span className="text-3xl sm:text-4xl font-extrabold text-amber-400 font-mono">161,000+</span>
            <p className="text-xs text-slate-400 font-mono">Standardized LOVs</p>
          </div>
        </div>
      </section>

      {/* 2. 10-AGENT SWARM ARCHITECTURE TOPOLOGY */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-xs font-mono uppercase tracking-widest text-cyan-400 font-bold">
            LangGraph Swarm Topology
          </h2>
          <p className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            10 Specialized Micro-Agents Working in Lockstep
          </p>
          <p className="text-xs text-slate-400">
            Deterministic sub-millisecond fast path backed by DuckDB & RapidFuzz with autonomous multimodal vision and ReAct fallback.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2.5 max-w-[1700px] mx-auto">
          {agentNodes.map((ag) => (
            <div
              key={ag.num}
              className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800/80 text-center space-y-2 hover:border-cyan-500/60 transition-all shadow-md group flex flex-col justify-between"
            >
              <div>
                <div className="h-6 w-6 rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400 font-mono text-[11px] font-bold flex items-center justify-center mx-auto mb-1.5">
                  {ag.num}
                </div>
                <h4 className="text-[11px] font-bold text-white font-mono leading-snug">
                  {ag.name}
                </h4>
              </div>
              <span className="text-[9px] font-mono text-cyan-400 px-1 py-0.5 rounded bg-slate-900 border border-slate-800 block truncate">
                {ag.tag}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* 3. CORE CAPABILITIES GRID */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-xs font-mono uppercase tracking-widest text-indigo-400 font-bold">
            State-of-the-Art Enterprise Intelligence
          </h2>
          <p className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Engineered Specifically for Industrial B2B Commerce
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {capabilities.map((cap, idx) => {
            const Icon = cap.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-slate-950/80 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4 shadow-lg group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="h-10 w-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 shadow-md group-hover:scale-105 transition-transform">
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className={`text-[10px] font-mono font-semibold px-2.5 py-0.5 rounded-full border ${cap.badgeColor}`}>
                      {cap.badge}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white">
                    {cap.title}
                  </h3>

                  <p className="text-xs text-slate-400 leading-relaxed">
                    {cap.desc}
                  </p>
                </div>

                <Link
                  to={cap.link}
                  className="pt-2 flex items-center space-x-1.5 text-xs font-mono font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  <span>Explore Feature</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            );
          })}
        </div>
      </section>

      {/* 4. FOOTER CALL TO ACTION */}
      <section className="p-8 sm:p-10 rounded-3xl bg-gradient-to-r from-slate-950 via-indigo-950/40 to-slate-950 border border-slate-800 text-center space-y-4 max-w-5xl mx-auto shadow-2xl">
        <h3 className="text-2xl sm:text-3xl font-extrabold text-white">
          Ready to experience the 252-column master standard?
        </h3>
        <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto">
          Ingest raw supplier feeds, run the 10-agent DAG swarm live, inspect cell-level cryptographic DBOM lineage, and download delivery-ready Excel workbooks.
        </p>
        <div className="pt-3 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/dashboard"
            className="inline-flex items-center space-x-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-extrabold text-sm shadow-xl shadow-cyan-500/20 transition-transform hover:scale-105 cursor-pointer"
          >
            <span>Open Command Center</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            to="/studio"
            className="inline-flex items-center space-x-2 px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-white font-semibold text-sm transition-transform hover:scale-105 cursor-pointer"
          >
            <Database className="h-4 w-4 text-cyan-400" />
            <span>Open 252 Studio</span>
          </Link>
        </div>
      </section>

    </div>
  );
}
