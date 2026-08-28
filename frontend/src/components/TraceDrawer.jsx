import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';

export default function TraceDrawer({ trace }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!trace || trace.length === 0) return null;

  return (
    <div className="mt-2 border border-border rounded-md bg-canvas/60 overflow-hidden select-none">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-1.5 flex items-center justify-between text-[11px] font-mono text-charcoal-muted hover:text-charcoal hover:bg-surface-hover transition-colors"
      >
        <div className="flex items-center gap-1.5">
          <Terminal className="w-3 h-3 text-zinc-500" />
          <span>Execution Graph Trail ({trace.length} steps)</span>
        </div>
        <div className="flex items-center gap-1">
          <span>{isOpen ? 'Close' : 'View'}</span>
          {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-3 border-t border-border bg-[#1C1917] text-zinc-300 font-mono text-[11px] space-y-1.5">
          {trace.map((step, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-zinc-500 shrink-0">[{idx + 1}]</span>
              <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
              <span className="text-zinc-200">{step}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
