/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0d14',
        card: '#121724',
        'card-foreground': '#f8fafc',
        border: '#1e293b',
        'border-highlight': '#334155',
        surface: {
          canvas: '#0a0d14',
          subtle: '#0f1420',
          card: '#121724',
          elevated: '#171e2e',
          overlay: 'rgba(18, 24, 38, 0.82)',
          border: 'rgba(255, 255, 255, 0.08)',
          'border-strong': 'rgba(255, 255, 255, 0.16)',
        },
        apple: {
          blue: '#0a84ff',
          'blue-hover': '#0071e3',
          purple: '#bf5af2',
          indigo: '#5e5ce6',
          teal: '#5de6ff',
          emerald: '#30d158',
          amber: '#ff9f0a',
          red: '#ff453a',
          gray: '#8e8e93',
          'gray-subtle': '#636366',
        },
        neon: {
          cyan: '#00f2fe',
          blue: '#4facfe',
          purple: '#a855f7',
          pink: '#ec4899',
          amber: '#f59e0b',
          emerald: '#10b981',
          rose: '#f43f5e',
        },
      },
      boxShadow: {
        'apple-sm': '0 2px 8px -2px rgba(0, 0, 0, 0.4), 0 1px 2px rgba(0, 0, 0, 0.3)',
        'apple-md': '0 8px 24px -4px rgba(0, 0, 0, 0.5), 0 2px 6px rgba(0, 0, 0, 0.3)',
        'apple-lg': '0 16px 40px -8px rgba(0, 0, 0, 0.6), 0 4px 12px rgba(0, 0, 0, 0.4)',
        'apple-glow': '0 0 24px -4px rgba(10, 132, 255, 0.35)',
        'apple-glow-green': '0 0 20px -4px rgba(48, 209, 88, 0.35)',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2.5s infinite ease-in-out',
        'orbit-spin': 'orbit 20s linear infinite',
        'flow-signal': 'flowSignal 1.2s ease-in-out infinite',
        'scan-line': 'scanLine 3s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.4', filter: 'drop-shadow(0 0 8px rgba(10,132,255,0.3))' },
          '50%': { opacity: '1', filter: 'drop-shadow(0 0 16px rgba(10,132,255,0.7))' },
        },
        orbit: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        flowSignal: {
          '0%': { strokeDashoffset: '24' },
          '100%': { strokeDashoffset: '0' },
        },
        scanLine: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' },
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Text"',
          '"SF Pro Display"',
          'system-ui',
          'sans-serif',
        ],
        mono: ['"SF Mono"', 'JetBrains Mono', 'ui-monospace', 'Menlo', 'Monaco', 'monospace'],
      },
    },
  },
  plugins: [],
};
