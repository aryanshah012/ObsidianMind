import React, { useState } from 'react';
import { Key, X, CheckCircle2, ShieldCheck, AlertCircle, ExternalLink } from 'lucide-react';

export default function ApiKeyModal({ isOpen, onClose, currentProvider, onSaveKey }) {
  const [provider, setProvider] = useState(currentProvider || 'google');
  const [apiKey, setApiKey] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    if (!apiKey.trim()) return;

    setIsSaving(true);
    setStatusMsg(null);

    try {
      const res = await fetch('/api/settings/api-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: apiKey.trim() }),
      });

      if (!res.ok) throw new Error('Failed to save API key');

      const data = await res.json();
      setStatusMsg({ type: 'success', text: data.message || 'API key saved!' });
      onSaveKey(provider, apiKey.trim());
      setTimeout(() => {
        onClose();
        setStatusMsg(null);
      }, 800);
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs select-none animate-fade-in">
      <div className="w-full max-w-md rounded-lg bg-surface border border-border p-5 shadow-elevated space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-sage-light border border-sage/30 flex items-center justify-center text-sage">
              <Key className="w-3.5 h-3.5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-charcoal font-sans flex items-center gap-2">
                <span>Model Engine Settings</span>
                <span className="keycap">ESC</span>
              </h3>
              <p className="text-[11px] text-charcoal-muted">
                Configure LLM credentials for generative answer synthesis
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

        {statusMsg && (
          <div
            className={`p-2.5 rounded text-xs flex items-center gap-2 border font-mono ${
              statusMsg.type === 'error'
                ? 'bg-rose-50 text-rose-800 border-rose-200'
                : 'bg-emerald-50 text-emerald-800 border-emerald-200'
            }`}
          >
            {statusMsg.type === 'error' ? (
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            )}
            <span>{statusMsg.text}</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          {/* Provider Selector Tabs */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-mono uppercase tracking-wider text-charcoal-muted block">
              Inference Provider
            </label>
            <div className="grid grid-cols-3 gap-1.5">
              {[
                { id: 'google', label: 'Google Gemini', desc: 'Gemini 2.0 Flash' },
                { id: 'openai', label: 'OpenAI', desc: 'GPT-4o Mini' },
                { id: 'groq', label: 'Groq Cloud', desc: 'LLaMA 3.3 70B' },
              ].map((p) => (
                <button
                  type="button"
                  key={p.id}
                  onClick={() => setProvider(p.id)}
                  className={`p-2.5 rounded-md text-left transition-all border ${
                    provider === p.id
                      ? 'bg-sage-light text-sage border-sage/40 font-semibold'
                      : 'bg-canvas-subtle text-charcoal-muted border-border hover:text-charcoal hover:bg-surface-hover'
                  }`}
                >
                  <div className="text-xs">{p.label}</div>
                  <div className="text-[10px] font-mono text-zinc-500 mt-0.5 truncate">{p.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* API Key Input */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-mono uppercase tracking-wider text-charcoal-muted">
                {provider.toUpperCase()} API KEY
              </label>
              {provider === 'google' && (
                <a
                  href="https://aistudio.google.com/app/apikey"
                  target="_blank"
                  rel="noreferrer"
                  className="text-[10px] font-mono text-sage hover:underline flex items-center gap-1"
                >
                  <span>Get Key</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              )}
            </div>
            <input
              type="password"
              placeholder={`Paste ${provider.toUpperCase()}_API_KEY...`}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full bg-surface border border-border rounded-md px-3 py-2 text-xs text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-zinc-400 font-mono shadow-subtle"
            />
          </div>

          <div className="bg-canvas-subtle rounded-md p-2.5 border border-border text-[11px] text-charcoal-muted flex items-start gap-2 font-mono">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span>
              API keys are saved directly into your local workspace <code className="text-charcoal font-semibold">.env</code>.
            </span>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="h-8 px-3 rounded text-xs font-mono text-charcoal-muted hover:text-charcoal hover:bg-surface-hover transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!apiKey.trim() || isSaving}
              className="h-8 px-4 rounded-md bg-sage hover:bg-sage-hover text-white text-xs font-mono font-semibold transition-all disabled:opacity-40 shadow-sm"
            >
              {isSaving ? 'Connecting...' : 'Save & Activate'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
