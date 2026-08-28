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
    <div className="flex-1 flex flex-col justify-center items-center py-6 sm:py-16 md:py-20 px-3.5 sm:px-6 text-center select-none max-w-4xl mx-auto w-full">
      {/* Top Status Badge */}
      <div className="inline-flex items-center gap-2 mb-3 sm:mb-4 text-[#2E7D6A] font-mono text-[11px] sm:text-xs md:text-sm font-semibold uppercase tracking-widest">
        <svg
          className="w-3.5 h-3.5 sm:w-4 sm:h-4"
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
      <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl lg:text-[56px] text-charcoal tracking-tight leading-[1.15] mb-3 sm:mb-5">
        Find the thread <br />
        <span className="italic font-normal">inside</span> your notes.
      </h1>

      {/* Subtitle */}
      <p className="text-xs sm:text-base md:text-lg text-charcoal-muted max-w-lg mx-auto leading-relaxed mb-6 sm:mb-10 font-sans">
        Ask a question and get an answer grounded in the documents you have indexed. Every response keeps its trail.
      </p>

      {/* 2x2 Suggestion Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-4 w-full max-w-2xl mx-auto">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(item.query)}
            className="text-left p-3.5 sm:p-5 rounded-xl bg-surface border border-border hover:border-zinc-400 hover:shadow-card transition-all group flex flex-col justify-between min-h-[4.75rem] sm:h-28 shadow-subtle active:scale-[0.98]"
          >
            <div className="font-mono text-[10.5px] sm:text-xs uppercase tracking-wider text-charcoal-muted font-medium">
              {item.tag}
            </div>

            <div className="flex items-center justify-between gap-2 mt-2 sm:mt-auto">
              <span className="text-xs sm:text-[15px] font-semibold text-charcoal group-hover:text-black transition-colors font-sans truncate">
                {item.query}
              </span>
              <ArrowUpRight className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-charcoal-subtle group-hover:text-charcoal transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 shrink-0" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
