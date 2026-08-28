import React from 'react';
import { Upload, Trash2, Menu, X, Sparkles, Loader2 } from 'lucide-react';

export default function Navbar({
  activeTab = 'chat',
  onClearChat,
  onToggleSidebar,
  isSidebarOpen,
  onOpenUpload,
  onLoadSample,
  isIndexing,
  activeVaultName = 'Primary Vault',
}) {
  const getTabTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Vault Analytics & Health';
      case 'documents':
        return 'Document Index';
      default:
        return 'Ask your knowledge base';
    }
  };

  return (
    <header className="h-20 w-full shrink-0 border-b border-border bg-canvas/90 backdrop-blur-sm px-6 sm:px-10 lg:px-12 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* Left: Breadcrumbs & Section Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg hover:bg-surface-hover text-charcoal-muted hover:text-charcoal transition-colors border border-border shadow-subtle"
          aria-label="Toggle Navigation"
        >
          {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        <div className="space-y-1">
          <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-charcoal-muted font-medium">
            <span>WORKSPACE</span>
            <span className="text-zinc-400">/</span>
            <span className="text-sage font-bold">{activeVaultName}</span>
            <span className="text-zinc-400">/</span>
            <span className="text-charcoal-soft font-bold">{activeTab}</span>
          </div>

          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-charcoal font-sans">
            {getTabTitle()}
          </h2>
        </div>
      </div>

      {/* Right: Upload Vault & 1-Click Demo Actions */}
      <div className="flex items-center gap-3">
        {/* 1-Click Sample Vault Demo */}
        {onLoadSample && (
          <button
            onClick={onLoadSample}
            disabled={isIndexing}
            className="hidden sm:flex h-10 px-3.5 rounded-lg bg-surface hover:bg-surface-hover text-charcoal font-sans text-xs font-semibold items-center gap-2 border border-border transition-all shadow-subtle active:scale-[0.98] disabled:opacity-50"
            title="Load sample Obsidian notes into this workspace"
          >
            {isIndexing ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-sage" />
            ) : (
              <Sparkles className="w-3.5 h-3.5 text-sage" />
            )}
            <span>Demo Vault</span>
          </button>
        )}

        <button
          onClick={onOpenUpload}
          className="h-10 px-4 rounded-lg bg-surface hover:bg-surface-hover text-charcoal font-sans text-sm font-semibold flex items-center gap-2.5 border border-border transition-all shadow-subtle active:scale-[0.98]"
        >
          <Upload className="w-4 h-4 text-charcoal" />
          <span>Upload Notes</span>
        </button>

        {onClearChat && activeTab === 'chat' && (
          <button
            onClick={onClearChat}
            className="h-10 w-10 rounded-lg bg-surface hover:bg-surface-hover text-charcoal-muted hover:text-charcoal flex items-center justify-center border border-border transition-all shadow-subtle active:scale-[0.98]"
            title="Clear Conversation History"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  );
}
