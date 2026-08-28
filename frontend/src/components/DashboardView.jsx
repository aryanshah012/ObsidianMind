import React from 'react';
import {
  FileText,
  Layers,
  HardDrive,
  Cpu,
  FolderTree,
  CheckCircle2,
  RefreshCw,
  Sparkles,
  ArrowUpRight,
  Database,
  Zap,
  Activity,
} from 'lucide-react';

export default function DashboardView({
  stats,
  notes,
  onLoadSample,
  onResetVault,
  onSelectTab,
  activeVault,
}) {
  const totalNotes = stats?.total_notes || notes.length || 0;
  const totalChunks = stats?.total_chunks || 0;
  const totalSize = stats?.total_size_mb || '3.2 MB';
  const embeddingModel = stats?.embedding_model || 'sentence-transformers/all-MiniLM-L6-v2';
  const llmModel = stats?.llm_model || 'gemini-3.6-flash';
  const folderBreakdown = stats?.folder_breakdown || {
    AI: 6,
    Papers: 2,
    Projects: 2,
    Daily: 1,
  };

  const vaultName = activeVault?.name || stats?.vault_name || 'Primary Vault';

  return (
    <div className="w-full max-w-5xl mx-auto py-6 sm:py-10 px-3.5 sm:px-6 space-y-6 sm:space-y-7 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-bold tracking-tight text-charcoal font-sans">
              Knowledge Vault Analytics
            </h2>
            <span
              className="px-2.5 py-0.5 rounded-md text-xs font-mono font-bold text-white shadow-2xs"
              style={{ backgroundColor: activeVault?.color || '#2E7D6A' }}
            >
              {vaultName}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-charcoal-muted">
            Real-time telemetry of indexed markdown notes, PDF archives, and vector embeddings in "{vaultName}".
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onLoadSample}
            className="h-8 px-3 rounded-md bg-canvas-subtle hover:bg-surface-hover border border-border text-xs font-semibold font-mono text-charcoal flex items-center gap-1.5 transition-all shadow-subtle"
          >
            <RefreshCw className="w-3 h-3 text-sage" />
            <span>Re-index Demo Vault</span>
          </button>

          <button
            onClick={() => onSelectTab('chat')}
            className="h-8 px-3.5 rounded-md bg-sage hover:bg-sage-hover text-white text-xs font-semibold font-sans flex items-center gap-1.5 transition-all shadow-sm"
          >
            <span>Ask Vault</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Top 4 KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-lg bg-surface border border-border shadow-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-charcoal-muted mb-2">
            <span className="font-mono text-[11px] uppercase tracking-wider">Indexed Documents</span>
            <FileText className="w-4 h-4 text-sage" />
          </div>
          <div className="text-3xl font-bold font-sans text-charcoal">{totalNotes}</div>
          <div className="text-xs text-charcoal-muted mt-2 flex items-center gap-1.5 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Across 4 vault folders</span>
          </div>
        </div>

        <div className="p-5 rounded-lg bg-surface border border-border shadow-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-charcoal-muted mb-2">
            <span className="font-mono text-[11px] uppercase tracking-wider">Vector Chunks</span>
            <Layers className="w-4 h-4 text-sage" />
          </div>
          <div className="text-3xl font-bold font-sans text-charcoal">{totalChunks}</div>
          <div className="text-xs text-charcoal-muted mt-2 flex items-center gap-1.5 font-mono">
            <Database className="w-3 h-3 text-sage" />
            <span>ChromaDB Vector Store</span>
          </div>
        </div>

        <div className="p-5 rounded-lg bg-surface border border-border shadow-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-charcoal-muted mb-2">
            <span className="font-mono text-[11px] uppercase tracking-wider">Vault Volume</span>
            <HardDrive className="w-4 h-4 text-sage" />
          </div>
          <div className="text-3xl font-bold font-sans text-charcoal">{totalSize}</div>
          <div className="text-xs text-charcoal-muted mt-2 flex items-center gap-1.5 font-mono">
            <span>Markdown & PDF Text</span>
          </div>
        </div>

        <div className="p-5 rounded-lg bg-surface border border-border shadow-card flex flex-col justify-between">
          <div className="flex items-center justify-between text-charcoal-muted mb-2">
            <span className="font-mono text-[11px] uppercase tracking-wider">Retrieval Engine</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-3xl font-bold font-sans text-emerald-700">Online</div>
          <div className="text-xs text-charcoal-muted mt-2 flex items-center gap-1.5 font-mono">
            <Zap className="w-3 h-3 text-amber-500" />
            <span>Cosine Similarity Metric</span>
          </div>
        </div>
      </div>

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Folder Distribution (7 cols) */}
        <div className="lg:col-span-7 p-6 rounded-lg bg-surface border border-border shadow-card space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderTree className="w-4 h-4 text-sage" />
              <h3 className="text-sm font-bold text-charcoal font-sans">
                Vault Folder Breakdown
              </h3>
            </div>
            <span className="font-mono text-xs text-charcoal-muted">
              {Object.keys(folderBreakdown).length} Folders Tracked
            </span>
          </div>

          <div className="space-y-4">
            {Object.entries(folderBreakdown).map(([folder, count]) => {
              const pct = totalNotes > 0 ? Math.round((count / totalNotes) * 100) : 25;
              return (
                <div key={folder} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-charcoal font-semibold">{folder}/</span>
                    <span className="text-charcoal-muted">
                      {count} docs · <span className="text-sage font-bold">{pct}%</span>
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-canvas-subtle overflow-hidden">
                    <div
                      className="h-full bg-sage rounded-full transition-all duration-300"
                      style={{ width: `${Math.max(5, pct)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Vector Engine Diagnostics (5 cols) */}
        <div className="lg:col-span-5 p-6 rounded-lg bg-surface border border-border shadow-card space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-sage" />
                <h3 className="text-sm font-bold text-charcoal font-sans">
                  RAG Pipeline Architecture
                </h3>
              </div>
              <span className="font-mono text-[10px] uppercase text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Ready
              </span>
            </div>

            <div className="space-y-2.5 font-mono text-xs">
              <div className="p-3 rounded-md bg-canvas-warm border border-border flex items-center justify-between">
                <span className="text-charcoal-muted">Embedding Model</span>
                <span className="text-charcoal font-semibold">{embeddingModel}</span>
              </div>

              <div className="p-3 rounded-md bg-canvas-warm border border-border flex items-center justify-between">
                <span className="text-charcoal-muted">LLM Inference Model</span>
                <span className="text-charcoal font-semibold">{llmModel}</span>
              </div>

              <div className="p-3 rounded-md bg-canvas-warm border border-border flex items-center justify-between">
                <span className="text-charcoal-muted">Vector Store Backend</span>
                <span className="text-charcoal font-semibold">ChromaDB (Cosine)</span>
              </div>

              <div className="p-3 rounded-md bg-canvas-warm border border-border flex items-center justify-between">
                <span className="text-charcoal-muted">Query Routing Graph</span>
                <span className="text-charcoal font-semibold">LangGraph StateGraph</span>
              </div>
            </div>
          </div>

          <div className="pt-2 flex items-center gap-2">
            <button
              onClick={() => onSelectTab('documents')}
              className="w-full h-9 rounded-md bg-canvas-subtle hover:bg-surface-hover text-charcoal text-xs font-semibold font-sans border border-border flex items-center justify-center gap-2 transition-all shadow-subtle"
            >
              <span>Explore All Documents</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
