/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Dark obsidian palette
        obsidian: '#0f0f11', // page background
        surface: '#18181b', // cards and panels (zinc-900)
        'card-border': '#27272a', // card borders and dividers (zinc-800)
        brand: {
          DEFAULT: '#2563eb', // primary brand blue
          light: '#3b82f6', // hover, focus rings, accents
        },
        content: {
          primary: '#f4f4f5',
          secondary: '#a1a1aa',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
