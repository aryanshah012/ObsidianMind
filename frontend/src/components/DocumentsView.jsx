import React, { useState } from 'react';
import {
  FileText,
  Search,
  ExternalLink,
  Eye,
  X,
  MessageSquare,
  FileCode,
  Folder,
  CheckSquare,
  Square,
  CheckCircle2,
  Filter,
} from 'lucide-react';

export default function DocumentsView({
  notes = [],
  onSelectPrompt,
  onSelectTab,
  selectedDocFilter = [],
  onUpdateDocFilter,
  activeVaultName = 'Primary Vault',
}) {
  const [search, setSearch] = useState('');
  const [selectedFolder, setSelectedFolder] = useState('ALL');
  const [previewNote, setPreviewNote] = useState(null);
  const [previewContent, setPreviewContent] = useState('');
  const [loadingPreview, setLoadingPreview] = useState(false);

  // Extract distinct folders
  const folders = ['ALL', ...new Set(notes.map((n) => n.folder || 'Root'))];

  // Filter notes
  const filteredNotes = notes.filter((n) => {
    const matchesSearch =
      n.title.toLowerCase().includes(search.toLowerCase()) ||
      n.source.toLowerCase().includes(search.toLowerCase());
    const matchesFolder =
      selectedFolder === 'ALL' || (n.folder || 'Root') === selectedFolder;
    return matchesSearch && matchesFolder;
  });

  const toggleSelectOne = (source) => {
    if (!onUpdateDocFilter) return;
    if (selectedDocFilter.includes(source)) {
      onUpdateDocFilter(selectedDocFilter.filter((s) => s !== source));
    } else {
      onUpdateDocFilter([...selectedDocFilter, source]);
    }
  };

  const toggleSelectAllFiltered = () => {
    if (!onUpdateDocFilter) return;
    const allFilteredSources = filteredNotes.map((n) => n.source);
    const allSelected = allFilteredSources.every((s) => selectedDocFilter.includes(s));

    if (allSelected) {
      // Deselect all filtered
      onUpdateDocFilter(selectedDocFilter.filter((s) => !allFilteredSources.includes(s)));
    } else {
      // Add all filtered
      const combined = Array.from(new Set([...selectedDocFilter, ...allFilteredSources]));
      onUpdateDocFilter(combined);
    }
  };

  const handleOpenPreview = async (note) => {
    setPreviewNote(note);
    setLoadingPreview(true);
    setPreviewContent('');
    try {
      const res = await fetch(
        `http://localhost:8000/api/notes/content?source=${encodeURIComponent(note.source)}`
      );
      if (res.ok) {
        const data = await res.json();
        setPreviewContent(data.content);
      } else {
        setPreviewContent(`Document: ${note.source}\nIndexed in vector database with ${note.chunks_count || 2} chunks.`);
      }
    } catch (err) {
      setPreviewContent(`Error loading document preview: ${err.message}`);
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleAskWithSelected = () => {
    onSelectTab('chat');
    if (selectedDocFilter.length === 1) {
      const targetNote = notes.find((n) => n.source === selectedDocFilter[0]);
      onSelectPrompt(`What are the key points in ${targetNote?.title || selectedDocFilter[0]}?`);
    } else {
      onSelectPrompt(`Synthesize the main concepts across the ${selectedDocFilter.length} selected documents.`);
    }
  };

  const isAllFilteredSelected =
    filteredNotes.length > 0 &&
    filteredNotes.every((n) => selectedDocFilter.includes(n.source));

  return (
    <div className="w-full max-w-[72vw] mx-auto py-8 sm:py-10 px-4 sm:px-6 space-y-5 animate-fade-in">
      {/* Search & Folder Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-charcoal-subtle" />
          <input
            type="text"
            placeholder="Search indexed documents by title or path..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-surface border border-border rounded-md pl-9 pr-3 py-1.5 text-xs text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-zinc-400 font-sans shadow-subtle"
          />
        </div>

        {/* Folder Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto custom-scrollbar pb-1 sm:pb-0">
          {folders.map((f) => (
            <button
              key={f}
              onClick={() => setSelectedFolder(f)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono transition-all shrink-0 border ${
                selectedFolder === f
                  ? 'bg-sage-light text-sage border-sage/30 font-semibold'
                  : 'bg-surface text-charcoal-muted border-border hover:text-charcoal hover:bg-surface-hover'
              }`}
            >
              {f === 'ALL' ? 'All Folders' : `${f}/`}
            </button>
          ))}
        </div>
      </div>

      {/* Floating Multi-Selection Action Banner */}
      {selectedDocFilter.length > 0 && (
        <div className="p-3 rounded-lg bg-sage-light border border-sage/30 flex flex-wrap items-center justify-between gap-3 shadow-card animate-fade-in">
          <div className="flex items-center gap-2 font-mono text-xs text-sage font-semibold">
            <CheckCircle2 className="w-4 h-4 text-sage" />
            <span>{selectedDocFilter.length} document(s) selected for grounded retrieval</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onUpdateDocFilter([])}
              className="h-7 px-2.5 rounded bg-surface border border-border text-xs font-mono text-charcoal-muted hover:text-charcoal transition-colors"
            >
              Deselect All
            </button>

            <button
              onClick={handleAskWithSelected}
              className="h-7 px-3 rounded bg-sage hover:bg-sage-hover text-white text-xs font-semibold font-sans flex items-center gap-1.5 transition-all shadow-sm"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ask with Selected ({selectedDocFilter.length})</span>
            </button>
          </div>
        </div>
      )}

      {/* Documents Table Container */}
      <div className="rounded-lg bg-surface border border-border shadow-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-canvas-subtle border-b border-border text-charcoal-muted font-mono uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-3 w-10 text-center">
                  <button
                    type="button"
                    onClick={toggleSelectAllFiltered}
                    className="p-1 text-charcoal-muted hover:text-charcoal"
                    title={isAllFilteredSelected ? 'Deselect all' : 'Select all'}
                  >
                    {isAllFilteredSelected ? (
                      <CheckSquare className="w-4 h-4 text-sage" />
                    ) : (
                      <Square className="w-4 h-4 text-charcoal-subtle" />
                    )}
                  </button>
                </th>
                <th className="py-3 px-3 font-semibold">Document Title</th>
                <th className="py-3 px-4 font-semibold">Folder</th>
                <th className="py-3 px-4 font-semibold">Type</th>
                <th className="py-3 px-4 font-semibold">Size</th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 font-sans text-charcoal">
              {filteredNotes.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-charcoal-muted font-mono text-xs">
                    No documents matching current search filter.
                  </td>
                </tr>
              ) : (
                filteredNotes.map((note, idx) => {
                  const isChecked = selectedDocFilter.includes(note.source);
                  return (
                    <tr
                      key={idx}
                      onClick={() => toggleSelectOne(note.source)}
                      className={`cursor-pointer transition-colors ${
                        isChecked
                          ? 'bg-sage-light/40 hover:bg-sage-light/60'
                          : 'hover:bg-canvas-warm'
                      }`}
                    >
                      <td className="py-3.5 px-3 text-center" onClick={(e) => e.stopPropagation()}>
                        <button
                          type="button"
                          onClick={() => toggleSelectOne(note.source)}
                          className="p-1"
                        >
                          {isChecked ? (
                            <CheckSquare className="w-4 h-4 text-sage" />
                          ) : (
                            <Square className="w-4 h-4 text-charcoal-subtle" />
                          )}
                        </button>
                      </td>

                      <td className="py-3.5 px-3">
                        <div className="flex items-center gap-2.5">
                          <div className="w-6 h-6 rounded bg-canvas-subtle border border-border flex items-center justify-center text-charcoal-muted shrink-0">
                            {note.doc_type === 'pdf' ? (
                              <FileText className="w-3.5 h-3.5 text-rose-500" />
                            ) : (
                              <FileCode className="w-3.5 h-3.5 text-sage" />
                            )}
                          </div>
                          <div className="min-w-0">
                            <div className="font-semibold text-charcoal truncate">
                              {note.title}
                            </div>
                            <div className="font-mono text-[10px] text-charcoal-muted truncate">
                              {note.source}
                            </div>
                          </div>
                        </div>
                      </td>

                      <td className="py-3.5 px-4 font-mono text-xs text-charcoal-muted">
                        <span className="inline-flex items-center gap-1">
                          <Folder className="w-3 h-3 text-zinc-400" />
                          <span>{note.folder || 'Root'}</span>
                        </span>
                      </td>

                      <td className="py-3.5 px-4 font-mono text-[10.5px]">
                        <span
                          className={`px-1.5 py-0.5 rounded uppercase font-bold border ${
                            note.doc_type === 'pdf'
                              ? 'bg-rose-50 text-rose-700 border-rose-200'
                              : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          }`}
                        >
                          {note.doc_type || 'md'}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 font-mono text-xs text-charcoal-muted">
                        {note.size_str || '12 KB'}
                      </td>

                      <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => handleOpenPreview(note)}
                            className="h-7 px-2 rounded hover:bg-canvas-subtle text-charcoal-muted hover:text-charcoal border border-transparent hover:border-border transition-all flex items-center gap-1 font-mono text-[11px]"
                            title="Preview raw text"
                          >
                            <Eye className="w-3 h-3" />
                            <span>Preview</span>
                          </button>

                          <button
                            onClick={() => {
                              onUpdateDocFilter([note.source]);
                              onSelectTab('chat');
                              onSelectPrompt(`What are the key points in ${note.title}?`);
                            }}
                            className="h-7 px-2.5 rounded bg-sage hover:bg-sage-hover text-white transition-all flex items-center gap-1 font-mono text-[11px] shadow-sm"
                            title="Query note in Chat"
                          >
                            <MessageSquare className="w-3.5 h-3.5" />
                            <span>Query</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Note Preview Modal */}
      {previewNote && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs select-none animate-fade-in">
          <div className="w-full max-w-2xl max-h-[85vh] rounded-lg bg-surface border border-border p-5 shadow-elevated flex flex-col space-y-3">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-sm font-bold text-charcoal font-sans">
                  {previewNote.title}
                </h3>
                <p className="font-mono text-[10.5px] text-charcoal-muted">
                  {previewNote.source}
                </p>
              </div>
              <button
                onClick={() => setPreviewNote(null)}
                className="p-1 rounded hover:bg-surface-hover text-charcoal-muted hover:text-charcoal"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-3 rounded bg-canvas-warm border border-border font-mono text-xs text-charcoal leading-relaxed whitespace-pre-wrap">
              {loadingPreview ? (
                <div className="py-8 text-center text-charcoal-muted">
                  Loading note content...
                </div>
              ) : (
                previewContent || 'No preview available.'
              )}
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-border">
              <span className="font-mono text-[11px] text-charcoal-muted">
                Type: {previewNote.doc_type?.toUpperCase() || 'MD'} · {previewNote.size_str || '12 KB'}
              </span>
              <button
                onClick={() => {
                  const note = previewNote;
                  setPreviewNote(null);
                  onUpdateDocFilter([note.source]);
                  onSelectTab('chat');
                  onSelectPrompt(`What are the key points in ${note.title}?`);
                }}
                className="h-8 px-3 rounded bg-sage hover:bg-sage-hover text-white text-xs font-semibold font-sans flex items-center gap-1.5 transition-all"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Ask about this note</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
