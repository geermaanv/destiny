"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { Page } from "@/components/ui";
import ConexionesTabs from "@/components/ConexionesTabs";
import GenderPrefs from "@/components/GenderPrefs";
import ProfileAvatar from "@/components/ProfileAvatar";
import { useSessionProfileId } from "@/lib/session";
import { apiUrl, DiscoverCandidate, DiscoverFilters, getDiscoverCandidates, getProfile, Profile } from "@/lib/api";
import { activeFilterCount, DEFAULT_FILTERS, loadFilters, saveFilters, saveLastList } from "@/lib/discover";

const CONTEXTS: { value: DiscoverFilters["context"]; label: string }[] = [
  { value: "pareja", label: "Pareja" },
  { value: "amistad", label: "Amistad" },
  { value: "laboral", label: "Trabajo" },
  { value: "ocasional", label: "Casual" },
];
const MIN_PCTS = [0, 50, 60, 70, 80];

const pill = (active: boolean) =>
  `rounded-full px-3 py-1.5 text-xs ring-1 ${
    active ? "bg-slate-700 text-white ring-slate-400" : "bg-slate-900 text-slate-300 ring-slate-700 hover:ring-slate-500"
  }`;

function Filters({ filters, onChange }: { filters: DiscoverFilters; onChange: (f: DiscoverFilters) => void }) {
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
        <p className="text-xs text-slate-400">Según qué sistema</p>
        <div className="flex gap-2">
          <button onClick={() => onChange({ ...filters, sistema: "astrologia" })} className={pill(filters.sistema === "astrologia")}>
            Astrología
          </button>
          <button onClick={() => onChange({ ...filters, sistema: "personalidad" })} className={pill(filters.sistema === "personalidad")}>
            Test de personalidad
          </button>
          <span className="self-center text-xs text-slate-500">Numerología, próximamente</span>
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
    </div>
  );
}

function CandidateCard({ c, big }: { c: DiscoverCandidate; big: boolean }) {
  return (
    <Link
      href={`/discover/${c.profile_id}`}
      className="block overflow-hidden rounded-xl bg-slate-900 ring-1 ring-slate-700 hover:ring-slate-500"
    >
      {c.photo_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={apiUrl(c.photo_url)} alt="" className={`w-full object-cover object-top ${big ? "aspect-square" : "aspect-[16/9]"}`} />
      ) : (
        <div className="flex aspect-[16/9] items-center justify-center bg-slate-800">
          <ProfileAvatar photoUrl={null} avatar={c.avatar} sunSign={c.sun_sign} size={64} />
        </div>
      )}
      <div className="flex items-start gap-3 p-3">
        <div className="min-w-0 flex-1">
          <p className="truncate font-medium">
            {c.display_name ?? "Sin nombre"}
            {c.age !== null && <span className="font-normal text-slate-400">, {c.age}</span>}
            {c.verificado && (
              <span className="ml-1.5 align-middle text-xs font-normal text-gold-300" title="Verificó su WhatsApp">
                ✓{"︎"} Verificado
              </span>
            )}
          </p>
          <p className="text-xs text-slate-400">{[c.sun_sign, c.gender_label, c.neighborhood].filter(Boolean).join(" · ")}</p>
          <p className="text-xs text-gold-300">{c.preview}</p>
        </div>
        <div className="text-right">
          <p className="font-semibold text-gold-300">{c.compatibility_pct}%</p>
          <p className="text-xs text-violet-400">Ver perfil →</p>
        </div>
      </div>
    </Link>
  );
}

function DiscoverContent() {
  const profileId = useSessionProfileId();
  const [me, setMe] = useState<Profile | null>(null);
  const [filters, setFilters] = useState<DiscoverFilters>(DEFAULT_FILTERS);
  const [filtersReady, setFiltersReady] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [skipPrefs, setSkipPrefs] = useState(false);
  const [candidates, setCandidates] = useState<DiscoverCandidate[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFilters(loadFilters());
    setFiltersReady(true);
  }, []);

  useEffect(() => {
    if (profileId) getProfile(profileId).then(setMe).catch(() => null);
  }, [profileId]);

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
          e.message === "409" && filters.sistema === "personalidad"
            ? "test"
            : e.message === "403"
              ? "Para ver Descubrir primero tenés que verificar tu identidad."
              : e.message === "409"
                ? "Te faltan tus datos natales. Volvé a empezar el registro para completarlos."
                : "No pudimos cargar Descubrir. Probá de nuevo en un rato."
        )
      );
  }, [profileId, filters, filtersReady, search]);

  function update(next: DiscoverFilters) {
    setFilters(next);
    saveFilters(next);
  }

  if (!profileId || !me) return <p className="text-slate-400">Cargando…</p>;

  const needsPrefs = filters.context === "pareja" && (!me.gender || me.show_me.length === 0) && !skipPrefs;
  const filterCount = activeFilterCount(filters);

  return (
    <div className="w-full space-y-4">
      <ConexionesTabs />

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

      {showFilters && !search && <Filters filters={filters} onChange={update} />}

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

      {error === "test" ? (
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
      {!needsPrefs && candidates?.map((c, i) => <CandidateCard key={c.profile_id} c={c} big={i === 0 || !search} />)}
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
