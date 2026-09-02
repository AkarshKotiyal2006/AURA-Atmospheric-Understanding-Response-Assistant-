/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      colors: {
        ink: {
          950: "#080B10",
          900: "#0A0E14",
          800: "#101826",
          700: "#16202E",
          600: "#1E2A3A",
          500: "#2B3A4D",
        },
        mist: {
          400: "#7C8B9C",
          200: "#B7C3D0",
          50: "#E4ECF3",
        },
        signal: {
          teal: "#3ED6C4",
          tealDim: "#1F5F58",
        },
        risk: {
          low: "#3EDB84",
          moderate: "#F2C14E",
          high: "#F2884B",
          critical: "#F0505A",
        },
      },
      boxShadow: {
        panel: "0 0 0 1px rgba(62,214,196,0.06), 0 8px 24px rgba(0,0,0,0.35)",
      },
    },
  },
  plugins: [],
};
