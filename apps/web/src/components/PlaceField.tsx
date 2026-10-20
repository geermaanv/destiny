"use client";

import { useEffect, useRef, useState } from "react";
import { Place, searchPlaces } from "@/lib/api";

const SEARCH_DEBOUNCE_MS = 300;

// Autocomplete del lugar de nacimiento (spec A1): hay que elegir una opción de
// la lista para tener lat/lon + timezone. Si el geocoder no responde, se
// acepta el texto libre para no bloquear el onboarding.
export default function PlaceField({
  selected,
  initialText,
  onSelect,
  onUnavailable,
  id = "birth-place",
  placeholder = "Ciudad donde naciste (ej. Buenos Aires)",
}: {
  selected: Place | null;
  initialText: string;
  onSelect: (place: Place | null, text: string) => void;
  onUnavailable: (unavailable: boolean) => void;
  id?: string;
  placeholder?: string;
}) {
  const [text, setText] = useState(initialText);
  const [options, setOptions] = useState<Place[]>([]);
  const [open, setOpen] = useState(false);
  const [searching, setSearching] = useState(false);
  const latestQuery = useRef("");

  useEffect(() => {
    const query = text.trim();
    if (selected?.label === text || query.length < 2) {
      setOptions([]);
      return;
    }
    latestQuery.current = query;
    setSearching(true);
    const id = setTimeout(async () => {
      try {
        const results = await searchPlaces(query);
        if (latestQuery.current !== query) return;
        setOptions(results);
        setOpen(true);
        onUnavailable(false);
      } catch {
        onUnavailable(true);
      } finally {
        if (latestQuery.current === query) setSearching(false);
      }
    }, SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(id);
  }, [text, selected, onUnavailable]);

  function choose(place: Place) {
    setText(place.label);
    setOpen(false);
    onSelect(place, place.label);
  }

  return (
    <div className="relative">
      <input
        id={id}
        type="text"
        required
        autoComplete="off"
        placeholder={placeholder}
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          onSelect(null, e.target.value);
        }}
        onFocus={() => options.length > 0 && setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        className="w-full rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400"
      />
      {open && (
        <ul className="absolute z-10 mt-1 w-full overflow-hidden rounded-md bg-slate-900 ring-1 ring-slate-700">
          {options.length === 0 ? (
            <li className="px-3 py-2 text-sm text-slate-500">
              {searching ? "Buscando…" : "Sin resultados. Probá con el nombre de la ciudad."}
            </li>
          ) : (
            options.map((place) => (
              <li key={place.label}>
                <button
                  type="button"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => choose(place)}
                  className="block w-full px-3 py-2 text-left text-sm text-slate-200 hover:bg-slate-800"
                >
                  {place.label}
                </button>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}
