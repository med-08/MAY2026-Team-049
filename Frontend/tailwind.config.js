/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Sora', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      colors: {
        brand: {
          green: {
            50: '#ecfdf5', 100: '#d1fae5', 400: '#34d399', 500: '#10b981', 600: '#059669', 700: '#047857'
          },
          blue: {
            50: '#eff6ff', 100: '#dbeafe', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8'
          },
          purple: {
            50: '#f5f3ff', 100: '#ede9fe', 400: '#a78bfa', 500: '#8b5cf6', 600: '#7c3aed', 700: '#6d28d9'
          },
          orange: {
            50: '#fff7ed', 100: '#ffedd5', 400: '#fb923c', 500: '#f59e0b', 600: '#d97706', 700: '#b45309'
          }
        }
      },
      boxShadow: {
        soft: '0 2px 8px 0 rgb(15 23 42 / 0.06), 0 1px 2px 0 rgb(15 23 42 / 0.04)',
        'soft-lg': '0 8px 24px -4px rgb(15 23 42 / 0.10), 0 2px 8px -2px rgb(15 23 42 / 0.06)'
      },
      borderRadius: {
        xl: '0.875rem',
        '2xl': '1.25rem'
      },
      backgroundImage: {
        'grad-green': 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
        'grad-blue': 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
        'grad-purple': 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)',
        'grad-orange': 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
        /* Page background: light = mild slate -> sky -> violet wash, dark = slate-950 -> slate-900 -> slate-800 */
        'grad-page-light': 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 45%, #f5f3ff 100%)',
        'grad-page-dark': 'linear-gradient(135deg, #020617 0%, #0f172a 55%, #1e293b 100%)',
        /* Sidebar background: mirrors the page gradients but vertical, so it shifts with the theme too */
        'grad-sidebar-light': 'linear-gradient(180deg, #ffffff 0%, #eff6ff 55%, #f5f3ff 100%)',
        'grad-sidebar-dark': 'linear-gradient(180deg, #020617 0%, #0f172a 60%, #1e293b 100%)'
      }
    }
  },
  plugins: []
}
