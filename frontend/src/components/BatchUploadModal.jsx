import React, { useState } from 'react';
import { X, UploadCloud, FileSpreadsheet, Check, AlertCircle, Loader2 } from 'lucide-react';

export default function BatchUploadModal({ isOpen, onClose, onUploadSuccess }) {
  if (!isOpen) return null;

  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

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
      setErrorMsg('');
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setErrorMsg('');
    }
  };

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true);
    setErrorMsg('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/v1/enrich/batch-json', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      if (data && data.records && data.records.length > 0) {
        onUploadSuccess(data.records, file.name);
        onClose();
      } else {
        setErrorMsg('No valid rows could be extracted from the uploaded CSV.');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setErrorMsg(`Failed to enrich batch CSV: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="glass-panel-elevated w-full max-w-lg rounded-2xl shadow-2xl border border-cyan-500/40 overflow-hidden p-6 bg-surface text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <FileSpreadsheet className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Catalog Batch Ingestion (CSV / Excel / JSON)</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded text-slate-400 hover:text-white hover:bg-surface-elevated">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${isDragging ? 'border-cyan-400 bg-cyan-950/40' : 'border-surface-border hover:border-cyan-500/60 bg-surface-elevated/60'}`}
          onClick={() => document.getElementById('csvFileInput').click()}
        >
          <input
            id="csvFileInput"
            type="file"
            accept=".csv,.xlsx,.xls,.json"
            onChange={handleFileChange}
            className="hidden"
          />
          <UploadCloud className="h-10 w-10 text-cyan-400 mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-200">
            {file ? file.name : "Drag and drop your raw CSV, Excel (.xlsx, .xls), or JSON feed here"}
          </p>
          <p className="text-[11px] text-slate-400 mt-1">Supports Unilog 6-column input standard (e.g. Sample-1000_Items.csv or test.xlsx)</p>
          {file && (
            <p className="text-[10px] font-mono text-emerald-400 mt-2">
              ✓ Ready for processing ({(file.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        {errorMsg && (
          <div className="mt-3 p-2.5 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-[11px] flex items-center space-x-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-5 flex items-center justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-surface hover:bg-surface-elevated text-xs font-medium text-slate-300"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleProcess}
            disabled={!file || isProcessing}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-400 hover:to-sky-400 disabled:opacity-50 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 cursor-pointer"
          >
            {isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-slate-950" />
                <span>Running LangGraph Swarm...</span>
              </>
            ) : (
              <span>Enrich across 252 Columns</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
