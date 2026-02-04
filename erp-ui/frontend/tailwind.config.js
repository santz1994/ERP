/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'], // Modern font for data legibility
      },
      colors: {
        // Brand: Enterprise-grade Blue (IBM/Linear style)
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // Primary Action
          600: '#2563eb', // Hover
          700: '#1d4ed8', // Active
          800: '#1e40af', // Deep accents
          900: '#0f172a', // Sidebar/Dark areas
        },
        // Status: Soft pastels for reduced eye-strain
        status: {
          success: '#10b981',  // Emerald
          warning: '#f59e0b',  // Amber
          error: '#ef4444',    // Red
          info: '#3b82f6',     // Blue
          running: '#22c55e',  // Machine running
          idle: '#64748b',     // Machine idle
        },
        // Surface colors for depth & hierarchy
        surface: {
          light: '#ffffff',
          dim: '#f8fafc',      // App background
          dark: '#0f172a',     // Sidebar background
        }
      },
      boxShadow: {
        'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'elevated': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        fadeIn: 'fadeIn 0.3s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class', // Safer strategy - won't override browser defaults aggressively
    }),
  ],
}
