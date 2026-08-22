import React, { useState, useEffect } from 'react';
import { Search, Sliders, CheckCircle2, AlertTriangle, Sparkles, Code, Zap } from 'lucide-react';
import { apiUrl } from '../config/api';

const SAMPLE_QUERIES = [
  {
    label: "Quiet Stainless Dishwasher (< 45 dBA)",
    query: "Dishwasher under 45 dBA stainless steel 120V 15A"
  },
  {
    label: "Cordless Brushless Miter Saw (< 35 lbs)",
    query: "DEWALT Cordless sliding miter saw with brushless motor under 35 lbs"
  },
  {
    label: "4-1/2 in Cut-Off Disc (> 10,000 RPM, 7/8 Arbor)",
    query: "4-1/2 in metal cut off disc with 7/8 in arbor rated over 10000 RPM"
  },
  {
    label: "Warm White LED Bulb (2700K, E26)",
    query: "9.5W A19 LED light bulb 2700K medium E26 base"
  },
  {
    label: "Brass Coupler (150# NPT)",
    query: "3/8 in brass pipe coupling 150# NPT female"
  }
];

export default function SearchPage() {
  const [query, setQuery] = useState(SAMPLE_QUERIES[0].query);
  const [enableLlm, setEnableLlm] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchData, setSearchData] = useState(null);

  const handleExecuteSearch = async (targetQuery = query) => {
    if (!targetQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await fetch(apiUrl('/api/v1/search/parametric'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: targetQuery, enable_llm: enableLlm })
      });
      const json = await res.json();
      if (json.success) {
        setSearchData(json.data);
      }
    } catch (err) {
      console.error('Error executing parametric search:', err);
    } finally {
      setIsSearching(false);
    }
  };

  useEffect(() => {
    handleExecuteSearch();
  }, [enableLlm]);

  const ast = searchData?.ast;
  const qualified = searchData?.qualified_matches || [];
  const tradeoffs = searchData?.disqualified_tradeoffs || [];

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="p-6 rounded-2xl bg-surface-elevated border border-surface-border shadow-xl space-y-4">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400 shadow-md">
            <Sliders className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-lg font-bold text-white tracking-tight">Parametric Engineering Constraint Search</h1>
              <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-semibold">
                AST Query Compiler & SQL Engine
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Natural Language → Physical Constraint AST Compiler & Multi-Variable Disqualification Explainer
            </p>
          </div>
        </div>

        {/* Search Input Bar */}
        <div className="space-y-3 pt-2">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleExecuteSearch()}
                placeholder="e.g. Dishwasher under 45 dBA stainless steel 120V 15A..."
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-surface border border-surface-border text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <button
              onClick={() => handleExecuteSearch()}
              disabled={isSearching}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 cursor-pointer flex items-center justify-center space-x-2 transition-all shrink-0"
            >
              {isSearching ? <Zap className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              <span>Compile & Search</span>
            </button>
          </div>

          {/* Quick Presets */}
          <div className="flex items-center space-x-2 overflow-x-auto pt-1">
            <span className="text-[11px] font-mono text-slate-500 shrink-0">Sample Contractor Queries:</span>
            {SAMPLE_QUERIES.map((sq, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(sq.query);
                  handleExecuteSearch(sq.query);
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-mono bg-surface hover:bg-surface-elevated text-slate-300 hover:text-cyan-300 border border-surface-border transition-colors shrink-0 cursor-pointer"
              >
                {sq.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Live AST Visualizer Banner */}
      {ast && (
        <div className="p-4 rounded-2xl bg-surface-elevated border border-surface-border space-y-2.5 shadow-md">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <Code className="h-4 w-4 text-cyan-400" />
              <span className="font-bold text-white font-mono">Compiled Parametric AST & DuckDB Filter</span>
            </div>
            <div className="flex items-center space-x-2 font-mono text-[11px]">
              <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                {ast.parser_used === 'DETERMINISTIC_REGEX' ? '⚡ Deterministic AST Fast-Path' : '⚡ Generative Fallback'}
              </span>
              <span className="text-slate-400">Total Scanned: {searchData?.total_candidates_scanned} SKUs</span>
            </div>
          </div>

          {/* AST Constraint Chips */}
          <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-mono">
            {ast.category_intent && (
              <span className="px-2.5 py-1 rounded-lg bg-purple-950 text-purple-300 border border-purple-800">
                Intent: {ast.category_intent.split('>').slice(-2).join(' > ')}
              </span>
            )}
            {ast.numerical_constraints.map((num, i) => (
              <span key={i} className="px-2.5 py-1 rounded-lg bg-cyan-950 text-cyan-300 border border-cyan-800">
                {num.field} {num.operator} {num.value} {num.unit}
              </span>
            ))}
            {ast.categorical_constraints.map((cat, i) => (
              <span key={i} className="px-2.5 py-1 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-800">
                {cat.field}: {cat.value}
              </span>
            ))}
          </div>

          {/* Compiled SQL */}
          <div className="text-[11px] font-mono text-slate-400 truncate bg-slate-950 p-2 rounded-lg border border-slate-800">
            <span className="text-cyan-500 font-semibold">DuckDB SQL:</span> {ast.compiled_sql}
          </div>
        </div>
      )}

      {/* Results Layout: 2-Pane Split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Pane 1: Qualified Matches (100% Alignment) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                Qualified Engineering Matches ({qualified.length})
              </h3>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950 px-2.5 py-0.5 rounded border border-emerald-800">
              100% Satisfied
            </span>
          </div>

          {qualified.length > 0 ? (
            qualified.map((item, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-surface-elevated border border-surface-border hover:border-emerald-700/80 transition-all space-y-2.5 shadow-md">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-cyan-300 font-mono">{item.brand_name} {item.mpn}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                    Score: {Math.round(item.alignment_score * 100)}% Match
                  </span>
                </div>

                <h4 className="text-xs font-semibold text-white">
                  {item.short_desc}
                </h4>

                <div className="space-y-1 pt-1">
                  {item.matched_constraints.map((m, i) => (
                    <div key={i} className="text-[11px] text-emerald-300 font-mono flex items-center space-x-1">
                      <span>{m}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 rounded-xl bg-surface-elevated border border-surface-border text-center text-xs text-slate-500 font-mono">
              No catalog items met 100% of the requested physical and electrical constraints.
              <br />See near-miss trade-off alternatives on the right ➔
            </div>
          )}
        </div>

        {/* Pane 2: Disqualified Candidates & Trade-Off Explanations */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-surface-border">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                Disqualified Candidates & Trade-Offs ({tradeoffs.length})
              </h3>
            </div>
            <span className="text-[10px] font-mono text-amber-400 bg-amber-950 px-2.5 py-0.5 rounded border border-amber-800">
              Delta Explanations
            </span>
          </div>

          {tradeoffs.length > 0 ? (
            tradeoffs.map((item, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-surface-elevated border border-surface-border hover:border-amber-700/80 transition-all space-y-2.5 shadow-md">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-300 font-mono">{item.brand_name} {item.mpn}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                    Partial: {Math.round(item.alignment_score * 100)}%
                  </span>
                </div>

                <h4 className="text-xs font-semibold text-slate-300">
                  {item.short_desc}
                </h4>

                <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-900/40 text-[11px] font-mono space-y-1">
                  {item.disqualification_reasons.map((r, i) => (
                    <div key={i} className="text-rose-300">
                      {r}
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 rounded-xl bg-surface-elevated border border-surface-border text-center text-xs text-slate-500 font-mono">
              No disqualified partial trade-offs to show.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
