import type { Config } from "tailwindcss";

// Paleta de marca, tomada del logo de Destiny: azul noche, coral (las manos) y
// dorado (los astros). En vez de cambiar cada clase, se redefinen las escalas
// que ya usa la app: `slate` pasa a ser la escala de azul noche (neutros) y
// `violet` la de coral (acción principal). `gold` es el acento.
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        slate: {
          50: "#f9f7f1",
          100: "#f4f1e8",
          200: "#e3e0f2",
          300: "#c9c6e3",
          400: "#a6a3cc",
          500: "#807daa",
          600: "#5b5890",
          700: "#3a3779",
          800: "#25225b", // azul noche del logo
          900: "#1a1844",
          950: "#0e0d29",
        },
        violet: {
          50: "#fff1f0",
          100: "#ffe0de",
          200: "#ffc6c2",
          300: "#ff9e98",
          400: "#fe7068",
          500: "#fc4b43", // coral de las manos del logo
          600: "#e9342c",
          700: "#c4261f",
          800: "#a2231e",
          900: "#86231f",
          950: "#490d0a",
        },
        gold: {
          100: "#fdf4d3",
          200: "#fbe7a2",
          300: "#f8d66b",
          400: "#f5c542", // dorado de los astros del logo
          500: "#e0aa1f",
        },
      },
    },
  },
  plugins: [],
};

export default config;
