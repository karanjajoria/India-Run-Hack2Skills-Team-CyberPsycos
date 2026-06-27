/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0D0F14',
        slate: '#1A1D26',
        panel: '#22263A',
        border: '#2E3347',
        muted: '#6B7394',
        ghost: '#9BA3BF',
        light: '#E8EAF2',
        accent: '#5B6EF5',
        'accent-dim': '#3D50D4',
        emerald: '#10C27A',
        amber: '#F59E0B',
        rose: '#F43F5E',
        violet: '#8B5CF6',
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        display: ['"Syne"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
