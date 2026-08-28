import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, Tag } from 'lucide-react';

export default function SourceCitation({ sources }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 border border-border rounded-md bg-canvas/80 overflow-hidden select-none">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 flex items-center justify-between text-xs font-mono text-charcoal hover:bg-surface-hover transition-colors"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="w-3.5 h-3.5 text-sage" />
          <span className="font-medium">
            Sources Grounding ({sources.length} {sources.length === 1 ? 'doc' : 'docs'})
          </span>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-charcoal-muted">
          <span>{isExpanded ? 'Hide' : 'Inspect Trail'}</span>
          {isExpanded ? (
            <ChevronUp className="w-3.5 h-3.5" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="p-2.5 space-y-2 border-t border-border bg-surface">
          {sources.map((src, idx) => {
            const scorePct = Math.round((src.highest_score || 0) * 100);
            return (
              <div
                key={idx}
                className="p-2.5 rounded bg-canvas-warm border border-border space-y-1.5 hover:border-zinc-400 transition-all"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-[10px] font-mono font-bold text-sage bg-sage-light px-1.5 py-0.2 rounded border border-sage/20">
                      [{idx + 1}]
                    </span>
                    <span className="text-xs font-semibold text-charcoal truncate">
                      {src.title || src.source}
                    </span>
                  </div>
                  <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-surface border border-border text-charcoal-muted">
                    {src.source}
                  </span>
                </div>

                {/* Score bar & Tags */}
                <div className="flex items-center justify-between gap-3 text-[11px] font-mono text-charcoal-muted">
                  <div className="flex items-center gap-2 flex-1 max-w-xs">
                    <span className="text-[9.5px] uppercase tracking-wider">Relevance:</span>
                    <div className="flex-1 h-1 rounded-full bg-border overflow-hidden">
                      <div
                        className="h-full bg-sage rounded-full"
                        style={{ width: `${Math.min(100, scorePct)}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-sage font-bold">
                      {scorePct}%
                    </span>
                  </div>

                  {src.tags && (
                    <div className="flex items-center gap-1 text-[10px] text-charcoal-muted truncate max-w-[140px]">
                      <Tag className="w-2.5 h-2.5 shrink-0" />
                      <span className="truncate">{src.tags}</span>
                    </div>
                  )}
                </div>

                {/* Excerpts */}
                {src.excerpts && src.excerpts.length > 0 && (
                  <div className="space-y-1 pt-1">
                    {src.excerpts.slice(0, 2).map((exc, eIdx) => (
                      <div
                        key={eIdx}
                        className="text-[11.5px] text-charcoal bg-surface p-2 rounded border-l-2 border-sage font-sans leading-relaxed"
                      >
                        "{exc}"
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
