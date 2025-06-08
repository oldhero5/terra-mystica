/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        // Terra Mystica theme colors
        aurora: {
          purple: 'hsl(280, 100%, 70%)',
          green: 'hsl(160, 100%, 50%)',
          teal: 'hsl(190, 90%, 50%)',
          blue: 'hsl(220, 90%, 60%)',
        },
        cosmic: {
          dark: 'hsl(230, 40%, 10%)',
          medium: 'hsl(230, 30%, 15%)',
          light: 'hsl(230, 20%, 20%)',
        }
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: 0 },
        },
        'aurora-flow': {
          '0%, 100%': { 
            transform: 'translateX(-50%) translateY(-50%) rotate(0deg) scale(1)',
            opacity: '0.6'
          },
          '50%': { 
            transform: 'translateX(-50%) translateY(-50%) rotate(180deg) scale(1.1)',
            opacity: '0.8'
          },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'aurora-flow': 'aurora-flow 20s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      backgroundImage: {
        'aurora-gradient': 'linear-gradient(45deg, hsl(280, 100%, 70%), hsl(190, 90%, 50%), hsl(160, 100%, 50%))',
        'cosmic-gradient': 'linear-gradient(135deg, hsl(230, 40%, 10%), hsl(250, 30%, 15%))',
      }
    },
  },
  plugins: [require('tailwindcss-animate')],
};