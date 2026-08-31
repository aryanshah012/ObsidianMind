import React from 'react';
import { Upload, Trash2, Menu, X, Sparkles, Loader2, LogOut, User } from 'lucide-react';

export default function Navbar({
  activeTab = 'chat',
  onClearChat,
  onToggleSidebar,
  isSidebarOpen,
  onOpenUpload,
  onLoadSample,
  isIndexing,
  activeVaultName = 'Primary Vault',
  user,
  onLogout,
}) {
  const getTabTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Vault Analytics';
      case 'documents':
        return 'Document Index';
      default:
        return 'Ask knowledge base';
    }
  };

  const getInitials = () => {
    if (!user) return 'U';
    const name = user.full_name || user.username || 'User';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <header className="h-16 sm:h-20 w-full shrink-0 border-b border-border bg-canvas/95 backdrop-blur-md px-3.5 sm:px-8 lg:px-10 flex items-center justify-between sticky top-0 z-30 select-none">
      {/* Left: Breadcrumbs & Section Title */}
      <div className="flex items-center gap-2.5 sm:gap-4 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg hover:bg-surface-hover text-charcoal-muted hover:text-charcoal transition-colors border border-border shadow-subtle shrink-0"
          aria-label="Toggle Navigation"
        >
          {isSidebarOpen ? <X className="w-4.5 h-4.5" /> : <Menu className="w-4.5 h-4.5" />}
        </button>

        <div className="min-w-0 space-y-0.5">
          <div className="flex items-center gap-1.5 font-mono text-[10px] sm:text-xs uppercase tracking-wider text-charcoal-muted font-medium truncate">
            <span className="hidden xs:inline">VAULT:</span>
            <span className="text-sage font-bold truncate max-w-[110px] sm:max-w-[200px]">{activeVaultName}</span>
            <span className="text-zinc-400">/</span>
            <span className="text-charcoal-soft font-semibold capitalize">{activeTab}</span>
          </div>

          <h2 className="text-base sm:text-xl lg:text-2xl font-bold tracking-tight text-charcoal font-sans truncate">
            {getTabTitle()}
          </h2>
        </div>
      </div>

      {/* Right: Upload Vault, 1-Click Demo, & User Profile / Logout */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {/* 1-Click Sample Vault Demo */}
        {onLoadSample && (
          <button
            onClick={onLoadSample}
            disabled={isIndexing}
            className="hidden md:flex h-9 sm:h-10 px-3 sm:px-3.5 rounded-lg bg-surface hover:bg-surface-hover text-charcoal font-sans text-xs font-semibold items-center gap-2 border border-border transition-all shadow-subtle active:scale-[0.98] disabled:opacity-50"
            title="Load sample Obsidian notes into your workspace"
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
          className="h-9 sm:h-10 px-3 sm:px-4 rounded-lg bg-surface hover:bg-surface-hover text-charcoal font-sans text-xs sm:text-sm font-semibold flex items-center gap-1.5 sm:gap-2.5 border border-border transition-all shadow-subtle active:scale-[0.98]"
        >
          <Upload className="w-3.5 sm:w-4 h-3.5 sm:h-4 text-charcoal" />
          <span className="hidden sm:inline">Upload Notes</span>
          <span className="sm:hidden">Upload</span>
        </button>

        {onClearChat && activeTab === 'chat' && (
          <button
            onClick={onClearChat}
            className="h-9 w-9 sm:h-10 sm:w-10 rounded-lg bg-surface hover:bg-surface-hover text-charcoal-muted hover:text-charcoal flex items-center justify-center border border-border transition-all shadow-subtle active:scale-[0.98] shrink-0"
            title="Clear Conversation History"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}

        {/* User Profile Pill & Sign Out Button */}
        {user && (
          <div className="flex items-center gap-1.5 pl-2 border-l border-border">
            <div
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-surface border border-border text-xs font-sans text-charcoal shadow-subtle"
              title={`Logged in as ${user.email || user.username}`}
            >
              <div className="w-6 h-6 rounded-md bg-sage text-white font-mono text-[10.5px] font-bold flex items-center justify-center">
                {getInitials()}
              </div>
              <span className="font-semibold hidden sm:inline max-w-[120px] truncate">
                {user.full_name || user.username}
              </span>
            </div>

            {onLogout && (
              <button
                onClick={onLogout}
                className="h-9 w-9 sm:h-10 sm:w-10 rounded-lg bg-surface hover:bg-rose-500/10 text-charcoal-muted hover:text-rose-600 flex items-center justify-center border border-border hover:border-rose-500/30 transition-all shadow-subtle active:scale-[0.98] shrink-0"
                title="Sign Out"
                aria-label="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
