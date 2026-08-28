import React, { useState } from 'react';
import { User, Copy, Check, Clock, Sparkles } from 'lucide-react';
import SourceCitation from './SourceCitation';
import TraceDrawer from './TraceDrawer';

export default function ChatMessage({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isRAG = message.route === 'KNOWLEDGE_BASE_QUERY';

  return (
    <div className="w-full max-w-3xl lg:max-w-4xl mx-auto px-2 sm:px-4 md:px-6 my-2.5 sm:my-4 animate-fade-in select-text">
      {isUser ? (
        /* ================= USER MESSAGE (AESTHETIC DEEP FOREST GREEN) ================= */
        <div className="rounded-xl bg-[#183B32] text-[#E8F5F1] border border-[#2E7D6A]/50 p-3.5 sm:p-5 md:p-6 shadow-card transition-all">
          <div className="flex items-start gap-2.5 sm:gap-4">
            {/* Dark Forest Avatar */}
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#0F2620] border border-[#2E7D6A]/60 flex items-center justify-center text-emerald-300 font-mono text-xs shrink-0 shadow-inner">
              <User className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-emerald-300" />
            </div>

            {/* User Content Area */}
            <div className="flex-1 min-w-0 space-y-2">
              {/* Header Bar */}
              <div className="flex items-center justify-between select-none">
                <div className="flex items-center gap-2 font-mono text-[11px] sm:text-xs">
                  <span className="font-bold tracking-wider text-emerald-100 uppercase">
                    YOU
                  </span>
                  <span className="text-emerald-500/60">•</span>
                  <span className="text-emerald-300/90 text-[10px] sm:text-[11px] uppercase tracking-widest font-semibold truncate">
                    VAULT QUERY
                  </span>
                </div>

                <button
                  onClick={handleCopy}
                  className="p-1 rounded-md text-emerald-300/70 hover:text-emerald-100 hover:bg-[#132E27] transition-colors shrink-0"
                  title="Copy question"
                >
                  {copied ? (
                    <Check className="w-3.5 h-3.5 text-emerald-300" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>

              {/* User Prompt Text */}
              <div className="text-[14.5px] sm:text-[16px] font-sans font-medium text-[#F2FBF7] leading-relaxed whitespace-pre-wrap word-break">
                {message.content}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* ================= ASSISTANT MESSAGE (WARM LINEN LIGHT THEME) ================= */
        <div className="rounded-xl bg-surface text-charcoal border border-border p-3.5 sm:p-5 md:p-6 shadow-card transition-all space-y-3">
          <div className="flex items-start gap-2.5 sm:gap-4">
            {/* Obsidian Emerald Avatar */}
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#183B32] border border-[#2E7D6A]/30 flex items-center justify-center text-emerald-300 font-mono text-[10.5px] sm:text-[11.5px] font-bold shrink-0 shadow-sm">
              OK
            </div>

            {/* Assistant Content Area */}
            <div className="flex-1 min-w-0 space-y-2.5">
              {/* Header Metadata Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 select-none border-b border-border/60 pb-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-xs sm:text-sm font-bold text-charcoal tracking-tight">
                    OBSIDIAN KNOWLEDGE
                  </span>

                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] sm:text-[10.5px] font-mono font-semibold border uppercase tracking-wider ${
                      isRAG
                        ? 'bg-sage-light text-sage border-sage/30'
                        : 'bg-canvas-subtle text-charcoal-muted border-border'
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        isRAG ? 'bg-sage' : 'bg-charcoal-muted'
                      }`}
                    />
                    <span>{isRAG ? 'Vault Grounded' : 'Direct LLM'}</span>
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  {message.latency_sec !== undefined && (
                    <div className="flex items-center gap-1 text-[11px] sm:text-xs text-charcoal-muted font-mono">
                      <Clock className="w-3 h-3 text-charcoal-subtle" />
                      <span>{message.latency_sec.toFixed(2)}s</span>
                    </div>
                  )}

                  <button
                    onClick={handleCopy}
                    className="p-1 rounded-md text-charcoal-muted hover:text-charcoal hover:bg-canvas-subtle transition-colors shrink-0"
                    title="Copy response"
                  >
                    {copied ? (
                      <Check className="w-3.5 h-3.5 text-sage" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Markdown Rendered Content */}
              <div className="prose-editorial text-charcoal text-[14.5px] sm:text-[16px] leading-[1.75] whitespace-pre-wrap">
                {message.content}
              </div>

              {/* Grounding Source Citations Drawer */}
              {message.sources && message.sources.length > 0 && (
                <div className="pt-2">
                  <SourceCitation sources={message.sources} />
                </div>
              )}

              {/* LangGraph Trace Drawer */}
              {message.execution_trace && message.execution_trace.length > 0 && (
                <div className="pt-1">
                  <TraceDrawer trace={message.execution_trace} />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
