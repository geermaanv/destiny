"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createProfile, Place, searchPlaces, setBirthData } from "@/lib/api";

// En desktop los inputs date/time solo abren el selector desde el ícono; así se
// abre al tocar cualquier parte del campo (en mobile ya es el comportamiento nativo).
function openPicker(e: React.MouseEvent<HTMLInputElement>) {
  try {
    e.currentTarget.showPicker?.();
  } catch {
    // showPicker puede fallar (ej. input deshabilitado o navegador sin soporte): queda el comportamiento nativo.
  }
}

const SEARCH_DEBOUNCE_MS = 300;

// Autocomplete del lugar de nacimiento (spec A1): hay que elegir una opción de
// la lista para tener lat/lon + timezone. Si el geocoder no responde, se
// acepta el texto libre para no bloquear el onboarding.
function PlaceField({
  selected,
  onSelect,
  onUnavailable,
}: {
  selected: Place | null;
  onSelect: (place: Place | null, text: string) => void;
  onUnavailable: (unavailable: boolean) => void;
}) {
  const [text, setText] = useState("");
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
        id="birth-place"
        type="text"
        required
        autoComplete="off"
        placeholder="Ciudad donde naciste (ej. Buenos Aires)"
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

function DatosNatalesForm() {
  const router = useRouter();
  const ref = useSearchParams().get("ref");
  const [profileId, setProfileId] = useState<string | null>(null);
  const [birthDate, setBirthDate] = useState("");
  const [birthPlace, setBirthPlace] = useState("");
  const [place, setPlace] = useState<Place | null>(null);
  const [geocodingDown, setGeocodingDown] = useState(false);
  const [birthTime, setBirthTime] = useState("");
  const [timeUnknown, setTimeUnknown] = useState(false);
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    createProfile()
      .then((profile) => setProfileId(profile.id))
      .catch(() => setError("No se pudo conectar con la API."));
  }, []);

  function nextStepUrl(id: string) {
    const params = new URLSearchParams({ profileId: id });
    if (ref) params.set("ref", ref);
    return `/onboarding/ritmo-notificaciones?${params.toString()}`;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!profileId) return;
    if (!place && !geocodingDown) {
      setError("Elegí tu ciudad de la lista de sugerencias.");
      return;
    }
    setStatus("submitting");
    setError(null);
    try {
      await setBirthData(profileId, {
        birth_date: birthDate,
        birth_time: timeUnknown || !birthTime ? undefined : birthTime,
        birth_place: place
          ? { query: place.label, lat: place.lat, lon: place.lon, timezone: place.timezone }
          : { query: birthPlace },
      });
      setStatus("done");
      router.push(nextStepUrl(profileId));
    } catch {
      setError("No se pudieron guardar los datos. Probá de nuevo.");
      setStatus("error");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-5">
      <h1 className="text-2xl font-semibold">Tus datos natales</h1>

      <div className="space-y-1">
        <label htmlFor="birth-date" className="block text-sm text-slate-400">
          Fecha de nacimiento
        </label>
        <input
          id="birth-date"
          type="date"
          required
          value={birthDate}
          onChange={(e) => setBirthDate(e.target.value)}
          onClick={openPicker}
          className="w-full cursor-pointer rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400"
        />
      </div>

      <div className="space-y-1">
        <label htmlFor="birth-place" className="block text-sm text-slate-400">
          Lugar de nacimiento
        </label>
        <PlaceField
          selected={place}
          onSelect={(selected, text) => {
            setPlace(selected);
            setBirthPlace(text);
          }}
          onUnavailable={setGeocodingDown}
        />
      </div>

      <div className="space-y-1">
        <label htmlFor="birth-time" className="block text-sm text-slate-400">
          Hora de nacimiento
        </label>
        <input
          id="birth-time"
          type="time"
          disabled={timeUnknown}
          value={birthTime}
          onChange={(e) => setBirthTime(e.target.value)}
          onClick={openPicker}
          className="w-full rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400 enabled:cursor-pointer disabled:opacity-40"
        />
        <label className="flex items-center gap-2 pt-1 text-sm text-slate-400">
          <input type="checkbox" checked={timeUnknown} onChange={(e) => setTimeUnknown(e.target.checked)} />
          No sé mi hora exacta
        </label>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <button
        type="submit"
        disabled={!profileId || status === "submitting"}
        className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white disabled:opacity-50"
      >
        {status === "submitting" ? "Guardando..." : "Continuar"}
      </button>
    </form>
  );
}

export default function DatosNatalesPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <Suspense>
        <DatosNatalesForm />
      </Suspense>
    </main>
  );
}
