/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        glass: {
          bg: 'rgba(15, 23, 42, 0.65)',
          border: 'rgba(255, 255, 255, 0.08)',
          highlight: 'rgba(255, 255, 255, 0.03)',
        },
        cyber: {
          bg: '#090D16',
          primary: '#6366F1', // Indigo 500
          secondary: '#EC4899', // Pink 500
          accent: '#06B6D4', // Cyan 500
          success: '#10B981', // Emerald 500
          warning: '#F59E0B', // Amber 500
          danger: '#EF4444', // Red 500
          text: '#F3F4F6',
          muted: '#9CA3AF'
        }
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s infinite alternate',
        'float-slow': 'float-slow 8s ease-in-out infinite',
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%': { boxShadow: '0 0 5px rgba(99, 102, 241, 0.2), 0 0 15px rgba(99, 102, 241, 0.1)' },
          '100%': { boxShadow: '0 0 15px rgba(99, 102, 241, 0.6), 0 0 30px rgba(99, 102, 241, 0.3)' }
        },
        'float-slow': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-15px)' }
        }
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
