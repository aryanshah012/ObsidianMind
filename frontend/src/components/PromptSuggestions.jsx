import React from 'react';
import { ArrowUpRight } from 'lucide-react';

const SUGGESTIONS = [
  {
    tag: "[SYNTHESIS]",
    query: "What did I learn about RAG?",
  },
  {
    tag: "[RECAP]",
    query: "Summarize my research notes",
  },
  {
    tag: "[DISCOVERY]",
    query: "Find notes about vector databases",
  },
  {
    tag: "[EXPLORE]",
    query: "What should I revisit?",
  },
];

export default function PromptSuggestions({ onSelectPrompt }) {
  return (
    <div className="flex-1 flex flex-col justify-center items-center py-14 sm:py-24 px-4 text-center select-none max-w-4xl mx-auto w-full">
      {/* Top Status Badge */}
      <div className="inline-flex items-center gap-2 mb-4 text-[#2E7D6A] font-mono text-xs sm:text-sm font-semibold uppercase tracking-widest">
        <svg
          className="w-4 h-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>
        <span>READY WHEN YOU ARE</span>
      </div>

      {/* Hero Display Heading */}
      <h1 className="font-serif text-4xl sm:text-5xl lg:text-[60px] text-charcoal tracking-tight leading-[1.14] mb-5">
        Find the thread <br />
        <span className="italic font-normal">inside</span> your notes.
      </h1>

      {/* Subtitle */}
      <p className="text-base sm:text-lg text-charcoal-muted max-w-xl mx-auto leading-relaxed mb-12 font-sans">
        Ask a question and get an answer grounded in the documents you have indexed. Every response keeps its trail.
      </p>

      {/* 2x2 Suggestion Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl mx-auto">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(item.query)}
            className="text-left p-5 rounded-xl bg-surface border border-border hover:border-zinc-400 hover:shadow-card transition-all group flex flex-col justify-between h-28 shadow-subtle"
          >
            <div className="font-mono text-xs uppercase tracking-wider text-charcoal-muted font-medium">
              {item.tag}
            </div>

            <div className="flex items-center justify-between gap-3 mt-auto">
              <span className="text-sm sm:text-[15.5px] font-semibold text-charcoal group-hover:text-black transition-colors font-sans">
                {item.query}
              </span>
              <ArrowUpRight className="w-4 h-4 text-charcoal-subtle group-hover:text-charcoal transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 shrink-0" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
