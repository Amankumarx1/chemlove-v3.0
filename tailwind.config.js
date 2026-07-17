/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./app.py"
  ],
  theme: {
    extend: {
      colors: {
        "primary": "var(--color-primary, #4cd7f6)",
        "on-primary": "var(--color-on-primary, #001f26)",
        "secondary": "var(--color-secondary, #a1cedb)",
        "tertiary": "var(--color-tertiary, #ffb0cd)",
        "background": "var(--color-background, #0e1416)",
        "surface": "var(--color-surface, #0e1416)",
        "primary-container": "var(--color-primary-container, #06b6d4)",
        "tertiary-container": "var(--color-tertiary-container, #ff79b4)",
        "surface-container": "var(--color-surface-container, #1b2122)",
        "surface-container-low": "var(--color-surface-container-low, #171d1e)",
        "surface-container-high": "var(--color-surface-container-high, #252b2d)",
        "on-surface": "var(--color-on-surface, #dee3e6)",
      },
      fontFamily: {
        headline: ["Inter", "sans-serif"],
        body: ["Inter", "sans-serif"],
      }
    },
  },
  plugins: [],
}
