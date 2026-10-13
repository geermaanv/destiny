// Tema visual según la carta (spec X2 v2): aplica la paleta del tema como
// variables CSS en toda la app y la recuerda en el dispositivo para que no
// parpadee al abrir.
export type Palette = Record<string, Record<string, string>>;

const STORAGE_KEY = "destiny-paleta";

function rgb(hex: string): string {
  return [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(" ");
}

export function applyPalette(palette: Palette, remember = true): void {
  const root = document.documentElement;
  for (const [scale, steps] of Object.entries(palette)) {
    for (const [step, hex] of Object.entries(steps)) {
      root.style.setProperty(`--${scale}-${step}`, rgb(hex));
    }
  }
  if (remember) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(palette));
    } catch {
      // sin almacenamiento: se aplica igual, solo que no se recuerda
    }
  }
}

export function applySavedPalette(): void {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) applyPalette(JSON.parse(saved), false);
  } catch {
    // dato corrupto o sin acceso: queda la paleta clásica
  }
}

// Vuelve a la paleta clásica de globals.css (ej. al cerrar sesión).
export function resetPalette(): void {
  document.documentElement.removeAttribute("style");
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // nada que borrar
  }
}
