"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Page, PageTitle } from "@/components/ui";
import ProfileAvatar from "@/components/ProfileAvatar";
import SystemsGrid, { globalCaption } from "@/components/SystemsGrid";
import { useSessionProfileId } from "@/lib/session";
import { apiUrl, createMatch, DiscoverCandidate, DiscoverFilters, getExplanation } from "@/lib/api";
import { findInLastList } from "@/lib/discover";
import { energyLabel, interestLabel } from "@/lib/profile";

// Perfil de otra persona en Descubrir (spec A11): todas sus fotos antes del match.
function Photos({ c }: { c: DiscoverCandidate }) {
  const [index, setIndex] = useState(0);
  const strip = useRef<HTMLDivElement>(null);
  if (c.photos.length === 0) {
    return (
      <div className="flex aspect-[4/5] items-center justify-center rounded-xl bg-slate-900 ring-1 ring-slate-700">
        <ProfileAvatar photoUrl={null} avatar={c.avatar} sunSign={c.sun_sign} size={96} />
      </div>
    );
  }
  return (
    <div className="space-y-2">
      <div
        ref={strip}
        onScroll={(e) => setIndex(Math.round(e.currentTarget.scrollLeft / e.currentTarget.clientWidth))}
        className="flex snap-x snap-mandatory overflow-x-auto rounded-xl ring-1 ring-slate-700 [scrollbar-width:none]"
      >
        {c.photos.map((url) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img key={url} src={apiUrl(url)} alt="" className="aspect-[4/5] w-full shrink-0 snap-center object-cover" />
        ))}
      </div>
      {c.photos.length > 1 && (
        <div className="flex justify-center gap-1.5">
          {c.photos.map((url, i) => (
            <button
              key={url}
              aria-label={`Foto ${i + 1}`}
              onClick={() => strip.current?.scrollTo({ left: i * strip.current.clientWidth, behavior: "smooth" })}
              className={`h-1.5 w-1.5 rounded-full ${i === index ? "bg-slate-200" : "bg-slate-600"}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function PerfilDeOtra() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const profileId = useSessionProfileId();
  const [found, setFound] = useState<{ filters: DiscoverFilters; candidate: DiscoverCandidate } | null | undefined>(undefined);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [requested, setRequested] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const last = findInLastList(id);
    if (!last) router.replace("/discover"); // se abrió sin pasar por Descubrir
    setFound(last);
  }, [id, router]);

  useEffect(() => {
    if (!profileId || !found) return;
    getExplanation(profileId, id, found.filters.context)
      .then(({ text }) => setExplanation(text))
      .catch(() => setExplanation(""));
  }, [profileId, found, id]);

  async function connect() {
    if (!profileId || connecting) return;
    setConnecting(true);
    setError(null);
    try {
      const { id: matchId, status } = await createMatch(profileId, id);
      if (status === "aceptada") router.push(`/chat/${matchId}`);
      else setRequested(true);
    } catch {
      setError("No pudimos enviar la solicitud. Probá de nuevo.");
    }
    setConnecting(false);
  }

  if (!profileId || !found) return <p className="text-slate-400">Cargando…</p>;
  const c = found.candidate;
  const energy = energyLabel(c.energy_period);

  return (
    <>
      <PageTitle
        title={`${c.display_name ?? "Perfil"}${c.age !== null ? `, ${c.age}` : ""}`}
        subtitle={
          <>
            {[c.sun_sign, c.gender_label, c.distance_km !== null ? `a ${c.distance_km} km` : c.neighborhood]
              .filter(Boolean)
              .join(" · ")}
            {c.verificado && <span className="ml-2 text-xs text-gold-300">✓{"\uFE0E"} Verificado</span>}
          </>
        }
        back={{ href: "/discover", label: "Descubrir" }}
      />
      <Photos c={c} />
      {(c.bio || energy || c.interests.length > 0) && (
        <div className="space-y-2 text-sm">
          {c.bio && <p className="text-slate-200">“{c.bio}”</p>}
          {energy && (
            <p className="text-slate-400">
              {energy.icon} Más energía a la {energy.label.toLowerCase()}
            </p>
          )}
          {c.interests.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {c.interests.map((i) => (
                <span key={i} className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                  {interestLabel(i)}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
      <div className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-slate-700">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-semibold text-gold-300">{c.global_pct}%</span>
          <span className="text-xs text-slate-500">{globalCaption(c.systems)}</span>
        </div>
        <SystemsGrid systems={c.systems} axesGlobal={c.axes_global} large />
        {c.approximate && <p className="text-xs text-slate-500">Astrología aproximada: sin hora exacta de nacimiento no se usan las casas.</p>}
        {c.personality?.flags && c.personality.flags.length > 0 && (
          <p className="text-xs text-gold-300">Diferencia importante en: {c.personality.flags.join(", ").toLowerCase()}.</p>
        )}
        <p className="text-sm text-slate-300">{explanation ?? "Cargando explicación…"}</p>
      </div>
      {requested ? (
        <p className="text-center text-sm text-gold-300">✓ Solicitud enviada. Te avisamos en Mis chats cuando acepte.</p>
      ) : (
        <button
          onClick={connect}
          disabled={connecting}
          className="w-full rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {connecting ? "Enviando solicitud…" : "Conectar"}
        </button>
      )}
      {error && <p className="text-sm text-gold-300">{error}</p>}
    </>
  );
}

export default function PerfilDeOtraPage() {
  return (
    <Page>
      <Suspense>
        <PerfilDeOtra />
      </Suspense>
    </Page>
  );
}
