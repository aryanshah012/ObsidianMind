"""
Design system and custom CSS for ObsidianMind.
Features a sleek Obsidian-inspired Dark & Glassmorphism theme.
"""

def get_custom_css() -> str:
    """Return injectible CSS styles for Streamlit."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 950px;
    }

    /* Brand Header Banner */
    .brand-hero {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .brand-title {
        font-size: 26px;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #c084fc, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 0;
        line-height: 1.5;
    }

    /* Status & Metric Cards */
    .stat-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }

    .stat-header {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .stat-value {
        font-size: 20px;
        font-weight: 700;
        color: #f8fafc;
    }

    .status-badge-ready {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    .status-badge-empty {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }

    .pulse-dot {
        width: 7px;
        height: 7px;
        background-color: currentColor;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* Route Badges */
    .badge-rag {
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.2), rgba(168, 85, 247, 0.2));
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.4);
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }

    .badge-general {
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2));
        color: #38bdf8;
        border: 1px solid rgba(6, 182, 212, 0.4);
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Source Citation Card */
    .source-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 8px;
        margin-bottom: 8px;
        transition: all 0.2s ease-in-out;
    }

    .source-card:hover {
        border-color: rgba(168, 85, 247, 0.6);
        background: rgba(30, 41, 59, 0.85);
    }

    .source-title {
        font-weight: 600;
        color: #e2e8f0;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .source-path {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #a78bfa;
        background: rgba(139, 92, 246, 0.12);
        padding: 2px 6px;
        border-radius: 4px;
    }

    .source-excerpt {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 6px;
        line-height: 1.4;
        font-style: italic;
        border-left: 2px solid rgba(139, 92, 246, 0.4);
        padding-left: 8px;
    }

    /* Prompt Suggestion Chips */
    .suggestion-chip {
        display: inline-block;
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.2);
        color: #cbd5e1;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .suggestion-chip:hover {
        background: rgba(139, 92, 246, 0.25);
        border-color: #a78bfa;
        color: #ffffff;
    }

    /* Trace Drawer */
    .trace-container {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #64748b;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 8px;
        padding: 10px;
        margin-top: 8px;
    }
    </style>
    """
