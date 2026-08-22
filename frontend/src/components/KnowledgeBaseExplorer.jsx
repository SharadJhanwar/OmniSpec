import React, { useState, useEffect } from 'react';
import { Database, Search, Sparkles, BookOpen, ShieldCheck, Scale, Zap, RefreshCw } from 'lucide-react';
import { apiUrl } from '../config/api';

export default function KnowledgeBaseExplorer() {
  const [activeTab, setActiveTab] = useState('BRANDS'); // BRANDS, FRACTIONS, THESAURUS, OVERRIDES
  const [searchTerm, setSearchTerm] = useState('');
  const [brands, setBrands] = useState([]);
  const [fractions, setFractions] = useState([]);
  const [thesaurus, setThesaurus] = useState([]);
  const [overrides, setOverrides] = useState([]);
  const [stats, setStats] = useState({ total_brands: 24, total_fractions: 19, master_uoms_count: 500, lov_rules_count: 161000 });
  const [isLoading, setIsLoading] = useState(false);

  const fetchStatsAndData = () => {
    setIsLoading(true);
    fetch(apiUrl('/api/v1/kb/stats'))
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.log('Stats fallback:', err));

    fetch(apiUrl('/api/v1/kb/brands'))
      .then(res => res.json())
      .then(data => setBrands(data.brands || []))
      .catch(err => console.log('Brands fallback:', err));

    fetch(apiUrl('/api/v1/kb/fractions'))
      .then(res => res.json())
      .then(data => setFractions(data.fractions || []))
      .catch(err => console.log('Fractions fallback:', err));

    fetch(apiUrl('/api/v1/kb/thesaurus'))
      .then(res => res.json())
      .then(data => setThesaurus(data.terms || []))
      .catch(err => console.log('Thesaurus fallback:', err));

    fetch(apiUrl('/api/v1/hitl/overrides'))
      .then(res => res.json())
      .then(data => setOverrides(data.overrides || []))
      .catch(err => console.log('Overrides fallback:', err))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchStatsAndData();
  }, []);

  const handleSearchBrands = (q) => {
    setSearchTerm(q);
    fetch(apiUrl(`/api/v1/kb/brands?q=${encodeURIComponent(q)}`))
      .then(res => res.json())
      .then(data => setBrands(data.brands || []))
      .catch(err => console.log('Brand search error:', err));
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-cyan-500/30 space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-surface-border pb-4">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
            <Database className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">UniCat Knowledge Graph & Rulebook Explorer</h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold">
                DuckDB In-Memory
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">Controlled Vocabularies, Legal Trademarks, Master UOMs & Active Overrides</p>
          </div>
        </div>

        {/* Aggregate Stats Badges */}
        <div className="flex items-center space-x-2 overflow-x-auto w-full sm:w-auto font-mono text-xs">
          <div className="px-2.5 py-1 rounded-lg bg-surface border border-surface-border text-slate-300 shrink-0">
            <span className="text-cyan-400 font-bold">{stats.total_brands || '27,000+'}</span> Brands
          </div>
          <div className="px-2.5 py-1 rounded-lg bg-surface border border-surface-border text-slate-300 shrink-0">
            <span className="text-sky-400 font-bold">161K</span> LOV Rules
          </div>
          <div className="px-2.5 py-1 rounded-lg bg-surface border border-surface-border text-slate-300 shrink-0">
            <span className="text-emerald-400 font-bold">63</span> Exact Fractions
          </div>
          <div className="px-2.5 py-1 rounded-lg bg-surface border border-surface-border text-slate-300 shrink-0">
            <span className="text-amber-400 font-bold">500</span> Master UOMs
          </div>
          <button
            onClick={fetchStatsAndData}
            className="p-1.5 rounded-lg bg-surface hover:bg-surface-elevated text-slate-400 hover:text-cyan-400 transition-colors cursor-pointer"
            title="Refresh Knowledge Base"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Tabs & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Navigation Tabs */}
        <div className="flex items-center space-x-1.5 w-full sm:w-auto overflow-x-auto">
          <button
            onClick={() => setActiveTab('BRANDS')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${activeTab === 'BRANDS' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-surface text-slate-400 hover:text-slate-200'}`}
          >
            UniCat Brands (27K)
          </button>
          <button
            onClick={() => setActiveTab('FRACTIONS')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${activeTab === 'FRACTIONS' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-surface text-slate-400 hover:text-slate-200'}`}
          >
            63 Decimal Fractions
          </button>
          <button
            onClick={() => setActiveTab('THESAURUS')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${activeTab === 'THESAURUS' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-surface text-slate-400 hover:text-slate-200'}`}
          >
            Trade Slang Thesaurus
          </button>
          <button
            onClick={() => setActiveTab('OVERRIDES')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${activeTab === 'OVERRIDES' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-surface text-slate-400 hover:text-slate-200'}`}
          >
            Active Learning ({overrides.length})
          </button>
        </div>

        {/* Live Search Input (for Brands tab) */}
        {activeTab === 'BRANDS' && (
          <div className="relative w-full sm:w-72">
            <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => handleSearchBrands(e.target.value)}
              placeholder="Search canonical brands or aliases..."
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-surface border border-surface-border text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
        )}
      </div>

      {/* Tab Panels */}
      <div className="overflow-x-auto max-h-[360px] rounded-xl border border-surface-border bg-surface-elevated/40">
        {/* TAB 1: BRANDS */}
        {activeTab === 'BRANDS' && (
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="sticky top-0 bg-surface-elevated text-slate-400 text-[10px] uppercase border-b border-surface-border">
              <tr>
                <th className="py-2.5 px-3">Approved Brand Name</th>
                <th className="py-2.5 px-3">Legal Manufacturer Name</th>
                <th className="py-2.5 px-3">Search Alias</th>
                <th className="py-2.5 px-3 text-center">Trademark</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border text-slate-300">
              {brands.map((b, idx) => (
                <tr key={idx} className="hover:bg-surface/60 transition-colors">
                  <td className="py-2 px-3 font-bold text-white">{b.brand_name}</td>
                  <td className="py-2 px-3 text-slate-300">{b.manufacturer_name}</td>
                  <td className="py-2 px-3 text-cyan-400">{b.search_alias}</td>
                  <td className="py-2 px-3 text-center">
                    <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-[10px] font-bold">
                      {b.symbol || '®'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* TAB 2: FRACTIONS */}
        {activeTab === 'FRACTIONS' && (
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="sticky top-0 bg-surface-elevated text-slate-400 text-[10px] uppercase border-b border-surface-border">
              <tr>
                <th className="py-2.5 px-3">Decimal Value</th>
                <th className="py-2.5 px-3">Approved Fraction Form</th>
                <th className="py-2.5 px-3">Trade Inch Standard Example</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border text-slate-300">
              {fractions.map((f, idx) => (
                <tr key={idx} className="hover:bg-surface/60 transition-colors">
                  <td className="py-2 px-3 text-amber-400 font-bold">{f.decimal}</td>
                  <td className="py-2 px-3 font-bold text-white">{f.fraction}</td>
                  <td className="py-2 px-3 text-emerald-400">{f.example}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* TAB 3: THESAURUS */}
        {activeTab === 'THESAURUS' && (
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="sticky top-0 bg-surface-elevated text-slate-400 text-[10px] uppercase border-b border-surface-border">
              <tr>
                <th className="py-2.5 px-3">Contractor / Trade Slang</th>
                <th className="py-2.5 px-3">Canonical Product Classification</th>
                <th className="py-2.5 px-3">Industry Vertical</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border text-slate-300">
              {thesaurus.map((t, idx) => (
                <tr key={idx} className="hover:bg-surface/60 transition-colors">
                  <td className="py-2 px-3 text-rose-400 font-semibold font-mono">"{t.slang}"</td>
                  <td className="py-2 px-3 text-cyan-400 font-bold">{t.canonical}</td>
                  <td className="py-2 px-3 text-slate-400">{t.category}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* TAB 4: OVERRIDES */}
        {activeTab === 'OVERRIDES' && (
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="sticky top-0 bg-surface-elevated text-slate-400 text-[10px] uppercase border-b border-surface-border">
              <tr>
                <th className="py-2.5 px-3">Mfg Part Number</th>
                <th className="py-2.5 px-3">Approved Brand Override</th>
                <th className="py-2.5 px-3">Manufacturer</th>
                <th className="py-2.5 px-3">Reviewer Notes</th>
                <th className="py-2.5 px-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border text-slate-300">
              {overrides.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-slate-500">
                    No manual reviewer overrides recorded yet. Review a SKU in the HITL Studio to register feedback.
                  </td>
                </tr>
              ) : (
                overrides.map((o, idx) => (
                  <tr key={idx} className="hover:bg-surface/60 transition-colors">
                    <td className="py-2 px-3 text-amber-400 font-bold">{o.mpn}</td>
                    <td className="py-2 px-3 text-emerald-400 font-bold">{o.brand_name}</td>
                    <td className="py-2 px-3 text-slate-300">{o.manufacturer_name}</td>
                    <td className="py-2 px-3 text-slate-400">{o.reviewer_notes}</td>
                    <td className="py-2 px-3 text-slate-500 text-[10px]">{o.updated_at}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
