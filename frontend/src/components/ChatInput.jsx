import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, ChevronDown, Check, X, Search, FileText, FileCode, CheckSquare, Square } from 'lucide-react';

const MODELS = [
  { id: 'gemini-3.5-flash-lite', label: 'Gemini 3.5 Lite (Fast)', provider: 'google' },
  { id: 'gemini-3.5-flash', label: 'Gemini 3.5 Flash', provider: 'google' },
  { id: 'gemini-3.6-flash', label: 'Gemini 3.6 Flash', provider: 'google' },
  { id: 'gpt-4o-mini', label: 'GPT-4o Mini', provider: 'openai' },
  { id: 'llama-3.3-70b-versatile', label: 'Llama 3.3 (Groq)', provider: 'groq' },
];

export default function ChatInput({
  onSendMessage,
  isLoading,
  disabled,
  selectedModel,
  onSelectModel,
  notes = [],
  selectedDocFilter = [],
  onUpdateDocFilter,
}) {
  const [input, setInput] = useState('');
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);
  const [isDocFilterOpen, setIsDocFilterOpen] = useState(false);
  const [docSearchQuery, setDocSearchQuery] = useState('');
  const textareaRef = useRef(null);
  const filterPopoverRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  // Click outside to close filter popover
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (filterPopoverRef.current && !filterPopoverRef.current.contains(e.target)) {
        setIsDocFilterOpen(false);
      }
    };
    if (isDocFilterOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isDocFilterOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || disabled) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const toggleDocSelection = (source) => {
    if (!onUpdateDocFilter) return;
    if (selectedDocFilter.includes(source)) {
      onUpdateDocFilter(selectedDocFilter.filter((s) => s !== source));
    } else {
      onUpdateDocFilter([...selectedDocFilter, source]);
    }
  };

  const handleSelectAllDocs = () => {
    if (!onUpdateDocFilter) return;
    onUpdateDocFilter(notes.map((n) => n.source));
  };

  const handleClearDocFilter = (e) => {
    if (e) e.stopPropagation();
    if (onUpdateDocFilter) {
      onUpdateDocFilter([]);
    }
  };

  const currentModelObj = MODELS.find((m) => m.id === selectedModel) || MODELS[0];

  const filteredDocs = notes.filter(
    (n) =>
      n.title.toLowerCase().includes(docSearchQuery.toLowerCase()) ||
      n.source.toLowerCase().includes(docSearchQuery.toLowerCase())
  );

  const isFiltered = selectedDocFilter && selectedDocFilter.length > 0 && selectedDocFilter.length < notes.length;

  return (
    <div className="p-2.5 sm:p-4 md:p-6 sticky bottom-0 z-20 pointer-events-none w-full">
      <form
        onSubmit={handleSubmit}
        className="max-w-3xl mx-auto pointer-events-auto relative w-full"
      >
        {/* Multi-Document Selection Popover */}
        {isDocFilterOpen && (
          <div
            ref={filterPopoverRef}
            className="absolute left-1/2 -translate-x-1/2 sm:left-0 sm:translate-x-0 bottom-full mb-2 w-[calc(100vw-1.5rem)] sm:w-96 max-w-sm rounded-lg bg-surface border border-border shadow-elevated p-3.5 space-y-3 z-40 animate-fade-in font-sans"
          >
            <div className="flex items-center justify-between border-b border-border pb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs sm:text-sm font-bold text-charcoal">Filter Grounded Context</span>
                <span className="font-mono text-[11px] text-sage bg-sage-light px-2 py-0.5 rounded border border-sage/20 font-semibold">
                  {selectedDocFilter.length === 0 ? 'All Notes' : `${selectedDocFilter.length} Selected`}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleSelectAllDocs}
                  className="text-xs font-mono text-sage hover:underline"
                >
                  All
                </button>
                <span className="text-zinc-300">·</span>
                <button
                  type="button"
                  onClick={handleClearDocFilter}
                  className="text-xs font-mono text-charcoal-muted hover:text-rose-600"
                >
                  Reset
                </button>
                <button
                  type="button"
                  onClick={() => setIsDocFilterOpen(false)}
                  className="p-1 text-charcoal-muted hover:text-charcoal"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Quick Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-charcoal-subtle" />
              <input
                type="text"
                placeholder="Search notes to include..."
                value={docSearchQuery}
                onChange={(e) => setDocSearchQuery(e.target.value)}
                className="w-full bg-canvas-warm border border-border rounded-md px-2.5 pl-8 py-1.5 text-xs text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-zinc-400 font-sans"
              />
            </div>

            {/* Document Checklist */}
            <div className="max-h-48 overflow-y-auto custom-scrollbar space-y-1 pr-1">
              {filteredDocs.length === 0 ? (
                <div className="py-4 text-center text-xs text-charcoal-muted font-mono">
                  No matching documents.
                </div>
              ) : (
                filteredDocs.map((doc) => {
                  const isChecked =
                    selectedDocFilter.length === 0 ||
                    selectedDocFilter.includes(doc.source);
                  return (
                    <button
                      key={doc.source}
                      type="button"
                      onClick={() => toggleDocSelection(doc.source)}
                      className={`w-full text-left p-2 rounded-md flex items-center justify-between gap-2 text-xs sm:text-[13px] transition-colors border ${
                        isChecked
                          ? 'bg-sage-light/60 border-sage/30 text-charcoal font-medium'
                          : 'bg-transparent border-transparent text-charcoal-muted hover:bg-canvas-warm'
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate min-w-0">
                        {isChecked ? (
                          <CheckSquare className="w-4 h-4 text-sage shrink-0" />
                        ) : (
                          <Square className="w-4 h-4 text-charcoal-subtle shrink-0" />
                        )}
                        <span className="truncate">{doc.title}</span>
                      </div>
                      <span className="font-mono text-[10px] text-charcoal-muted shrink-0">
                        {doc.folder || 'Root'}/
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            <div className="pt-2 border-t border-border flex items-center justify-between text-xs font-mono text-charcoal-muted">
              <span>Targets checked notes</span>
              <button
                type="button"
                onClick={() => setIsDocFilterOpen(false)}
                className="px-2.5 py-1 rounded bg-sage hover:bg-sage-hover text-white text-xs font-sans font-semibold"
              >
                Apply
              </button>
            </div>
          </div>
        )}

        <div className="rounded-xl bg-surface border border-border shadow-dock p-2.5 sm:p-3.5 space-y-2 focus-within:border-zinc-400 transition-all">
          {/* Top Metadata Row: @all-notes / multi-select pill & Model Dropdown */}
          <div className="flex items-center justify-between select-none gap-2">
            {/* Clickable Multi-Document Pill */}
            <div className="flex items-center gap-1.5 min-w-0">
              <button
                type="button"
                onClick={() => setIsDocFilterOpen(!isDocFilterOpen)}
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md border text-[11px] sm:text-xs font-mono transition-all truncate max-w-[130px] sm:max-w-[200px] ${
                  isFiltered
                    ? 'bg-sage-light text-sage border-sage/40 font-semibold shadow-xs'
                    : 'bg-canvas-subtle border-border text-charcoal hover:bg-surface-hover'
                }`}
                title="Click to select multiple documents for grounded retrieval"
              >
                <span className="text-zinc-400">@</span>
                <span className="truncate">
                  {isFiltered
                    ? `${selectedDocFilter.length} doc${selectedDocFilter.length === 1 ? '' : 's'}`
                    : 'all-notes'}
                </span>
                <ChevronDown className="w-3 h-3 text-charcoal-muted shrink-0" />
              </button>

              {isFiltered && (
                <button
                  type="button"
                  onClick={handleClearDocFilter}
                  className="p-1 rounded hover:bg-canvas-subtle text-charcoal-muted hover:text-rose-600 transition-colors shrink-0"
                  title="Reset to all notes"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Model Selector Dropdown */}
            <div className="relative shrink-0">
              <button
                type="button"
                onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-canvas-subtle border border-border text-[11px] sm:text-xs font-mono text-charcoal hover:bg-surface-hover transition-colors max-w-[135px] sm:max-w-[180px] truncate"
              >
                <span className="truncate">{currentModelObj.label}</span>
                <ChevronDown className="w-3 h-3 text-charcoal-muted shrink-0" />
              </button>

              {isModelDropdownOpen && (
                <div className="absolute right-0 bottom-full mb-1.5 w-44 rounded-lg bg-surface border border-border shadow-elevated p-1 space-y-0.5 z-30 font-mono text-xs">
                  {MODELS.map((m) => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => {
                        onSelectModel(m.id, m.provider);
                        setIsModelDropdownOpen(false);
                      }}
                      className={`w-full text-left px-2 py-1.5 rounded-md flex items-center justify-between transition-colors text-xs ${
                        selectedModel === m.id
                          ? 'bg-sage-light text-sage font-bold'
                          : 'text-charcoal-muted hover:text-charcoal hover:bg-surface-hover'
                      }`}
                    >
                      <span className="truncate">{m.label}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Text Input & Send Button */}
          <div className="flex items-end gap-2">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={
                disabled
                  ? 'Indexing...'
                  : isFiltered
                  ? `Ask grounded in ${selectedDocFilter.length} doc(s)...`
                  : 'Ask a question about your vault...'
              }
              className="flex-1 bg-transparent px-1 py-1 text-[16px] text-charcoal placeholder-charcoal-subtle focus:outline-none resize-none max-h-32 custom-scrollbar font-sans leading-relaxed min-w-0"
            />

            <button
              type="submit"
              disabled={!input.trim() || isLoading || disabled}
              className="h-8.5 w-8.5 sm:h-9 sm:w-9 rounded-lg bg-[#2E7D6A] hover:bg-[#266757] text-white flex items-center justify-center transition-all disabled:opacity-40 active:scale-[0.96] shadow-sm shrink-0"
              title="Send Query (Enter)"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin text-white" />
              ) : (
                <Send className="w-4 h-4 text-white" />
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
