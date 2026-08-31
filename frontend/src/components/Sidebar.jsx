import React, { useState } from 'react';
import {
  MessageSquare,
  LayoutDashboard,
  FileText,
  Search,
  Settings,
  Circle,
  User,
  LogOut,
  Shield,
} from 'lucide-react';
import VaultSwitcher from './VaultSwitcher';

export default function Sidebar({
  activeTab = 'chat',
  onSelectTab,
  stats,
  notes = [],
  onOpenSettings,
  isOpen,
  onSearchNotes,
  vaults = [],
  activeVaultId = 'default',
  onSelectVault,
  onCreateVault,
  onDeleteVault,
  user,
  onLogout,
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const docCount = stats?.total_notes || notes.length || 0;
  const sizeMb = stats?.total_size_mb || '0.0 MB';

  const handleSearchSubmit = (e) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      if (onSearchNotes) onSearchNotes(searchQuery.trim());
      onSelectTab('documents');
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
    <aside
      className={`fixed lg:sticky top-0 left-0 z-50 w-72 sm:w-80 max-w-[85vw] h-full h-[100dvh] shrink-0 bg-surface-sidebar border-r border-border flex flex-col justify-between transition-transform duration-200 ease-out select-none shadow-xl lg:shadow-none ${
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}
    >
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top Brand Header */}
        <div className="h-20 px-5 border-b border-border flex items-center gap-3.5 shrink-0">
          {/* Isometric 3D Cube Icon */}
          <div className="w-9 h-9 rounded-lg bg-[#183B32] border border-[#2E7D6A]/40 flex items-center justify-center text-emerald-300 shadow-sm shrink-0">
            <svg
              className="w-4.5 h-4.5"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path
                d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="#A7D4C6"
                strokeWidth="1.6"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          <div className="min-w-0">
            <h1 className="text-base font-bold tracking-tight text-charcoal truncate font-sans">
              ObsidianMind
            </h1>
            <div className="font-mono text-[10.5px] uppercase tracking-widest text-charcoal-muted font-medium">
              AI KNOWLEDGE ASSISTANT
            </div>
          </div>
        </div>

        {/* Vault / Workspace Switcher */}
        <div className="p-3.5 pb-2 shrink-0">
          <VaultSwitcher
            vaults={vaults}
            activeVaultId={activeVaultId}
            onSelectVault={onSelectVault}
            onCreateVault={onCreateVault}
            onDeleteVault={onDeleteVault}
          />
        </div>

        {/* Search Bar */}
        <div className="px-3.5 pb-2 shrink-0">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-charcoal-subtle" />
            <input
              type="text"
              placeholder="Search personal notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleSearchSubmit}
              className="w-full bg-surface border border-border rounded-lg pl-9 pr-10 py-2 text-sm text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-zinc-400 font-sans transition-colors shadow-subtle"
            />
            <span className="keycap absolute right-2 top-1/2 -translate-y-1/2 text-[10.5px]">
              ⌘K
            </span>
          </div>
        </div>

        {/* Workspace Navigation Items */}
        <div className="flex-1 px-3.5 py-1.5 space-y-1.5 overflow-y-auto custom-scrollbar">
          <div className="px-2.5 pb-1 font-mono text-[11px] uppercase tracking-wider text-charcoal-muted font-semibold">
            NAVIGATION
          </div>

          {/* Chat Tab */}
          <button
            onClick={() => onSelectTab('chat')}
            className={`w-full text-left px-3.5 py-2.5 rounded-lg text-sm font-semibold flex items-center justify-between transition-all ${
              activeTab === 'chat'
                ? 'bg-surface text-charcoal border border-border shadow-subtle'
                : 'text-charcoal-muted hover:text-charcoal hover:bg-surface-hover border border-transparent'
            }`}
          >
            <div className="flex items-center gap-3">
              <MessageSquare className={`w-4 h-4 ${activeTab === 'chat' ? 'text-sage' : 'text-charcoal-muted'}`} />
              <span>Chat</span>
            </div>
          </button>

          {/* Dashboard / Analytics Tab */}
          <button
            onClick={() => onSelectTab('dashboard')}
            className={`w-full text-left px-3.5 py-2.5 rounded-lg text-sm font-semibold flex items-center justify-between transition-all ${
              activeTab === 'dashboard'
                ? 'bg-surface text-charcoal border border-border shadow-subtle'
                : 'text-charcoal-muted hover:text-charcoal hover:bg-surface-hover border border-transparent'
            }`}
          >
            <div className="flex items-center gap-3">
              <LayoutDashboard className={`w-4 h-4 ${activeTab === 'dashboard' ? 'text-sage' : 'text-charcoal-muted'}`} />
              <span>Dashboard</span>
            </div>
          </button>

          {/* Documents Tab with Live Count */}
          <button
            onClick={() => onSelectTab('documents')}
            className={`w-full text-left px-3.5 py-2.5 rounded-lg text-sm font-semibold flex items-center justify-between transition-all ${
              activeTab === 'documents'
                ? 'bg-surface text-charcoal border border-border shadow-subtle'
                : 'text-charcoal-muted hover:text-charcoal hover:bg-surface-hover border border-transparent'
            }`}
          >
            <div className="flex items-center gap-3">
              <FileText className={`w-4 h-4 ${activeTab === 'documents' ? 'text-sage' : 'text-charcoal-muted'}`} />
              <span>Documents</span>
            </div>
            <span className="font-mono text-xs text-charcoal-muted px-2 py-0.5 rounded-md bg-canvas-subtle border border-border font-medium">
              {docCount}
            </span>
          </button>

          {/* Settings Tab */}
          <button
            onClick={onOpenSettings}
            className="w-full text-left px-3.5 py-2.5 rounded-lg text-sm font-semibold flex items-center justify-between text-charcoal-muted hover:text-charcoal hover:bg-surface-hover border border-transparent transition-all"
          >
            <div className="flex items-center gap-3">
              <Settings className="w-4 h-4 text-charcoal-muted" />
              <span>Settings</span>
            </div>
          </button>
        </div>
      </div>

      {/* Bottom User Profile & Knowledge Base Status */}
      <div className="p-3.5 border-t border-border shrink-0 bg-surface/50 space-y-2.5">
        {/* User Account Info Pill */}
        {user && (
          <div className="p-2.5 rounded-lg bg-surface border border-border flex items-center justify-between shadow-subtle">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-7 h-7 rounded-md bg-sage text-white font-mono text-xs font-bold flex items-center justify-center shrink-0">
                {getInitials()}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-bold text-charcoal truncate font-sans">
                  {user.full_name || user.username}
                </div>
                <div className="text-[10px] text-charcoal-muted font-mono truncate">
                  {user.email}
                </div>
              </div>
            </div>
            {onLogout && (
              <button
                onClick={onLogout}
                className="p-1.5 rounded-md text-charcoal-muted hover:text-rose-600 hover:bg-rose-500/10 transition-colors"
                title="Sign Out"
                aria-label="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}

        {/* Status Footprint */}
        <div className="p-2.5 rounded-lg bg-surface/80 border border-border/80 space-y-1.5 shadow-subtle">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Circle className="w-2 h-2 fill-sage text-sage animate-pulse" />
              <span className="text-[11px] font-bold text-charcoal tracking-tight font-mono">
                {stats?.status === 'Ready' ? 'PERSONAL VAULT READY' : 'ONLINE'}
              </span>
            </div>
            <span className="font-mono text-[10px] text-charcoal-muted font-medium">
              {sizeMb}
            </span>
          </div>

          <div className="flex items-center justify-between text-[10.5px] text-charcoal-muted font-mono pt-1 border-t border-border/60">
            <span>{stats?.total_chunks || 0} chunks</span>
            <span>{docCount} docs</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
