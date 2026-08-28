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
    <div className="w-full max-w-3xl lg:max-w-4xl mx-auto px-4 sm:px-6 my-4 animate-fade-in select-text">
      {isUser ? (
        /* ================= USER MESSAGE (AESTHETIC DEEP FOREST GREEN) ================= */
        <div className="rounded-xl bg-[#183B32] text-[#E8F5F1] border border-[#2E7D6A]/50 p-5 sm:p-6 shadow-card transition-all">
          <div className="flex items-start gap-4">
            {/* Dark Forest Avatar */}
            <div className="w-8 h-8 rounded-lg bg-[#0F2620] border border-[#2E7D6A]/60 flex items-center justify-center text-emerald-300 font-mono text-xs shrink-0 shadow-inner">
              <User className="w-4 h-4 text-emerald-300" />
            </div>

            {/* User Content Area */}
            <div className="flex-1 min-w-0 space-y-2.5">
              {/* Header Bar */}
              <div className="flex items-center justify-between select-none">
                <div className="flex items-center gap-2.5 font-mono text-xs">
                  <span className="font-bold tracking-wider text-emerald-100 uppercase text-xs">
                    YOU
                  </span>
                  <span className="text-emerald-500/60">•</span>
                  <span className="text-emerald-300/90 text-[11px] uppercase tracking-widest font-semibold">
                    VAULT QUERY
                  </span>
                </div>

                <button
                  onClick={handleCopy}
                  className="p-1.5 rounded-md text-emerald-300/70 hover:text-emerald-100 hover:bg-[#132E27] transition-colors"
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
              <div className="text-[15.5px] sm:text-[16.5px] font-sans font-medium text-[#F2FBF7] leading-relaxed whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* ================= ASSISTANT MESSAGE (WARM LINEN LIGHT THEME) ================= */
        <div className="rounded-xl bg-surface text-charcoal border border-border p-6 sm:p-7 shadow-card transition-all space-y-3.5">
          <div className="flex items-start gap-4">
            {/* Obsidian Emerald Avatar */}
            <div className="w-8 h-8 rounded-lg bg-[#183B32] border border-[#2E7D6A]/30 flex items-center justify-center text-emerald-300 font-mono text-[11.5px] font-bold shrink-0 shadow-sm">
              OK
            </div>

            {/* Assistant Content Area */}
            <div className="flex-1 min-w-0 space-y-3">
              {/* Header Metadata Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2.5 select-none border-b border-border/60 pb-2.5">
                <div className="flex items-center gap-2.5">
                  <span className="font-mono text-xs sm:text-sm font-bold text-charcoal tracking-tight">
                    OBSIDIAN KNOWLEDGE
                  </span>

                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[10.5px] font-mono font-semibold border uppercase tracking-wider ${
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
                    <span>{isRAG ? 'Grounded in Vault' : 'Direct LLM'}</span>
                  </span>
                </div>

                <div className="flex items-center gap-2.5">
                  {message.latency_sec !== undefined && (
                    <div className="flex items-center gap-1.5 text-xs text-charcoal-muted font-mono">
                      <Clock className="w-3.5 h-3.5 text-charcoal-subtle" />
                      <span>{message.latency_sec.toFixed(2)}s</span>
                    </div>
                  )}

                  <button
                    onClick={handleCopy}
                    className="p-1.5 rounded-md text-charcoal-muted hover:text-charcoal hover:bg-canvas-subtle transition-colors"
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
              <div className="prose-editorial text-charcoal text-[15.5px] sm:text-[16.5px] leading-[1.8] whitespace-pre-wrap">
                {message.content}
              </div>

              {/* Grounding Source Citations Drawer */}
              {message.sources && message.sources.length > 0 && (
                <div className="pt-2.5">
                  <SourceCitation sources={message.sources} />
                </div>
              )}

              {/* LangGraph Trace Drawer */}
              {message.execution_trace && message.execution_trace.length > 0 && (
                <div className="pt-1.5">
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
