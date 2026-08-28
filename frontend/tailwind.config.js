/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: '#F7F5F0',
          subtle: '#F2EFEB',
          warm: '#F9F8F6',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          elevated: '#FBF9F5',
          hover: '#F0EDE6',
          active: '#EAE6DD',
          sidebar: '#F2EFEB',
        },
        sage: {
          DEFAULT: '#2E7D6A',
          hover: '#266757',
          dark: '#1C5447',
          light: '#EAF3F0',
          muted: '#8FB9AD',
        },
        border: {
          DEFAULT: '#E5E2DC',
          subtle: '#EDEAE4',
          strong: '#D1CCC2',
        },
        charcoal: {
          DEFAULT: '#18181B',
          soft: '#27272A',
          muted: '#6B7280',
          subtle: '#9CA3AF',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        serif: ['"Newsreader"', '"Instrument Serif"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
        sm: '6px',
        md: '8px',
        lg: '10px',
        xl: '12px',
        '2xl': '14px',
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
        elevated: '0 4px 16px -2px rgba(0, 0, 0, 0.06), 0 2px 4px -2px rgba(0, 0, 0, 0.04)',
        dock: '0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [],
}
