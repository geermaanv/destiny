import type { Config } from "tailwindcss";

// Las tres escalas que usa toda la app: `slate` (fondo y neutros), `violet`
// (acción principal) y `gold` (acento). Son variables CSS para poder cambiar el
// tema según la carta (spec X2 v2): la paleta clásica (logo: azul noche, coral y
// dorado) está en globals.css y la de cada tema llega de la API (src/lib/theme.ts).
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        slate: {
          50: "rgb(var(--slate-50) / <alpha-value>)",
          100: "rgb(var(--slate-100) / <alpha-value>)",
          200: "rgb(var(--slate-200) / <alpha-value>)",
          300: "rgb(var(--slate-300) / <alpha-value>)",
          400: "rgb(var(--slate-400) / <alpha-value>)",
          500: "rgb(var(--slate-500) / <alpha-value>)",
          600: "rgb(var(--slate-600) / <alpha-value>)",
          700: "rgb(var(--slate-700) / <alpha-value>)",
          800: "rgb(var(--slate-800) / <alpha-value>)",
          900: "rgb(var(--slate-900) / <alpha-value>)",
          950: "rgb(var(--slate-950) / <alpha-value>)",
        },
        violet: {
          50: "rgb(var(--violet-50) / <alpha-value>)",
          100: "rgb(var(--violet-100) / <alpha-value>)",
          200: "rgb(var(--violet-200) / <alpha-value>)",
          300: "rgb(var(--violet-300) / <alpha-value>)",
          400: "rgb(var(--violet-400) / <alpha-value>)",
          500: "rgb(var(--violet-500) / <alpha-value>)",
          600: "rgb(var(--violet-600) / <alpha-value>)",
          700: "rgb(var(--violet-700) / <alpha-value>)",
          800: "rgb(var(--violet-800) / <alpha-value>)",
          900: "rgb(var(--violet-900) / <alpha-value>)",
          950: "rgb(var(--violet-950) / <alpha-value>)",
        },
        gold: {
          100: "rgb(var(--gold-100) / <alpha-value>)",
          200: "rgb(var(--gold-200) / <alpha-value>)",
          300: "rgb(var(--gold-300) / <alpha-value>)",
          400: "rgb(var(--gold-400) / <alpha-value>)",
          500: "rgb(var(--gold-500) / <alpha-value>)",
        },
      },
    },
  },
  plugins: [],
};

export default config;
