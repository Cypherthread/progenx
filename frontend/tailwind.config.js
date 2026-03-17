/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(220 13% 20%)',
        input: 'hsl(220 13% 20%)',
        ring: 'hsl(192 91% 47%)',
        background: 'hsl(222 47% 6%)',
        foreground: 'hsl(210 40% 93%)',
        primary: {
          DEFAULT: 'hsl(192 91% 47%)',
          foreground: 'hsl(0 0% 100%)',
        },
        secondary: {
          DEFAULT: 'hsl(220 20% 14%)',
          foreground: 'hsl(210 40% 80%)',
        },
        accent: {
          DEFAULT: 'hsl(192 91% 47%)',
          foreground: 'hsl(0 0% 100%)',
        },
        destructive: {
          DEFAULT: 'hsl(0 63% 55%)',
          foreground: 'hsl(0 0% 100%)',
        },
        muted: {
          DEFAULT: 'hsl(220 20% 14%)',
          foreground: 'hsl(215 16% 55%)',
        },
        card: {
          DEFAULT: 'hsl(222 30% 10%)',
          foreground: 'hsl(210 40% 93%)',
        },
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
