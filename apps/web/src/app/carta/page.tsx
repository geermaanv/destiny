"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import AskBox from "@/components/AskBox";
import { SkyWheel } from "@/components/BirthSky";
import { Card, ListCard, ListRow, Page, PageTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import {
  createShare,
  deleteShare,
  getMyPersonality,
  getShare,
  ShareStatus,
  getNatalDimensions,
  getNatalSynthesis,
  getStyle,
  MyPersonality,
  NatalDimension,
  NatalDimensions,
  NatalFoundation,
  Style,
} from "@/lib/api";

// Mi carta (spec A8; pestaña propia y en pestañas por dimensión, spec U1-D).
const POINT_NAMES: Record<string, string> = {
  sol: "Sol", luna: "Luna", mercurio: "Mercurio", venus: "Venus", marte: "Marte", jupiter: "Júpiter",
  saturno: "Saturno", urano: "Urano", neptuno: "Neptuno", pluton: "Plutón", asc: "Ascendente",
  mc: "Medio Cielo", desc: "Descendente", ic: "Fondo de Cielo",
};
const ASPECT_NAMES: Record<string, string> = {
  conjuncion: "conjunción", sextil: "sextil", cuadratura: "cuadratura", trigono: "trígono", oposicion: "oposición",
};
const SHORT: Record<string, string> = { identidad: "Identidad", amor: "Amor", vocacion: "Vocación", emociones: "Emociones" };

function label(f: NatalFoundation): string {
  const point = POINT_NAMES[f.punto] ?? f.punto;
  if (f.tipo === "signo") return `${point} en ${f.signo}`;
  if (f.tipo === "casa") return `${point} en casa ${f.casa}`;
  return `${point} en ${ASPECT_NAMES[f.aspecto ?? ""] ?? f.aspecto} con ${POINT_NAMES[f.otro ?? ""] ?? f.otro}`;
}

function Dimension({ profileId, dimension }: { profileId: string; dimension: NatalDimension }) {
  const [synthesis, setSynthesis] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setSynthesis(null);
    setExpanded(false);
    setOpen(false);
    getNatalSynthesis(profileId, dimension.clave)
      .then((s) => setSynthesis(s.texto))
      .catch(() => setSynthesis(""));
  }, [profileId, dimension.clave]);

  return (
    <Card className="space-y-3">
      <div>
        <h2 className="text-lg font-medium text-gold-300">{dimension.nombre}</h2>
        <p className="text-sm text-slate-400">{dimension.pregunta}</p>
      </div>
      <p className={`text-sm leading-relaxed text-slate-200 ${expanded ? "" : "line-clamp-3"}`}>
        {synthesis === null ? "Leyendo tu carta…" : synthesis}
      </p>
      {synthesis && !expanded && (
        <button type="button" onClick={() => setExpanded(true)} className="text-sm text-violet-400">
          Leer más
        </button>
      )}
      {dimension.faltan_por_hora.length > 0 && (
        <p className="text-xs text-gold-300">Con tu hora exacta de nacimiento sumamos: {dimension.faltan_por_hora.join(", ")}.</p>
      )}
      <div className="flex justify-between text-sm">
        <button type="button" onClick={() => setOpen(!open)} className="text-violet-400">
          {open ? "Ocultar en qué se basa" : "En qué se basa →"}
        </button>
        <Link
          href={`/astrochat?q=${encodeURIComponent(`¿Qué más dice mi carta sobre ${dimension.nombre.toLowerCase()}?`)}`}
          className="text-violet-400"
        >
          Consultá sobre esto →
        </Link>
      </div>
      {open && (
        <div className="space-y-3 border-t border-slate-800 pt-3">
          <ul className="space-y-2">
            {dimension.fundamentos.map((f, i) => (
              <li key={i} className="text-sm">
                <span className="block text-slate-200">{label(f)}</span>
                <span className="block text-slate-400">{f.texto}</span>
              </li>
            ))}
          </ul>
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-wide text-slate-500">Para pensar</p>
            {dimension.preguntas.map((q) => (
              <p key={q} className="text-sm text-slate-300">
                {q}
              </p>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

// Compartir mi carta (spec A9): un toque; Destiny decide qué datos se muestran.
const SHARE_TEXT = "¿Por qué con algunas personas fluye y con otras no? Mirá mi carta en Destiny y descubrí la tuya:";

function ShareCard({ profileId }: { profileId: string }) {
  const [status, setStatus] = useState<ShareStatus | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getShare(profileId).then(setStatus).catch(() => null);
  }, [profileId]);

  async function share() {
    setBusy(true);
    try {
      const s = await createShare(profileId);
      setStatus(s);
      const url = `${window.location.origin}/c/${s.token}`;
      if (navigator.share) {
        await navigator.share({ title: "Mi carta en Destiny", text: SHARE_TEXT, url }).catch(() => null);
      } else {
        window.open(`https://wa.me/?text=${encodeURIComponent(`${SHARE_TEXT} ${url}`)}`, "_blank");
      }
    } finally {
      setBusy(false);
    }
  }

  // Arriba, debajo de la rueda: compartir es sobre toda la carta (pedido de German).
  return (
    <div className="space-y-1 text-center text-sm">
      <button type="button" onClick={share} disabled={busy} className="text-violet-400 disabled:opacity-60">
        Compartir mi carta →
      </button>
      <p className="text-xs text-slate-500">
        {status?.activo ? (
          <>
            Se vio {status.vistas} {status.vistas === 1 ? "vez" : "veces"} ·{" "}
            <button
              type="button"
              className="underline"
              onClick={async () => {
                await deleteShare(profileId);
                setStatus({ activo: false, vistas: 0 });
              }}
            >
              Dejar de compartir
            </button>
          </>
        ) : (
          "Se comparten tus signos y lecturas, nunca tu fecha, hora ni lugar de nacimiento."
        )}
      </p>
    </div>
  );
}

function MiCarta() {
  const profileId = useSessionProfileId();
  const [data, setData] = useState<NatalDimensions | null>(null);
  const [style, setStyle] = useState<Style | null>(null);
  const [personality, setPersonality] = useState<MyPersonality | null>(null);
  const [tab, setTab] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!profileId) return;
    getNatalDimensions(profileId)
      .then((d) => {
        setData(d);
        setTab(d.dimensiones[0]?.clave ?? null);
      })
      .catch(() => setError(true));
    getStyle(profileId).then(setStyle).catch(() => null);
    getMyPersonality(profileId).then(setPersonality).catch(() => null);
  }, [profileId]);

  if (error) return <p className="text-slate-400">No pudimos leer tu carta. Revisá tus datos de nacimiento.</p>;
  if (!profileId || !data) return <p className="text-slate-400">Cargando…</p>;
  const current = data.dimensiones.find((d) => d.clave === tab) ?? data.dimensiones[0];

  return (
    <>
      <PageTitle
        title="Mi carta"
        subtitle="Lo que dice tu carta natal sobre cuatro áreas de tu vida. Una lectura simbólica para pensarte, no una predicción."
      />
      {style && <SkyWheel cielo={style.cielo} leyenda={style.cielo_leyenda} />}
      <ShareCard profileId={profileId} />
      {data.aproximado && (
        <p className="text-xs text-gold-300">
          Sin tu hora exacta, la lectura es aproximada.{" "}
          <Link href={`/onboarding/datos-natales?profileId=${profileId}&editar=1`} className="underline">
            Cargar la hora
          </Link>
        </p>
      )}
      <div role="tablist" className="grid grid-cols-4 gap-1 rounded-xl bg-slate-900 p-1 ring-1 ring-slate-700">
        {data.dimensiones.map((d) => (
          <button
            key={d.clave}
            role="tab"
            aria-selected={d.clave === current.clave}
            type="button"
            onClick={() => setTab(d.clave)}
            className={`rounded-lg px-1 py-1.5 text-xs ${
              d.clave === current.clave ? "bg-violet-600 text-white" : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            {SHORT[d.clave] ?? d.nombre}
          </button>
        ))}
      </div>
      <Dimension profileId={profileId} dimension={current} />
      <AskBox
        title="Preguntá sobre tu carta"
        hint="¿Querés profundizar en algo de tu carta? Preguntá y te respondemos con ella."
        example="¿Qué dice mi carta sobre cómo me vinculo?"
      />
      <ListCard>
        <ListRow
          href="/perfil/test"
          icon="✓"
          title="Test de personalidad"
          detail={
            personality && personality.completed === personality.total_questions
              ? "Completo: suma tu compatibilidad de personalidad"
              : "32 preguntas: suma una compatibilidad de personalidad, aparte de la astrología"
          }
        />
      </ListCard>
    </>
  );
}

export default function MiCartaPage() {
  return (
    <Page>
      <Suspense>
        <MiCarta />
      </Suspense>
    </Page>
  );
}
