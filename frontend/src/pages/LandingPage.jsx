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
  Workflow
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';

export default function LandingPage() {
  const { items, avgConfidence, hitlCount } = useCatalog();

  const capabilities = [
    {
      icon: Search,
      color: 'from-cyan-500 to-sky-500',
      badgeColor: 'bg-cyan-950 text-cyan-400 border-cyan-800',
      title: 'Parametric Engineering Search',
      badge: 'AST Compiler Engine',
      desc: 'Translates free-form contractor queries like "Dishwasher under 45 dBA stainless steel 120V" into structured DuckDB SQL with side-by-side Qualified vs. Disqualified trade-off explanations.',
      link: '/search'
    },
    {
      icon: GitBranch,
      color: 'from-indigo-500 to-purple-500',
      badgeColor: 'bg-indigo-950 text-indigo-400 border-indigo-800',
      title: 'Product Family & Variant Induction',
      badge: 'Assortment Gap Detector',
      desc: 'Decomposes flat, fragmented SKUs into canonical Parent PDPs with multi-axis variant matrices and identifies missing fractional contractor sizes in distributor assortments.',
      link: '/intelligence'
    },
    {
      icon: ShieldAlert,
      color: 'from-amber-500 to-orange-500',
      badgeColor: 'bg-amber-950 text-amber-400 border-amber-800',
      title: 'Defect Probability Index (DPI)',
      badge: 'Risk-Ranked HITL',
      desc: 'Multivariate defect scoring across brand confidence, trademark marks, character bounds, and 12-rule audit violations for intelligent review queue routing.',
      link: '/review'
    },
    {
      icon: ShieldCheck,
      color: 'from-emerald-500 to-teal-500',
      badgeColor: 'bg-emerald-950 text-emerald-400 border-emerald-800',
      title: 'Cell-Level DBOM & Provenance',
      badge: 'SHA-256 Cryptographic',
      desc: 'Full cell-by-cell data bill of materials across all 252 delivery columns with extraction method, source locator coordinates, and cryptographic lineage hashes.',
      link: '/studio'
    },
    {
      icon: GitCompare,
      color: 'from-purple-500 to-pink-500',
      badgeColor: 'bg-purple-950 text-purple-400 border-purple-800',
      title: 'Compatibility & Substitute Matrix',
      badge: 'Multi-Domain Evaluator',
      desc: 'Evaluates mechanical, electrical, and dimensional compatibility (arbor size, voltage platforms, pipe threads) and discovers direct OEM functional substitutes.',
      link: '/intelligence'
    },
    {
      icon: FileSpreadsheet,
      color: 'from-teal-500 to-emerald-500',
      badgeColor: 'bg-teal-950 text-teal-400 border-teal-800',
      title: 'Excel (.xlsx) & OEM PDF Datasheets',
      badge: '1-Click Deliverables',
      desc: 'Autonomous generation of formatted multi-sheet Excel workbooks with frozen header panes (C2) and 1-page contractor submittal PDF specification sheets.',
      link: '/studio'
    }
  ];

  const agentPillars = [
    { num: '01', name: 'Ingestion & Tokenizer', tag: 'MPN Cleaning' },
    { num: '02', name: 'Entity Resolution', tag: '27K UniCat Brands' },
    { num: '03', name: 'Taxonomy Classifier', tag: '4-Tier Hierarchy' },
    { num: '04', name: 'Spec & UOM Normalizer', tag: 'Fractional Conversion' },
    { num: '05', name: 'OEM Sourcing RAG', tag: 'DuckDB + Vision' },
    { num: '06', name: 'LOV Standardization', tag: '161K Vocabularies' },
    { num: '07', name: 'Copy Synthesis', tag: 'Bounds & Rules' },
    { num: '08', name: 'Digital Asset Engine', tag: 'Image & PDF Locators' },
    { num: '09', name: 'Quality & Audit Gate', tag: '12-Rule Audit' }
  ];

  return (
    <div className="space-y-16 pb-16">
      
      {/* HERO SECTION */}
      <section className="relative pt-6 pb-12 overflow-hidden">
        {/* Glow backdrop */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-cyan-600/15 via-indigo-600/15 to-sky-400/10 blur-[120px] pointer-events-none rounded-full" />

        <div className="relative text-center max-w-4xl mx-auto space-y-6">
          
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-surface border border-cyan-800/60 shadow-lg shadow-cyan-500/10">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs font-mono text-cyan-300 font-semibold">
              9-Agent LangGraph Swarm • 252-Column Master Standard
            </span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-[1.1]">
            AI-Powered Product Intelligence for <br />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
              Industrial Commerce
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Transform messy, fragmented industrial supplier feeds into structured, validated, enriched, traceable, and commerce-ready product intelligence.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-3.5 pt-2">
            <Link
              to="/studio"
              className="px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-bold text-sm shadow-lg shadow-cyan-500/25 flex items-center space-x-2 transition-all hover:scale-[1.02] cursor-pointer"
            >
              <Zap className="h-4 w-4 fill-current" />
              <span>Launch Studio & 252-Grid</span>
              <ArrowRight className="h-4 w-4" />
            </Link>

            <Link
              to="/search"
              className="px-6 py-3.5 rounded-xl bg-surface hover:bg-surface-elevated border border-surface-border text-slate-200 hover:text-white font-semibold text-sm transition-all hover:border-cyan-700/80 flex items-center space-x-2 cursor-pointer shadow-md"
            >
              <Search className="h-4 w-4 text-cyan-400" />
              <span>Parametric Search</span>
            </Link>

            <Link
              to="/intelligence"
              className="px-6 py-3.5 rounded-xl bg-surface hover:bg-surface-elevated border border-surface-border text-slate-200 hover:text-white font-semibold text-sm transition-all hover:border-indigo-700/80 flex items-center space-x-2 cursor-pointer shadow-md"
            >
              <GitBranch className="h-4 w-4 text-indigo-400" />
              <span>Product Families</span>
            </Link>
          </div>
        </div>

        {/* Live Metrics Showcase Banner */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto mt-12">
          <div className="p-4 rounded-2xl bg-surface-elevated border border-surface-border text-center space-y-1 shadow-lg">
            <span className="text-2xl sm:text-3xl font-extrabold text-cyan-400 font-mono">9 Agents</span>
            <p className="text-xs text-slate-400 font-mono">LangGraph DAG Swarm</p>
          </div>
          <div className="p-4 rounded-2xl bg-surface-elevated border border-surface-border text-center space-y-1 shadow-lg">
            <span className="text-2xl sm:text-3xl font-extrabold text-emerald-400 font-mono">252 Columns</span>
            <p className="text-xs text-slate-400 font-mono">Unilog Master Standard</p>
          </div>
          <div className="p-4 rounded-2xl bg-surface-elevated border border-surface-border text-center space-y-1 shadow-lg">
            <span className="text-2xl sm:text-3xl font-extrabold text-purple-400 font-mono">27,000+</span>
            <p className="text-xs text-slate-400 font-mono">UniCat Canonical Brands</p>
          </div>
          <div className="p-4 rounded-2xl bg-surface-elevated border border-surface-border text-center space-y-1 shadow-lg">
            <span className="text-2xl sm:text-3xl font-extrabold text-amber-400 font-mono">161,000+</span>
            <p className="text-xs text-slate-400 font-mono">Standardized LOVs</p>
          </div>
        </div>
      </section>

      {/* 9-AGENT DAG SWARM ARCHITECTURE */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-xs font-mono uppercase tracking-widest text-cyan-400 font-bold">
            LangGraph Execution Pipeline
          </h2>
          <p className="text-2xl font-bold text-white tracking-tight">
            9 Specialized Micro-Agents Working as One
          </p>
          <p className="text-xs text-slate-400">
            Deterministic fast-path execution with DuckDB & RapidFuzz with autonomous multimodal fallback.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-9 gap-2.5 max-w-6xl mx-auto">
          {agentPillars.map((ag) => (
            <div
              key={ag.num}
              className="p-3.5 rounded-xl bg-surface-elevated border border-surface-border text-center space-y-2 hover:border-cyan-500/60 transition-all shadow-md group flex flex-col justify-between"
            >
              <div>
                <div className="h-6 w-6 rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400 font-mono text-[11px] font-bold flex items-center justify-center mx-auto mb-1.5">
                  {ag.num}
                </div>
                <h4 className="text-[11px] font-bold text-white font-mono leading-snug">
                  {ag.name}
                </h4>
              </div>
              <span className="text-[10px] font-mono text-cyan-400/90 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 block truncate">
                {ag.tag}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* CORE CAPABILITIES GRID */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-xs font-mono uppercase tracking-widest text-indigo-400 font-bold">
            State-of-the-Art Intelligence
          </h2>
          <p className="text-2xl font-bold text-white tracking-tight">
            Engineered Specifically for Industrial B2B Commerce
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {capabilities.map((cap, idx) => {
            const Icon = cap.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-surface-elevated border border-surface-border hover:border-slate-700 transition-all flex flex-col justify-between space-y-4 shadow-lg group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="h-10 w-10 rounded-xl bg-slate-900 border border-surface-border flex items-center justify-center text-cyan-400 shadow-md group-hover:scale-105 transition-transform">
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className={`text-[10px] font-mono font-semibold px-2.5 py-0.5 rounded border ${cap.badgeColor}`}>
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

      {/* FOOTER CALL TO ACTION */}
      <section className="p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-surface-border text-center space-y-4 max-w-5xl mx-auto shadow-2xl">
        <h3 className="text-xl sm:text-2xl font-bold text-white">
          Ready to experience the 252-column master standard?
        </h3>
        <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto">
          Ingest raw supplier feeds, run the 9-agent DAG swarm live, inspect cell-level cryptographic DBOM lineage, and download delivery-ready Excel workbooks.
        </p>
        <div className="pt-2">
          <Link
            to="/studio"
            className="inline-flex items-center space-x-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-bold text-sm shadow-xl shadow-cyan-500/20 transition-transform hover:scale-105 cursor-pointer"
          >
            <span>Open Studio Workbench</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

    </div>
  );
}
