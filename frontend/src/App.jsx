import React, { useState, useEffect, useRef, useCallback } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import PromptSuggestions from './components/PromptSuggestions';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import DashboardView from './components/DashboardView';
import DocumentsView from './components/DocumentsView';
import ApiKeyModal from './components/ApiKeyModal';
import UploadModal from './components/UploadModal';
import AuthModal from './components/AuthModal';
import { Loader2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || '';

export default function App() {
  // Authentication State
  const [token, setToken] = useState(() => localStorage.getItem('obsidian_token') || '');
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('obsidian_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [vaults, setVaults] = useState([
    {
      id: 'default',
      name: 'Primary Vault',
      description: 'Personal knowledge vault',
      icon: 'Folder',
      color: '#2E7D6A',
      is_default: true,
      chunk_count: 0,
    },
  ]);
  const [activeVaultId, setActiveVaultId] = useState('default');
  const [stats, setStats] = useState({
    status: 'Ready',
    vault_id: 'default',
    vault_name: 'Primary Vault',
    total_notes: 0,
    total_chunks: 0,
    total_size_mb: '0.0 MB',
    last_indexed_at: 'Live',
  });
  const [notes, setNotes] = useState([]);
  const [selectedDocFilter, setSelectedDocFilter] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const [selectedModel, setSelectedModel] = useState('gemini-3.5-flash-lite');
  const [selectedProvider, setSelectedProvider] = useState('google');
  const [currentApiKey, setCurrentApiKey] = useState(
    localStorage.getItem('obsidian_api_key') || localStorage.getItem('antigravity_api_key') || ''
  );
  const [toast, setToast] = useState(null);

  const chatEndRef = useRef(null);

  // Show temporary toast notification
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  // Helper for authenticated API calls
  const apiFetch = useCallback(
    async (endpoint, options = {}) => {
      const headers = { ...options.headers };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      if (res.status === 401) {
        // Token expired or invalid
        handleLogout(false);
        throw new Error('Session expired. Please sign in again.');
      }

      return res;
    },
    [token]
  );

  // Logout handler
  const handleLogout = async (callApi = true) => {
    if (callApi && token) {
      try {
        await fetch(`${API_BASE}/api/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (e) {
        // Ignore network errors on logout
      }
    }

    localStorage.removeItem('obsidian_token');
    localStorage.removeItem('obsidian_user');
    setToken('');
    setUser(null);
    setMessages([]);
    setNotes([]);
    setSelectedDocFilter([]);
    showToast('Signed out of personal workspace.', 'success');
  };

  // Login handler
  const handleLoginSuccess = (newToken, newUser) => {
    localStorage.setItem('obsidian_token', newToken);
    localStorage.setItem('obsidian_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
    setMessages([]);
    setSelectedDocFilter([]);
    showToast(`Signed in as ${newUser.full_name || newUser.username}!`);
  };

  // Fetch all user-isolated vaults, stats, and notes from API
  const fetchAllData = useCallback(
    async (targetVaultId) => {
      if (!token) return;
      const currentVault = targetVaultId || activeVaultId;

      try {
        // 1. Fetch user's vaults list
        const vaultsRes = await apiFetch('/api/vaults');
        if (vaultsRes.ok) {
          const vaultsData = await vaultsRes.json();
          if (vaultsData.vaults && vaultsData.vaults.length > 0) {
            setVaults(vaultsData.vaults);
            const activeV = vaultsData.vaults.find((v) => v.is_active);
            if (activeV && !targetVaultId) {
              setActiveVaultId(activeV.id);
            }
          }
        }

        // 2. Fetch stats for user's workspace
        const statsRes = await apiFetch(`/api/stats?vault_id=${currentVault}`);
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }

        // 3. Fetch user's notes in this workspace
        const notesRes = await apiFetch(`/api/notes?vault_id=${currentVault}`);
        if (notesRes.ok) {
          const notesData = await notesRes.json();
          setNotes(notesData.notes || []);
        }
      } catch (err) {
        console.warn('Backend sync warning:', err);
      }
    },
    [token, activeVaultId, apiFetch]
  );

  useEffect(() => {
    if (token) {
      fetchAllData();
    }
  }, [token, fetchAllData]);

  // Switch active vault workspace
  const handleSelectVault = async (vaultId) => {
    if (vaultId === activeVaultId) return;
    try {
      const res = await apiFetch(`/api/vaults/${vaultId}/select`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setActiveVaultId(vaultId);
        if (data.vaults) setVaults(data.vaults);
        if (data.stats) setStats(data.stats);

        // Refresh notes for this vault
        const notesRes = await apiFetch(`/api/notes?vault_id=${vaultId}`);
        if (notesRes.ok) {
          const notesData = await notesRes.json();
          setNotes(notesData.notes || []);
        }

        const selectedVaultObj = vaults.find((v) => v.id === vaultId);
        showToast(`Switched to "${selectedVaultObj?.name || vaultId}"`);
        setSelectedDocFilter([]);
      }
    } catch (err) {
      showToast(`Failed to switch workspace: ${err.message}`, 'error');
    }
  };

  // Create a new vault workspace
  const handleCreateVault = async (vaultData) => {
    const res = await apiFetch('/api/vaults', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(vaultData),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to create workspace');
    }

    if (data.vault) {
      setActiveVaultId(data.vault.id);
      showToast(`Workspace "${data.vault.name}" created!`);
      fetchAllData(data.vault.id);
    }
  };

  // Delete a workspace
  const handleDeleteVault = async (vaultId) => {
    try {
      const res = await apiFetch(`/api/vaults/${vaultId}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to delete workspace');
      }

      showToast(data.message || 'Workspace deleted.');
      if (data.active_vault_id) {
        setActiveVaultId(data.active_vault_id);
      }
      fetchAllData(data.active_vault_id);
    } catch (err) {
      showToast(`Error deleting workspace: ${err.message}`, 'error');
    }
  };

  // Global Keyboard Shortcuts (⌘K, ⌘,, Escape)
  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === ',') {
        e.preventDefault();
        setIsApiKeyModalOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setIsApiKeyModalOpen(false);
        setIsUploadModalOpen(false);
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  const handleSaveApiKey = (provider, key) => {
    setCurrentApiKey(key);
    setSelectedProvider(provider);
    localStorage.setItem('obsidian_api_key', key);
    showToast(`${provider.toUpperCase()} API key activated!`);
  };

  // Auto-scroll chat on new message
  useEffect(() => {
    if (activeTab === 'chat') {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading, activeTab]);

  // Send query
  const handleSendMessage = async (queryText) => {
    if (!queryText.trim() || isLoading) return;

    setActiveTab('chat');
    const userMessage = { role: 'user', content: queryText };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const chatHistory = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await apiFetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          chat_history: chatHistory,
          doc_filter: selectedDocFilter.length > 0 ? selectedDocFilter : undefined,
          vault_id: activeVaultId,
          provider: selectedProvider,
          model: selectedModel,
          api_key: currentApiKey || undefined,
          top_k: 4,
          score_threshold: 0.35,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to process question');
      }

      const data = await res.json();
      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        route: data.route,
        route_reasoning: data.route_reasoning,
        sources: data.sources || [],
        execution_trace: data.execution_trace || [],
        latency_sec: data.latency_sec,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      fetchAllData(activeVaultId);
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${err.message}.`,
        route: 'GENERAL_QUERY',
        latency_sec: 0.0,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Load sample vault into user's active private workspace
  const handleLoadSample = async () => {
    setIsIndexing(true);
    try {
      const res = await apiFetch(`/api/sample-vault?vault_id=${activeVaultId}`, {
        method: 'POST',
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || 'Failed to load sample vault');

      showToast(`Sample vault loaded! Indexed ${data.total_notes} documents into your workspace.`);
      fetchAllData(activeVaultId);
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    } finally {
      setIsIndexing(false);
    }
  };

  // Batch upload multiple files into user's private workspace
  const handleUploadFiles = async (filesToUpload) => {
    if (!filesToUpload || filesToUpload.length === 0) return;
    setIsIndexing(true);

    const formData = new FormData();
    for (const file of filesToUpload) {
      formData.append('files', file);
    }

    try {
      const res = await apiFetch(`/api/upload?vault_id=${activeVaultId}`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || 'Upload failed');

      showToast(data.message || `Indexed ${filesToUpload.length} document(s) successfully!`);
      setIsUploadModalOpen(false);
      fetchAllData(activeVaultId);
    } catch (err) {
      showToast(`Upload failed: ${err.message}`, 'error');
    } finally {
      setIsIndexing(false);
    }
  };

  // Reset database for user's active workspace
  const handleResetVault = async () => {
    const activeVaultObj = vaults.find((v) => v.id === activeVaultId);
    const vaultName = activeVaultObj?.name || 'this workspace';
    if (!window.confirm(`Are you sure you want to wipe all indexed vectors and reset "${vaultName}"?`)) {
      return;
    }
    try {
      const res = await apiFetch(`/api/reset?vault_id=${activeVaultId}`, { method: 'POST' });
      if (res.ok) {
        showToast(`Vector store for "${vaultName}" successfully cleared.`);
        setMessages([]);
        setSelectedDocFilter([]);
        fetchAllData(activeVaultId);
      }
    } catch (err) {
      showToast(`Reset failed: ${err.message}`, 'error');
    }
  };

  // If not authenticated, present the authentication screen
  if (!token || !user) {
    return <AuthModal onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="fixed inset-0 h-full h-[100dvh] w-full overflow-hidden bg-canvas text-charcoal flex font-sans select-none">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 animate-fade-in">
          <div
            className={`px-3.5 py-2 rounded-md text-xs font-mono flex items-center gap-2.5 shadow-elevated border ${
              toast.type === 'error'
                ? 'bg-rose-50 text-rose-800 border-rose-200'
                : 'bg-surface text-charcoal border-border'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                toast.type === 'error' ? 'bg-rose-500' : 'bg-emerald-500'
              }`}
            />
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* Settings / API Key Modal */}
      <ApiKeyModal
        isOpen={isApiKeyModalOpen}
        onClose={() => setIsApiKeyModalOpen(false)}
        currentApiKey={currentApiKey}
        currentProvider={selectedProvider}
        onSaveApiKey={handleSaveApiKey}
      />

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadFiles={handleUploadFiles}
        isIndexing={isIndexing}
        activeVaultName={vaults.find((v) => v.id === activeVaultId)?.name || 'Primary Vault'}
      />

      {/* Mobile Drawer Backdrop */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden backdrop-blur-xs transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Left Column: Fixed Non-Scrolling Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          setIsSidebarOpen(false);
        }}
        stats={stats}
        notes={notes}
        onOpenSettings={() => setIsApiKeyModalOpen(true)}
        isOpen={isSidebarOpen}
        vaults={vaults}
        activeVaultId={activeVaultId}
        onSelectVault={handleSelectVault}
        onCreateVault={handleCreateVault}
        onDeleteVault={handleDeleteVault}
        user={user}
        onLogout={handleLogout}
      />

      {/* Right Column: Navbar (Top Fixed) + Center Scrollable Content Area */}
      <div className="flex-1 flex flex-col h-full h-[100dvh] min-w-0 overflow-hidden bg-canvas relative">
        {/* Top Navbar: Pinned firmly at top */}
        <Navbar
          activeTab={activeTab}
          stats={stats}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          isSidebarOpen={isSidebarOpen}
          onOpenUpload={() => setIsUploadModalOpen(true)}
          onLoadSample={handleLoadSample}
          onClearChat={() => setMessages([])}
          isIndexing={isIndexing}
          onOpenSettings={() => setIsApiKeyModalOpen(true)}
          activeVaultName={vaults.find((v) => v.id === activeVaultId)?.name || 'Primary Vault'}
          user={user}
          onLogout={handleLogout}
        />

        {/* Center: Scrollable Content Body (ONLY this area scrolls) */}
        <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col min-h-0 relative">
          {activeTab === 'chat' ? (
            <div className="flex-1 flex flex-col justify-between min-h-full">
              {/* Chat Feed */}
              {messages.length === 0 ? (
                <PromptSuggestions onSelectPrompt={handleSendMessage} />
              ) : (
                <div className="space-y-4 max-w-4xl mx-auto py-6 px-4 sm:px-6 w-full">
                  {messages.map((msg, idx) => (
                    <ChatMessage key={idx} message={msg} />
                  ))}

                  {/* Assistant Streaming / Thinking Indicator */}
                  {isLoading && (
                    <div className="w-full max-w-3xl lg:max-w-4xl mx-auto px-4 sm:px-6 my-4 animate-fade-in">
                      <div className="rounded-xl bg-surface border border-border p-5 shadow-card flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-[#183B32] border border-[#2E7D6A]/30 flex items-center justify-center text-emerald-300 font-mono text-xs font-bold shrink-0">
                          OK
                        </div>
                        <div className="flex items-center gap-2 text-charcoal-muted font-mono text-xs">
                          <Loader2 className="w-4 h-4 animate-spin text-sage" />
                          <span>Synthesizing response from {vaults.find((v) => v.id === activeVaultId)?.name || 'vault'}...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}

              {/* Floating Bottom Chat Dock */}
              <ChatInput
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                disabled={isIndexing}
                selectedModel={selectedModel}
                onSelectModel={(model, provider) => {
                  setSelectedModel(model);
                  setSelectedProvider(provider);
                }}
                notes={notes}
                selectedDocFilter={selectedDocFilter}
                onUpdateDocFilter={setSelectedDocFilter}
              />
            </div>
          ) : activeTab === 'dashboard' ? (
            <DashboardView
              stats={stats}
              notes={notes}
              onOpenUpload={() => setIsUploadModalOpen(true)}
              onLoadSample={handleLoadSample}
              onResetVault={handleResetVault}
              isIndexing={isIndexing}
              activeVault={vaults.find((v) => v.id === activeVaultId)}
            />
          ) : (
            <DocumentsView
              notes={notes}
              onOpenUpload={() => setIsUploadModalOpen(true)}
              onLoadSample={handleLoadSample}
              isIndexing={isIndexing}
              selectedDocFilter={selectedDocFilter}
              onUpdateDocFilter={setSelectedDocFilter}
              activeVaultName={vaults.find((v) => v.id === activeVaultId)?.name || 'Primary Vault'}
            />
          )}
        </div>
      </div>
    </div>
  );
}
