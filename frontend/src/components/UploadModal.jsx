import React, { useState, useRef } from 'react';
import { Upload, X, FileText, CheckCircle2, AlertCircle, Sparkles, Loader2, FolderArchive, Trash2, Plus } from 'lucide-react';

export default function UploadModal({
  isOpen,
  onClose,
  onUploadFiles,
  onLoadSample,
  isIndexing,
  activeVaultName = 'Primary Vault',
}) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const dropped = Array.from(e.dataTransfer.files || []);
    if (dropped.length > 0) {
      setSelectedFiles((prev) => [...prev, ...dropped]);
    }
  };

  const handleFileSelect = (e) => {
    const chosen = Array.from(e.target.files || []);
    if (chosen.length > 0) {
      setSelectedFiles((prev) => [...prev, ...chosen]);
    }
  };

  const handleRemoveFile = (indexToRemove) => {
    setSelectedFiles((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleExecuteUpload = () => {
    if (selectedFiles.length === 0) return;
    onUploadFiles(selectedFiles);
    setSelectedFiles([]);
  };

  const totalSizeKb = selectedFiles.reduce((acc, f) => acc + f.size / 1024, 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs select-none animate-fade-in">
      <div className="w-full max-w-lg rounded-lg bg-surface border border-border p-6 shadow-elevated space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-sage-light border border-sage/30 flex items-center justify-center text-sage">
              <Upload className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-charcoal font-sans">
                  Upload Vault or Documents
                </h3>
                <span className="font-mono text-[10px] text-sage bg-sage-light px-1.5 py-0.2 rounded border border-sage/30 font-semibold">
                  {activeVaultName}
                </span>
              </div>
              <p className="text-[11px] text-charcoal-muted">
                Indexing directly into workspace "{activeVaultName}"
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-surface-hover text-charcoal-muted hover:text-charcoal transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`p-6 border-2 border-dashed rounded-lg text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-2 ${
            isDragOver
              ? 'border-sage bg-sage-light/30'
              : 'border-border hover:border-zinc-400 bg-canvas-warm'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".zip,.pdf,.md,.markdown,.txt"
            onChange={handleFileSelect}
            className="hidden"
          />

          <div className="w-9 h-9 rounded-full bg-surface border border-border flex items-center justify-center text-sage shadow-subtle">
            {isIndexing ? (
              <Loader2 className="w-4 h-4 animate-spin text-sage" />
            ) : (
              <FolderArchive className="w-4 h-4 text-sage" />
            )}
          </div>

          <div>
            <div className="text-xs font-semibold text-charcoal">
              {isIndexing ? 'Indexing...' : 'Select or drag & drop multiple files'}
            </div>
            <div className="text-[10.5px] text-charcoal-muted font-mono mt-0.5">
              Hold Shift or ⌘ to select multiple PDFs, Markdown notes, or ZIPs
            </div>
          </div>
        </div>

        {/* Selected Files Queue */}
        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-charcoal-muted">
              <span>Selected Queue ({selectedFiles.length} files · {totalSizeKb < 1024 ? `${round(totalSizeKb, 1)} KB` : `${round(totalSizeKb/1024, 1)} MB`})</span>
              <button
                onClick={() => setSelectedFiles([])}
                className="text-rose-600 hover:underline"
              >
                Clear all
              </button>
            </div>

            <div className="max-h-36 overflow-y-auto custom-scrollbar space-y-1.5 p-1 rounded bg-canvas-subtle border border-border">
              {selectedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-1.5 rounded bg-surface border border-border text-xs font-mono"
                >
                  <div className="flex items-center gap-2 truncate min-w-0">
                    <FileText className="w-3.5 h-3.5 text-sage shrink-0" />
                    <span className="truncate text-charcoal font-medium">{file.name}</span>
                    <span className="text-[10px] text-charcoal-muted shrink-0">
                      ({round(file.size / 1024, 1)} KB)
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveFile(idx);
                    }}
                    className="p-1 text-charcoal-muted hover:text-rose-600 transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={handleExecuteUpload}
              disabled={isIndexing}
              className="w-full py-2.5 px-4 rounded-md bg-sage hover:bg-sage-hover text-white text-xs font-semibold font-sans flex items-center justify-center gap-2 transition-all shadow-sm active:scale-[0.98]"
            >
              {isIndexing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing {selectedFiles.length} Document(s)...</span>
                </>
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload & Index {selectedFiles.length} File(s)</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* 1-Click Sample Vault Option */}
        {selectedFiles.length === 0 && (
          <>
            <div className="relative flex py-1 items-center">
              <div className="flex-grow border-t border-border"></div>
              <span className="flex-shrink mx-3 text-[10px] font-mono uppercase tracking-wider text-charcoal-muted">
                OR EXPLORE WITH DEMO VAULT
              </span>
              <div className="flex-grow border-t border-border"></div>
            </div>

            <button
              onClick={() => {
                onLoadSample();
                onClose();
              }}
              disabled={isIndexing}
              className="w-full py-2 px-4 rounded-md bg-canvas-subtle hover:bg-surface-hover border border-border text-xs font-semibold text-charcoal flex items-center justify-center gap-2 transition-all shadow-subtle active:scale-[0.98]"
            >
              <Sparkles className="w-3.5 h-3.5 text-sage" />
              <span>Load Educational Sample Vault (11 Docs / 44 Chunks)</span>
            </button>
          </>
        )}
      </div>
    </div>
  );
}

function round(val, dec) {
  return Number(Math.round(val + 'e' + dec) + 'e-' + dec);
}
