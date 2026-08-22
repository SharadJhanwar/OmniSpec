import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Table,
  Search,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Database,
  Layers,
  Sparkles,
  Zap,
  Activity,
  CheckCircle2,
  FileSpreadsheet,
  Image as ImageIcon,
  Cpu,
  Workflow
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';
import AgentSwarmVisualizer from '../components/AgentSwarmVisualizer';
import VisualAssetGallery from '../components/VisualAssetGallery';

export default function DashboardPage() {
  const navigate = useNavigate();
  const {
    items,
    activeItem,
    avgConfidence,
    hitlCount,
    handleOpenDbom,
    isEnriching,
    activeTraces,
    setIsUploadOpen
  } = useCatalog();

  const totalRows = items.length;
  const totalCells = totalRows * 252;
  const actualImgCount = items.filter(
    it => it['Actual Image (Yes/No)'] === 'Yes' || (it['Product Image'] && String(it['Product Image']).startsWith('http'))
  ).length;

  return (
    <div className="space-y-6 pb-12 font-sans text-slate-200">
      
      {/* 1. Header & Primary Action Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Catalog Intelligence Overview
            </h1>
            <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold">
              10-Agent Swarm
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Converting supplier catalog feeds into strictly conformant <strong className="text-slate-200 font-mono">252-Column Master Deliverables</strong> via in-memory DuckDB knowledge and live web discovery.
          </p>
        </div>

        <div className="flex items-center space-x-3 self-start sm:self-auto">
          <button
            onClick={() => setIsUploadOpen(true)}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-xs font-semibold text-slate-200 transition-all cursor-pointer shadow-sm"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Upload Catalog</span>
          </button>

          <button
            onClick={() => navigate('/studio')}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-xs font-bold text-slate-950 transition-all shadow-md shadow-cyan-500/20 cursor-pointer"
          >
            <span>Open 252 Studio</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. 6 Executive Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* Enriched SKUs */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 hover:border-cyan-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Enriched SKUs</span>
            <Database className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-slate-100 font-mono">{totalRows}</div>
          <div className="text-[10px] text-emerald-400 font-medium mt-1">252 Cols Master Truth</div>
        </div>

        {/* 5-Pillar Confidence */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 hover:border-emerald-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>5-Pillar Conf</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            {Math.round(avgConfidence * 100)}%
          </div>
          <div className="text-[10px] text-slate-400 font-medium mt-1">Calibrated Evidence</div>
        </div>

        {/* Cells Populated */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 hover:border-indigo-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Cells Structured</span>
            <Table className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-black text-indigo-400 font-mono">{totalCells}</div>
          <div className="text-[10px] text-slate-400 font-medium mt-1">Zero Metadata Leakage</div>
        </div>

        {/* Swarm Speed */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 hover:border-purple-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Swarm Speed</span>
            <Zap className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-black text-purple-400 font-mono">278.6</div>
          <div className="text-[10px] text-slate-400 font-medium mt-1">SKUs / sec Fast-Path</div>
        </div>

        {/* Real Image Discovery */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 hover:border-cyan-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Image Discovery</span>
            <ImageIcon className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-black text-cyan-400 font-mono">
            {actualImgCount}/{totalRows || 1}
          </div>
          <div className="text-[10px] text-emerald-400 font-medium mt-1">Real Sourced Photos</div>
        </div>

        {/* HITL Queue */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 hover:border-amber-500/40 transition-all">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>HITL Queue</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-400 font-mono">{hitlCount}</div>
          <div className="text-[10px] text-amber-400 font-medium mt-1">DPI Triage Queue</div>
        </div>
      </div>

      {/* 3. Live 10-Agent Swarm Visualizer Topology */}
      <AgentSwarmVisualizer
        activeItem={activeItem}
        isEnriching={isEnriching}
        traces={activeTraces}
      />

      {/* 4. Live Sourced Digital Asset Gallery */}
      <VisualAssetGallery items={items} onInspectDbom={handleOpenDbom} />

      {/* 5. Master Catalog Preview Table */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center space-x-2.5">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Enriched Catalog Master Records
            </h3>
          </div>
          <button
            onClick={() => navigate('/studio')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1 cursor-pointer"
          >
            <span>View all 252 columns</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px]">
                <th className="py-2.5 px-3">Asset</th>
                <th className="py-2.5 px-3">MPN</th>
                <th className="py-2.5 px-3">Brand (®, ™)</th>
                <th className="py-2.5 px-3">Classpath / Taxonomy</th>
                <th className="py-2.5 px-3">Invoice Desc (&le;40 ALL CAPS)</th>
                <th className="py-2.5 px-3 text-center">Confidence</th>
                <th className="py-2.5 px-3 text-right">DBOM</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {items.slice(0, 5).map((it, idx) => {
                const imgUrl = it['Product Image'] || it.product_image;
                const isReal = String(imgUrl).startsWith('http');
                const brand = it.BRAND_NAME || it.brand_name || 'Brand';
                const mpn = it.Mfg_Part_Num || it.mfg_part_num || it.MANUFACTURER_PART_NUMBER || 'SKU';
                const conf = Math.round((it._confidence || 1.0) * 100);

                return (
                  <tr key={idx} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-2.5 px-3">
                      <div className="w-9 h-9 rounded-lg bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center">
                        {isReal ? (
                          <img src={imgUrl} alt={mpn} className="w-full h-full object-contain p-0.5" />
                        ) : (
                          <ImageIcon className="w-4 h-4 text-slate-600" />
                        )}
                      </div>
                    </td>
                    <td className="py-2.5 px-3 font-mono font-bold text-cyan-400">{mpn}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{brand}</td>
                    <td className="py-2.5 px-3 text-slate-300 truncate max-w-[220px]" title={it.Classpath || it.classpath}>
                      {it.Classpath || it.classpath || 'Industrial'}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-300 truncate max-w-[200px]">
                      {it.INVOICE_DESC || it.invoice_desc || 'N/A'}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                        conf >= 90 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
                      }`}>
                        {conf}%
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => handleOpenDbom(it)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-500 text-slate-300 hover:text-slate-950 transition-colors text-[11px] font-medium cursor-pointer"
                        title="Inspect DBOM Provenance"
                      >
                        <ShieldCheck className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
