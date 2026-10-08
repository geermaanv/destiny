"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { BirthTimePeriod, createProfile, getProfile, Place, searchPlaces, setBirthData } from "@/lib/api";
import OnboardingSteps from "@/components/OnboardingSteps";

const SEARCH_DEBOUNCE_MS = 300;

const pad = (n: number) => String(n).padStart(2, "0");
const HOURS = Array.from({ length: 24 }, (_, i) => pad(i));
const MINUTES = Array.from({ length: 60 }, (_, i) => pad(i));
// Fecha en tres desplegables (día / mes / año): el calendario nativo abre en el
// año actual y llegar al año de nacimiento es tedioso. Mínimo 18 años (spec A1).
const MIN_AGE = 18;
const MAX_AGE = 100;
const CURRENT_YEAR = new Date().getFullYear();
const YEARS = Array.from({ length: MAX_AGE - MIN_AGE + 1 }, (_, i) => String(CURRENT_YEAR - MIN_AGE - i));
const MONTHS = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];
const daysInMonth = (year: string, month: string) =>
  year && month ? new Date(Number(year), Number(month), 0).getDate() : 31;

function isAdult(isoDate: string): boolean {
  const [y, m, d] = isoDate.split("-").map(Number);
  const today = new Date();
  const eighteenth = new Date(y + MIN_AGE, m - 1, d);
  return eighteenth <= today;
}

// Si no sabe la hora exacta pero recuerda la franja, usamos el punto medio de
// esa franja (desvío máximo de 3 h en vez de 12 h). Mismos valores que la API.
const PERIODS: { value: BirthTimePeriod; label: string; range: string; midpoint: string }[] = [
  { value: "madrugada", label: "Madrugada", range: "00 a 06 hs", midpoint: "03:00" },
  { value: "manana", label: "Mañana", range: "06 a 12 hs", midpoint: "09:00" },
  { value: "tarde", label: "Tarde", range: "12 a 18 hs", midpoint: "15:00" },
  { value: "noche", label: "Noche", range: "18 a 24 hs", midpoint: "21:00" },
];

const SELECT_CLASS =
  "rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400 enabled:cursor-pointer disabled:opacity-40";

// Autocomplete del lugar de nacimiento (spec A1): hay que elegir una opción de
// la lista para tener lat/lon + timezone. Si el geocoder no responde, se
// acepta el texto libre para no bloquear el onboarding.
function PlaceField({
  selected,
  initialText,
  onSelect,
  onUnavailable,
}: {
  selected: Place | null;
  initialText: string;
  onSelect: (place: Place | null, text: string) => void;
  onUnavailable: (unavailable: boolean) => void;
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
  const params = useSearchParams();
  const ref = params.get("ref");
  const existingProfileId = params.get("profileId");
  const [profileId, setProfileId] = useState<string | null>(null);
  const [loadedPlace, setLoadedPlace] = useState<string | null>(existingProfileId ? null : "");
  const started = useRef(false);
  const [birthDay, setBirthDay] = useState("");
  const [birthMonth, setBirthMonth] = useState("");
  const [birthYear, setBirthYear] = useState("");
  const birthDate =
    birthDay && birthMonth && birthYear ? `${birthYear}-${birthMonth}-${birthDay}` : "";
  const [birthPlace, setBirthPlace] = useState("");
  const [place, setPlace] = useState<Place | null>(null);
  const [geocodingDown, setGeocodingDown] = useState(false);
  const [birthHour, setBirthHour] = useState("");
  const [birthMinute, setBirthMinute] = useState("00");
  const birthTime = birthHour ? `${birthHour}:${birthMinute}` : "";
  const [timeUnknown, setTimeUnknown] = useState(false);
  const [timePeriod, setTimePeriod] = useState<BirthTimePeriod | null>(null);
  const chosenPeriod = PERIODS.find((p) => p.value === timePeriod);
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    if (!existingProfileId) {
      createProfile()
        .then((profile) => setProfileId(profile.id))
        .catch(() => setError("No se pudo conectar con la API."));
      return;
    }
    // Volvió desde un paso posterior: se recupera lo cargado en vez de crear otro perfil.
    getProfile(existingProfileId)
      .then((p) => {
        setProfileId(p.id);
        if (p.birth_date) {
          const [y, m, d] = p.birth_date.split("-");
          setBirthYear(y);
          setBirthMonth(m);
          setBirthDay(d);
        }
        if (p.birth_place_query) {
          setBirthPlace(p.birth_place_query);
          if (p.birth_place_lat !== null && p.birth_place_lon !== null && p.birth_place_timezone) {
            setPlace({
              label: p.birth_place_query,
              lat: p.birth_place_lat,
              lon: p.birth_place_lon,
              timezone: p.birth_place_timezone,
            });
          }
        }
        if (p.birth_time) {
          const [hh, mm] = p.birth_time.split(":");
          if (p.birth_time_estimated) {
            setTimeUnknown(true);
            setTimePeriod(PERIODS.find((x) => x.midpoint === `${hh}:${mm}`)?.value ?? null);
          } else {
            setBirthHour(hh);
            setBirthMinute(mm);
          }
        }
        setLoadedPlace(p.birth_place_query ?? "");
      })
      .catch(() => {
        // El perfil ya no se puede editar (ej. verificado) o no existe: se arranca de cero.
        setLoadedPlace("");
        createProfile().then((profile) => setProfileId(profile.id));
      });
  }, [existingProfileId]);

  function nextStepUrl(id: string) {
    const params = new URLSearchParams({ profileId: id });
    if (ref) params.set("ref", ref);
    return `/onboarding/perfil?${params.toString()}`;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!profileId) return;
    if (!birthDate) {
      setError("Completá tu fecha de nacimiento.");
      return;
    }
    if (!isAdult(birthDate)) {
      setError(`Tenés que ser mayor de ${MIN_AGE} años para usar Destiny.`);
      return;
    }
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
        birth_time_period: timeUnknown && timePeriod ? timePeriod : undefined,
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
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/logo.png" alt="Destiny" width={72} height={72} className="mx-auto" />
      <h1 className="text-2xl font-semibold">Tus datos natales</h1>

      <div className="space-y-1">
        <label htmlFor="birth-day" className="block text-sm text-slate-400">
          Fecha de nacimiento
        </label>
        <div className="flex gap-2">
          <select
            id="birth-day"
            aria-label="Día"
            value={birthDay}
            onChange={(e) => setBirthDay(e.target.value)}
            className={`${SELECT_CLASS} w-20`}
          >
            <option value="">Día</option>
            {Array.from({ length: daysInMonth(birthYear, birthMonth) }, (_, i) => pad(i + 1)).map((d) => (
              <option key={d} value={d}>
                {Number(d)}
              </option>
            ))}
          </select>
          <select
            aria-label="Mes"
            value={birthMonth}
            onChange={(e) => {
              setBirthMonth(e.target.value);
              if (Number(birthDay) > daysInMonth(birthYear, e.target.value)) setBirthDay("");
            }}
            className={`${SELECT_CLASS} min-w-0 flex-1`}
          >
            <option value="">Mes</option>
            {MONTHS.map((name, i) => (
              <option key={name} value={pad(i + 1)}>
                {name}
              </option>
            ))}
          </select>
          <select
            aria-label="Año"
            value={birthYear}
            onChange={(e) => {
              setBirthYear(e.target.value);
              if (Number(birthDay) > daysInMonth(e.target.value, birthMonth)) setBirthDay("");
            }}
            className={`${SELECT_CLASS} w-24`}
          >
            <option value="">Año</option>
            {YEARS.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-1">
        <label htmlFor="birth-place" className="block text-sm text-slate-400">
          Lugar de nacimiento
        </label>
        {loadedPlace !== null && (
        <PlaceField
          selected={place}
          initialText={loadedPlace}
          onSelect={(selected, text) => {
            setPlace(selected);
            setBirthPlace(text);
          }}
          onUnavailable={setGeocodingDown}
        />
        )}
      </div>

      <div className="space-y-1">
        <label htmlFor="birth-hour" className="block text-sm text-slate-400">
          Hora de nacimiento
        </label>
        {/* Dos selects en 24 h: el input type="time" nativo usa AM/PM según el
            idioma del navegador y es fácil cargar mal la hora a mano. */}
        <div className="flex items-center gap-2">
          <select
            id="birth-hour"
            aria-label="Hora"
            disabled={timeUnknown}
            value={birthHour}
            onChange={(e) => setBirthHour(e.target.value)}
            className={`${SELECT_CLASS} flex-1`}
          >
            <option value="">Hora</option>
            {HOURS.map((h) => (
              <option key={h} value={h}>
                {h}
              </option>
            ))}
          </select>
          <span className="text-slate-500">:</span>
          <select
            aria-label="Minutos"
            disabled={timeUnknown || !birthHour}
            value={birthMinute}
            onChange={(e) => setBirthMinute(e.target.value)}
            className={`${SELECT_CLASS} flex-1`}
          >
            {MINUTES.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
          <span className="text-sm text-slate-500">hs</span>
        </div>
        <label className="flex items-center gap-2 pt-1 text-sm text-slate-400">
          <input type="checkbox" checked={timeUnknown} onChange={(e) => setTimeUnknown(e.target.checked)} />
          No sé mi hora exacta
        </label>
        {timeUnknown && (
          <div className="space-y-2 rounded-md bg-slate-900 px-3 py-3">
            <p className="text-sm text-slate-300">¿Te acordás si fue de madrugada, a la mañana, a la tarde o a la noche?</p>
            <div className="grid grid-cols-2 gap-2">
              {PERIODS.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => setTimePeriod(timePeriod === p.value ? null : p.value)}
                  className={`rounded-md px-2 py-1.5 text-left ring-1 ${
                    timePeriod === p.value
                      ? "bg-violet-600 text-white ring-violet-500"
                      : "bg-slate-950 text-slate-300 ring-slate-700 hover:ring-violet-400"
                  }`}
                >
                  <span className="block text-sm">{p.label}</span>
                  <span className="block text-xs opacity-70">{p.range}</span>
                </button>
              ))}
            </div>
            <p className="text-xs text-slate-400">
              {chosenPeriod ? (
                <>
                  Tomamos las <span className="text-slate-200">{chosenPeriod.midpoint}</span>, el medio de la{" "}
                  {chosenPeriod.label.toLowerCase()}: así el desvío del cálculo es como mucho de 3 horas.
                </>
              ) : (
                <>
                  Si no te acordás, no pasa nada: tomamos las <span className="text-slate-200">12:00</span>, el
                  mediodía, porque es el punto medio del día y así el desvío del cálculo es el menor posible.
                </>
              )}
            </p>
          </div>
        )}
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
        <div className="flex w-full flex-col items-center gap-6 py-10">
          <OnboardingSteps step={1} />
          <DatosNatalesForm />
        </div>
      </Suspense>
    </main>
  );
}
