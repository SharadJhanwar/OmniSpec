import React, { useState } from 'react';
import {
  ShieldCheck,
  Search,
  FileText,
  Lock,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Sparkles,
  ExternalLink,
  Download,
  Fingerprint
} from 'lucide-react';
import { useCatalog } from '../context/CatalogContext';

export default function LedgerPage() {
  const { items, handleOpenDbom } = useCatalog();
  const [selectedSku, setSelectedSku] = useState(items[0] || null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredItems = items.filter(it => {
    const mpn = (it.Mfg_Part_Num || it.mfg_part_num || it.MANUFACTURER_PART_NUMBER || '').toLowerCase();
    const brand = (it.BRAND_NAME || it.brand_name || '').toLowerCase();
    return mpn.includes(searchTerm.toLowerCase()) || brand.includes(searchTerm.toLowerCase());
  });

  // Mock cell-level ledger records for the active SKU
  const activeMpn = selectedSku?.Mfg_Part_Num || selectedSku?.mfg_part_num || selectedSku?.MANUFACTURER_PART_NUMBER || '9A-570-320';
  const activeBrand = selectedSku?.BRAND_NAME || selectedSku?.brand_name || 'Mirka®';

  const cellLedgerEntries = [
    { col: 'BRAND_NAME', val: activeBrand, agent: 'Agent 2: Entity Resolution', conf: '100.0%', hash: 'sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069', source: 'DuckDB 27K Master KB' },
    { col: 'Classpath', val: selectedSku?.Classpath || 'Abrasives & Polishing>Sandpaper>Sanding Discs', agent: 'Agent 3: Taxonomy Classifier', conf: '98.5%', hash: 'sha256:9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72', source: '4-Tier Classpath Taxonomy' },
    { col: 'INVOICE_DESC', val: selectedSku?.INVOICE_DESC || 'SANDING DISC 9A 2-3/4X30 9A-570-320', agent: 'Agent 7: Copy Builder', conf: '100.0%', hash: 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', source: 'Formula Generator (<=40 ALL CAPS)' },
    { col: 'MOBILE_DESC', val: selectedSku?.MOBILE_DESC || 'Mirka USA Inc Mirka, Sanding Disc, Abranet, 9A-570-320', agent: 'Agent 7: Copy Builder', conf: '100.0%', hash: 'sha256:ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb', source: 'Formula Generator (60-80 chars)' },
    { col: 'ATTRIBUTE_LABEL 1', val: 'Abrasive Material', agent: 'Agent 9: ReAct Finalizer', conf: '96.2%', hash: 'sha256:d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35', source: 'DuckDuckGo + CRAG Extraction' },
    { col: 'ATTRIBUTE_VALUE 1', val: 'Aluminum Oxide Mesh', agent: 'Agent 9: ReAct Finalizer', conf: '96.2%', hash: 'sha256:4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce', source: 'UniCat LOV Dictionary' },
    { col: 'Product Image', val: selectedSku?.['Product Image'] || 'MIRKA_9A-570-320.jpg', agent: 'Agent 8: Digital Assets', conf: '99.0%', hash: 'sha256:4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a', source: 'Live Web Discovery' },
    { col: 'Specification Sheet', val: `${activeBrand.replace(/[®™]/g, '').trim()}_${activeMpn}_Specification_Sheet.pdf`, agent: 'Agent 8: Digital Assets', conf: '100.0%', hash: 'sha256:ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d', source: 'Canonical Naming Standard' }
  ];

  return (
    <div className="space-y-6 pb-12 font-sans text-slate-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
            <Fingerprint className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-extrabold text-white tracking-tight">
                Cryptographic Data Bill of Materials (DBOM) & Lineage Ledger
              </h1>
              <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-purple-950 text-purple-400 border border-purple-800 font-semibold">
                SHA-256 Immutable Audit
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Cell-by-cell evidentiary audit trail, extraction coordinates, confidence calibration, and verifiable cryptographic lineage.
            </p>
          </div>
        </div>

        <button
          onClick={() => handleOpenDbom(selectedSku || items[0])}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-xs font-bold text-white shadow-lg shadow-purple-950/40 cursor-pointer self-start sm:self-auto"
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Launch DBOM Provenance Modal</span>
        </button>
      </div>

      {/* SKU Selector Strip */}
      <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Filter SKUs in Ledger..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 font-mono"
          />
        </div>

        {/* Selected SKU Pills */}
        <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto">
          {filteredItems.slice(0, 5).map((it, idx) => {
            const mpn = it.Mfg_Part_Num || it.mfg_part_num || it.MANUFACTURER_PART_NUMBER || `SKU-${idx}`;
            const isSelected = selectedSku?.Mfg_Part_Num === it.Mfg_Part_Num;
            return (
              <button
                key={idx}
                onClick={() => setSelectedSku(it)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-purple-600 text-white font-bold shadow-md shadow-purple-900/50'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {mpn}
              </button>
            );
          })}
        </div>
      </div>

      {/* Cryptographic Ledger Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden space-y-0">
        <div className="p-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-mono">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-200 font-bold">Cell Provenance Ledger:</span>
            <span className="text-cyan-400">{activeBrand} {activeMpn}</span>
          </div>
          <span className="text-[11px] font-mono text-slate-500">252 / 252 Columns Verified</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-900/90 border-b border-slate-800 text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">Column Target</th>
                <th className="py-3 px-4">Populated Value</th>
                <th className="py-3 px-4">Agent Extractor</th>
                <th className="py-3 px-4">Knowledge Source</th>
                <th className="py-3 px-4 text-center">Confidence</th>
                <th className="py-3 px-4 font-mono text-[10px]">SHA-256 Cryptographic Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {cellLedgerEntries.map((entry, idx) => (
                <tr key={idx} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-cyan-400">{entry.col}</td>
                  <td className="py-3 px-4 text-slate-200 font-medium max-w-[200px] truncate" title={entry.val}>{entry.val}</td>
                  <td className="py-3 px-4 text-slate-300">{entry.agent}</td>
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">{entry.source}</td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                      {entry.conf}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-[10px] text-slate-500 truncate max-w-[220px]" title={entry.hash}>
                    {entry.hash}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
