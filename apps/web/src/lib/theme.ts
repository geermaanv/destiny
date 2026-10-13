// Tema visual según la carta (spec X2 v2 y v3): paleta (con acento por Venus),
// modo claro/oscuro, tipografía de títulos y cielo de nacimiento de fondo. Se
// aplica como variables CSS en toda la app y se recuerda en el dispositivo
// para que no parpadee al abrir.
export type Palette = Record<string, Record<string, string>>;

export type Look = {
  paleta: Palette;
  modo: "oscuro" | "claro";
  tipografia: string;
  fondo: boolean;
  cielo: { punto: string; lon: number }[];
  cielo_leyenda?: string;
  elementos?: Record<string, number>;
};

const STORAGE_KEY = "destiny-look";
const EVENT = "destiny-look";

function rgb(hex: string): string {
  return [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(" ");
}

export function applyLook(look: Look, remember = true): void {
  const root = document.documentElement;
  for (const [scale, steps] of Object.entries(look.paleta)) {
    for (const [step, hex] of Object.entries(steps)) {
      root.style.setProperty(`--${scale}-${step}`, rgb(hex));
    }
  }
  root.style.colorScheme = look.modo === "claro" ? "light" : "dark";
  // Solo títulos; la tipografía de lectura es la misma en todos los temas.
  root.style.setProperty("--font-display", look.tipografia === "clasica" ? "inherit" : `var(--font-${look.tipografia})`);
  if (remember) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(look));
    } catch {
      // sin almacenamiento: se aplica igual, solo que no se recuerda
    }
  }
  window.dispatchEvent(new CustomEvent<Look>(EVENT, { detail: look }));
}

export function savedLook(): Look | null {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? (JSON.parse(saved) as Look) : null;
  } catch {
    return null;
  }
}

export function onLookChange(handler: (look: Look | null) => void): () => void {
  const listener = (e: Event) => handler((e as CustomEvent<Look | null>).detail);
  window.addEventListener(EVENT, listener);
  return () => window.removeEventListener(EVENT, listener);
}

// Vuelve al tema clásico de globals.css (ej. al cerrar sesión).
export function resetLook(): void {
  document.documentElement.removeAttribute("style");
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // nada que borrar
  }
  window.dispatchEvent(new CustomEvent(EVENT, { detail: null }));
}
