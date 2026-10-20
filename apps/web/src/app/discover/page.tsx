"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { Page } from "@/components/ui";
import ConnectionsStrip from "@/components/ConnectionsStrip";
import GenderPrefs from "@/components/GenderPrefs";
import PlaceField from "@/components/PlaceField";
import ProfileAvatar from "@/components/ProfileAvatar";
import SystemsGrid, { globalCaption } from "@/components/SystemsGrid";
import { useSessionProfileId } from "@/lib/session";
import {
  apiUrl,
  DiscoverCandidate,
  DiscoverFilters,
  getDiscoverCandidates,
  getMyPersonality,
  getProfile,
  MyPersonality,
  Interest,
  Place,
  Profile,
  Sistema,
  setLookingFor,
  setResidence,
} from "@/lib/api";
import { activeFilterCount, DEFAULT_FILTERS, loadFilters, saveFilters, saveLastList } from "@/lib/discover";
import { interestLabel, INTERESTS } from "@/lib/profile";

const CONTEXTS: { value: DiscoverFilters["context"]; label: string }[] = [
  { value: "pareja", label: "Pareja" },
  { value: "amistad", label: "Amistad" },
  { value: "laboral", label: "Trabajo" },
  { value: "ocasional", label: "Casual" },
];
const MIN_PCTS = [0, 50, 60, 70, 80];
const DISTANCES: (number | null)[] = [null, 5, 10, 25, 50, 100];
const SISTEMAS: { value: Sistema; label: string }[] = [
  { value: "astrologia", label: "Astrología" },
  { value: "personalidad", label: "Test de personalidad" },
];

const pill = (active: boolean) =>
  `rounded-full px-3 py-1.5 text-xs ring-1 ${
    active ? "bg-slate-700 text-white ring-slate-400" : "bg-slate-900 text-slate-300 ring-slate-700 hover:ring-slate-500"
  }`;

function Filters({
  filters,
  onChange,
  myInterests,
}: {
  filters: DiscoverFilters;
  onChange: (f: DiscoverFilters) => void;
  myInterests: Interest[];
}) {
  const [edadMin, setEdadMin] = useState(String(filters.edad_min));
  const [edadMax, setEdadMax] = useState(String(filters.edad_max));

  function applyAges() {
    const clamp = (v: string, fallback: number) => Math.min(99, Math.max(18, Number(v) || fallback));
    let min = clamp(edadMin, 18);
    let max = clamp(edadMax, 99);
    if (min > max) [min, max] = [max, min];
    setEdadMin(String(min));
    setEdadMax(String(max));
    onChange({ ...filters, edad_min: min, edad_max: max });
  }

  return (
    <div className="space-y-4 rounded-xl bg-slate-900 p-4 ring-1 ring-slate-700">
      <div className="space-y-2">
        <p className="text-xs text-slate-400">Sistemas que suman al número global</p>
        <div className="flex flex-wrap gap-2">
          {SISTEMAS.map((s) => {
            const on = filters.sistemas.includes(s.value);
            return (
              <button
                key={s.value}
                // Siempre queda al menos un sistema prendido.
                onClick={() =>
                  on
                    ? filters.sistemas.length > 1 && onChange({ ...filters, sistemas: filters.sistemas.filter((x) => x !== s.value) })
                    : onChange({ ...filters, sistemas: [...filters.sistemas, s.value] })
                }
                className={pill(on)}
              >
                {on ? "✓ " : ""}
                {s.label}
              </button>
            );
          })}
          <span className="self-center text-xs text-slate-500">Numerología, pronto</span>
        </div>
        {filters.sistemas.length < SISTEMAS.length && (
          <p className="text-xs text-gold-300">Sin todos los sistemas, el resultado pierde precisión.</p>
        )}
      </div>
      <div className="space-y-2">
        <p className="text-xs text-slate-400">Distancia</p>
        <div className="flex flex-wrap gap-2">
          {DISTANCES.map((d) => (
            <button key={d ?? "todas"} onClick={() => onChange({ ...filters, max_km: d })} className={pill(filters.max_km === d)}>
              {d === null ? "Cualquiera" : `A menos de ${d} km`}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        <p className="text-xs text-slate-400">Compatibilidad mínima</p>
        <div className="flex flex-wrap gap-2">
          {MIN_PCTS.map((p) => (
            <button key={p} onClick={() => onChange({ ...filters, min_pct: p })} className={pill(filters.min_pct === p)}>
              {p === 0 ? "Cualquiera" : `${p}% o más`}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        <p className="text-xs text-slate-400">Edad</p>
        <div className="flex items-center gap-2 text-sm">
          <input
            inputMode="numeric"
            value={edadMin}
            onChange={(e) => setEdadMin(e.target.value)}
            onBlur={applyAges}
            aria-label="Edad desde"
            className="w-16 rounded-md bg-slate-950 px-2 py-1.5 text-center outline-none ring-1 ring-slate-700 focus:ring-slate-400"
          />
          <span className="text-slate-400">a</span>
          <input
            inputMode="numeric"
            value={edadMax}
            onChange={(e) => setEdadMax(e.target.value)}
            onBlur={applyAges}
            aria-label="Edad hasta"
            className="w-16 rounded-md bg-slate-950 px-2 py-1.5 text-center outline-none ring-1 ring-slate-700 focus:ring-slate-400"
          />
          <span className="text-slate-400">años</span>
        </div>
      </div>
      <div className="space-y-2">
        <div className="flex items-baseline justify-between">
          <p className="text-xs text-slate-400">Intereses (tiene que tener todos los que marques)</p>
          {myInterests.length > 0 && (
            <button onClick={() => onChange({ ...filters, intereses: myInterests })} className="text-xs text-violet-400">
              Usar mis intereses
            </button>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {INTERESTS.map((i) => {
            const on = filters.intereses.includes(i.value);
            return (
              <button
                key={i.value}
                onClick={() =>
                  onChange({
                    ...filters,
                    intereses: on ? filters.intereses.filter((x) => x !== i.value) : [...filters.intereses, i.value],
                  })
                }
                className={pill(on)}
              >
                {i.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Spec B10: con qué criterio se está buscando. Siempre visible: lo que está por defecto
// en gris y sin ✕ (tocarlo abre Filtros); lo que cambiaste, resaltado y con ✕.
function ActiveFilters({
  filters,
  onChange,
  onOpen,
}: {
  filters: DiscoverFilters;
  onChange: (f: DiscoverFilters) => void;
  onOpen: () => void;
}) {
  type Chip = { label: string; clear?: DiscoverFilters };
  const chips: Chip[] = [{ label: CONTEXTS.find((c) => c.value === filters.context)?.label ?? "" }];
  const both = filters.sistemas.length === SISTEMAS.length;
  chips.push(
    both
      ? { label: "Astrología y test" }
      : {
          label: filters.sistemas[0] === "astrologia" ? "Solo astrología" : "Solo test",
          clear: { ...filters, sistemas: DEFAULT_FILTERS.sistemas },
        }
  );
  chips.push(
    filters.max_km === null
      ? { label: "Cualquier distancia" }
      : { label: `A menos de ${filters.max_km} km`, clear: { ...filters, max_km: null } }
  );
  const defaultAges = filters.edad_min === DEFAULT_FILTERS.edad_min && filters.edad_max === DEFAULT_FILTERS.edad_max;
  chips.push({
    label: `${filters.edad_min} a ${filters.edad_max} años`,
    clear: defaultAges ? undefined : { ...filters, edad_min: DEFAULT_FILTERS.edad_min, edad_max: DEFAULT_FILTERS.edad_max },
  });
  chips.push(
    filters.min_pct === 0
      ? { label: "Cualquier compatibilidad" }
      : { label: `${filters.min_pct}% o más`, clear: { ...filters, min_pct: 0 } }
  );
  for (const i of filters.intereses)
    chips.push({ label: interestLabel(i), clear: { ...filters, intereses: filters.intereses.filter((x) => x !== i) } });
  const changed = chips.filter((c) => c.clear).length;

  return (
    <div className="flex flex-wrap gap-2">
      {chips.map((c) =>
        c.clear ? (
          <button
            key={c.label}
            onClick={() => onChange(c.clear!)}
            aria-label={`Sacar filtro ${c.label}`}
            className="inline-flex items-center gap-1.5 rounded-full bg-slate-700 px-3 py-1 text-xs text-white ring-1 ring-slate-400"
          >
            {c.label} <span className="text-slate-300">✕</span>
          </button>
        ) : (
          <button key={c.label} onClick={onOpen} className="rounded-full px-3 py-1 text-xs text-slate-400 ring-1 ring-slate-700">
            {c.label}
          </button>
        )
      )}
      {changed > 1 && (
        <button
          onClick={() => onChange({ ...DEFAULT_FILTERS, context: filters.context })}
          className="rounded-full border border-dashed border-slate-600 px-3 py-1 text-xs text-slate-400"
        >
          Borrar todos
        </button>
      )}
    </div>
  );
}

function CandidateCard({ c }: { c: DiscoverCandidate }) {
  const details = [c.sun_sign, c.distance_km !== null ? `a ${c.distance_km} km` : null].filter(Boolean).join(" · ");
  return (
    <Link href={`/discover/${c.profile_id}`} className="block rounded-xl bg-slate-900 p-3 ring-1 ring-slate-700 hover:ring-slate-500">
      <div className="flex gap-3">
        {c.photo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={apiUrl(c.photo_url)} alt="" className="h-32 w-32 shrink-0 rounded-lg object-cover object-top" />
        ) : (
          <span className="flex h-32 w-32 shrink-0 items-center justify-center rounded-lg bg-slate-800">
            <ProfileAvatar photoUrl={null} avatar={c.avatar} sunSign={c.sun_sign} size={64} />
          </span>
        )}
        <div className="min-w-0 flex-1 space-y-1">
          <p className="font-medium">
            {c.display_name ?? "Sin nombre"}
            {c.age !== null && `, ${c.age}`}
            {details && <span className="font-normal text-slate-400"> · {details}</span>}
          </p>
          {c.verificado && <p className="text-xs text-gold-300">✓{"\uFE0E"} Verificado</p>}
          <p className="text-xs text-gold-300">{c.preview}</p>
          {c.common_interests.length > 0 && (
            <p className="text-xs text-slate-400">
              {c.common_interests.length === 1 ? "1 interés en común" : `${c.common_interests.length} intereses en común`}:{" "}
              {c.common_interests.map((i) => interestLabel(i).toLowerCase()).join(", ")}
            </p>
          )}
          <p className="pt-1 text-3xl font-semibold leading-none text-gold-300">{c.global_pct}%</p>
          <p className="text-xs text-slate-500">{globalCaption(c)}</p>
        </div>
      </div>
      <div className="mt-3">
        <SystemsGrid c={c} />
      </div>
      <p className="mt-2 text-right text-xs text-violet-400">Ver perfil →</p>
    </Link>
  );
}

function ResidencePrompt({ me, onSaved, onSkip }: { me: Profile; onSaved: (p: Profile) => void; onSkip?: () => void }) {
  const [place, setPlace] = useState<Place | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function save() {
    if (!place) {
      setError("Elegí tu ciudad de la lista.");
      return;
    }
    try {
      onSaved(await setResidence(me.id, place));
    } catch {
      setError("No se pudo guardar. Probá de nuevo.");
    }
  }
  return (
    <div className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/50">
      <div>
        <p className="font-medium">¿Dónde vivís?</p>
        <p className="text-xs text-slate-400">Para mostrarte la distancia. Nadie ve tu ciudad: solo los kilómetros.</p>
      </div>
      <PlaceField
        id="residence"
        placeholder="Tu ciudad (ej. Córdoba)"
        selected={place}
        initialText=""
        onSelect={(p) => setPlace(p)}
        onUnavailable={(u) => u && setError("El buscador de ciudades no responde. Probá en un rato.")}
      />
      {error && <p className="text-sm text-gold-300">{error}</p>}
      <button onClick={save} className="w-full rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white">
        Guardar
      </button>
      {onSkip && (
        <button onClick={onSkip} className="w-full text-center text-xs text-slate-500 underline">
          Ahora no
        </button>
      )}
    </div>
  );
}

function DiscoverContent() {
  const profileId = useSessionProfileId();
  const [me, setMe] = useState<Profile | null>(null);
  const [myTest, setMyTest] = useState<MyPersonality | null>(null);
  const [filters, setFilters] = useState<DiscoverFilters>(DEFAULT_FILTERS);
  const [filtersReady, setFiltersReady] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [skipPrefs, setSkipPrefs] = useState(false);
  const [skipResidence, setSkipResidence] = useState(false);
  const [candidates, setCandidates] = useState<DiscoverCandidate[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFilters(loadFilters());
    setFiltersReady(true);
  }, []);

  useEffect(() => {
    if (!profileId) return;
    getProfile(profileId).then(setMe).catch(() => null);
    getMyPersonality(profileId).then(setMyTest).catch(() => null);
  }, [profileId]);

  // Spec A12: lo que busca se guarda en el perfil (ordena el test de personalidad).
  useEffect(() => {
    if (profileId && me && filtersReady && me.looking_for !== filters.context) {
      setLookingFor(profileId, filters.context)
        .then(setMe)
        .catch(() => null);
    }
  }, [profileId, me, filters.context, filtersReady]);

  // La búsqueda espera a que se deje de escribir.
  useEffect(() => {
    const id = setTimeout(() => setSearch(query.trim()), 400);
    return () => clearTimeout(id);
  }, [query]);

  useEffect(() => {
    if (!profileId || !filtersReady) return;
    setCandidates(null);
    setError(null);
    getDiscoverCandidates(profileId, filters, search)
      .then((list) => {
        setCandidates(list);
        saveLastList(filters, list);
      })
      .catch((e: Error) =>
        setError(
          e.message === "409" && filters.max_km !== null && me?.residence_lat == null
            ? "residencia"
            : e.message === "409" && filters.sistemas.length === 1 && filters.sistemas[0] === "personalidad"
            ? "test"
            : e.message === "403"
              ? "Para ver Descubrir primero tenés que verificar tu identidad."
              : e.message === "409"
                ? "Te faltan tus datos natales. Volvé a empezar el registro para completarlos."
                : "No pudimos cargar Descubrir. Probá de nuevo en un rato."
        )
      );
  }, [profileId, filters, filtersReady, search, me?.residence_lat]);

  function update(next: DiscoverFilters) {
    setFilters(next);
    saveFilters(next);
  }

  if (!profileId || !me) return <p className="text-slate-400">Cargando…</p>;

  const needsPrefs = filters.context === "pareja" && (!me.gender || me.show_me.length === 0) && !skipPrefs;
  const filterCount = activeFilterCount(filters);
  // Spec A12: quien dejó Atracción para más tarde y ahora busca pareja o casual.
  const attractionPending =
    (filters.context === "pareja" || filters.context === "ocasional") &&
    myTest !== null &&
    myTest.completed > 0 &&
    Object.keys(myTest.answers).filter((id) => id.startsWith("E1.")).length < 8;
  const needsResidence = !needsPrefs && me.residence_lat === null && (filters.max_km !== null || !skipResidence);

  return (
    <div className="w-full space-y-4">
      <h1 className="text-2xl font-semibold">¿Con quién fluye?</h1>
      {/* Spec U3: sin solapas; las conexiones van en una franja arriba de Descubrir. */}
      <ConnectionsStrip profileId={profileId} />

      {!me.has_photo && (
        <Link
          href="/perfil/fotos?desde=descubrir"
          className="block rounded-xl bg-slate-900 p-3 text-sm text-gold-200 ring-1 ring-gold-400/50"
        >
          Subí tu foto para que otros te vean. <span className="text-violet-400">Subir foto →</span>
        </Link>
      )}

      <div className="flex gap-2">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="⌕ Buscar por nombre"
          className="min-w-0 flex-1 rounded-md bg-slate-900 px-3 py-2 text-sm outline-none ring-1 ring-slate-700 focus:ring-slate-400"
        />
        <button
          onClick={() => setShowFilters((v) => !v)}
          className={`rounded-md px-3 py-2 text-sm ring-1 ${showFilters ? "bg-slate-700 text-white ring-slate-400" : "bg-slate-900 text-slate-300 ring-slate-700"}`}
        >
          Filtros{filterCount > 0 && ` · ${filterCount}`}
        </button>
      </div>

      {!search && (
        <div className="space-y-1">
          <p className="text-xs text-slate-400">¿Qué buscás?</p>
          <div className="flex gap-2">
            {CONTEXTS.map((c) => (
              <button key={c.value} onClick={() => update({ ...filters, context: c.value })} className={`flex-1 ${pill(filters.context === c.value)}`}>
                {c.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {showFilters && !search && (
        <Filters
          key={`${filters.edad_min}-${filters.edad_max}`}
          filters={filters}
          onChange={update}
          myInterests={me.interests ?? []}
        />
      )}
      {!search && <ActiveFilters filters={filters} onChange={update} onOpen={() => setShowFilters(true)} />}

      {needsPrefs && (
        <div className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/50">
          <div>
            <p className="font-medium">Para mostrarte gente para pareja</p>
            <p className="text-xs text-slate-400">Contanos tu género y a quién querés ver. Lo podés cambiar en Editar perfil.</p>
          </div>
          <GenderPrefs profile={me} submitLabel="Guardar y ver" onSaved={setMe} />
          <button onClick={() => setSkipPrefs(true)} className="w-full text-center text-xs text-slate-500 underline">
            Ahora no
          </button>
        </div>
      )}

      {attractionPending && (
        <Link href="/perfil/test?eje=E1" className="block rounded-xl bg-slate-900 p-3 text-sm text-gold-200 ring-1 ring-gold-400/50">
          Completá las preguntas de atracción para tu compatibilidad de pareja →
        </Link>
      )}

      {needsResidence && (
        <ResidencePrompt me={me} onSaved={setMe} onSkip={filters.max_km === null ? () => setSkipResidence(true) : undefined} />
      )}

      {error === "residencia" ? null : error === "test" ? (
        <p className="text-sm text-slate-300">
          Para buscar por personalidad primero completá tu test.{" "}
          <Link href="/perfil/test" className="text-violet-400">
            Hacer el test →
          </Link>
        </p>
      ) : error ? (
        <p className="text-red-400">{error}</p>
      ) : null}

      {!error && candidates === null && <p className="text-slate-400">Cargando…</p>}
      {!error && candidates?.length === 0 && (
        <div className="space-y-1 text-sm text-slate-400">
          {search ? (
            <p>Nadie con ese nombre.</p>
          ) : filterCount > 0 ? (
            <>
              <p>Nadie con estos filtros todavía.</p>
              <button onClick={() => update({ ...DEFAULT_FILTERS, context: filters.context })} className="text-violet-400">
                Ampliar filtros →
              </button>
            </>
          ) : (
            <p>Todavía no hay nadie en tu frecuencia.</p>
          )}
        </div>
      )}
      {!needsPrefs && candidates?.map((c) => <CandidateCard key={c.profile_id} c={c} />)}
    </div>
  );
}

export default function DiscoverPage() {
  return (
    <Page>
      <Suspense>
        <DiscoverContent />
      </Suspense>
    </Page>
  );
}
