import { DiscoverCandidate, DiscoverFilters } from "@/lib/api";

// Spec B8: los filtros se recuerdan en el navegador. Y la última lista se guarda en la
// pestaña para abrir el perfil de una persona sin volver a calcular todo.
const FILTERS_KEY = "destiny:descubrir:filtros";
const LAST_KEY = "destiny:descubrir:ultima";

export const DEFAULT_FILTERS: DiscoverFilters = {
  context: "pareja",
  sistema: "astrologia",
  min_pct: 0,
  edad_min: 18,
  edad_max: 99,
};

export function loadFilters(): DiscoverFilters {
  try {
    const saved = JSON.parse(localStorage.getItem(FILTERS_KEY) ?? "null");
    return saved ? { ...DEFAULT_FILTERS, ...saved } : DEFAULT_FILTERS;
  } catch {
    return DEFAULT_FILTERS;
  }
}

export function saveFilters(filters: DiscoverFilters) {
  try {
    localStorage.setItem(FILTERS_KEY, JSON.stringify(filters));
  } catch {
    // Sin almacenamiento (ventana privada): los filtros duran lo que dura la pantalla.
  }
}

// Cuántos filtros se apartan del valor por defecto (sin contar el tipo de vínculo).
export function activeFilterCount(f: DiscoverFilters): number {
  return [
    f.sistema !== DEFAULT_FILTERS.sistema,
    f.min_pct !== DEFAULT_FILTERS.min_pct,
    f.edad_min !== DEFAULT_FILTERS.edad_min || f.edad_max !== DEFAULT_FILTERS.edad_max,
  ].filter(Boolean).length;
}

export function saveLastList(filters: DiscoverFilters, candidates: DiscoverCandidate[]) {
  try {
    sessionStorage.setItem(LAST_KEY, JSON.stringify({ filters, candidates }));
  } catch {}
}

export function findInLastList(id: string): { filters: DiscoverFilters; candidate: DiscoverCandidate } | null {
  try {
    const last = JSON.parse(sessionStorage.getItem(LAST_KEY) ?? "null");
    const candidate = last?.candidates?.find((c: DiscoverCandidate) => c.profile_id === id);
    return candidate ? { filters: last.filters, candidate } : null;
  } catch {
    return null;
  }
}
