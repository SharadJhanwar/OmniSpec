import React, { useState } from 'react';
import { X, UploadCloud, FileSpreadsheet, Check, AlertCircle } from 'lucide-react';

export default function BatchUploadModal({ isOpen, onClose, onUploadSuccess }) {
  if (!isOpen) return null;

  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true);

    // Simulate batch stream ingestion
    setTimeout(() => {
      setIsProcessing(false);
      onUploadSuccess(file.name);
      onClose();
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md">
      <div className="glass-panel-elevated w-full max-w-lg rounded-2xl shadow-2xl border border-surface-border overflow-hidden p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <FileSpreadsheet className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Catalog CSV Ingestion</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${isDragging ? 'border-cyan-400 bg-cyan-950/20' : 'border-surface-border hover:border-slate-500 bg-surface/50'}`}
          onClick={() => document.getElementById('csvFileInput').click()}
        >
          <input
            id="csvFileInput"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="hidden"
          />
          <UploadCloud className="h-10 w-10 text-cyan-400 mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-200">
            {file ? file.name : "Drag and drop your raw supplier CSV feed here"}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">Supports Unilog 6-column input standard (e.g. Sample-1000_Items.csv)</p>
        </div>

        {/* Action Buttons */}
        <div className="mt-5 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-surface hover:bg-surface-elevated text-xs font-medium text-slate-300"
          >
            Cancel
          </button>
          <button
            onClick={handleProcess}
            disabled={!file || isProcessing}
            className="px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 disabled:opacity-50 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20"
          >
            {isProcessing ? "Processing LangGraph Swarm..." : "Enrich across 252 Columns"}
          </button>
        </div>
      </div>
    </div>
  );
}
