/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/*.html',
    '!./node_modules/**',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1565C0',
        primaryDark: '#0D47A1',
        primaryDeep: '#091B3A',
        gold: '#E8B931',
        goldLight: '#F5D060',
        dark: '#111111',
        bodyText: '#2a2a2a',
        lightGray: '#FAFAFA',
        midGray: '#6B7280',
        warmWhite: '#FFFDF7',
      },
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        body: ['Lora', 'Georgia', 'serif'],
      },
    }
  },
  plugins: [],
}
