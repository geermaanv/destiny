"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import AskBox from "@/components/AskBox";
import { SkyWheel } from "@/components/BirthSky";
import { Card, ListCard, ListRow, Page, PageTitle, segmentClass, SEGMENTS } from "@/components/ui";
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
  SUN_SIGNS as SIGNS,
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
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setSynthesis(null);
    setOpen(false);
    getNatalSynthesis(profileId, dimension.clave)
      .then((s) => setSynthesis(s.texto))
      .catch(() => setSynthesis(""));
  }, [profileId, dimension.clave]);

  // Texto completo (una área por vez), y "En qué se basa" como link discreto: es la
  // trazabilidad que distingue a Destiny de un horóscopo genérico.
  return (
    <Card className="space-y-3">
      <div>
        <h2 className="text-lg font-medium text-gold-300">{dimension.nombre}</h2>
        <p className="text-sm text-slate-400">{dimension.pregunta}</p>
      </div>
      <p className="text-sm leading-relaxed text-slate-200">{synthesis === null ? "Leyendo tu carta…" : synthesis}</p>
      {dimension.faltan_por_hora.length > 0 && (
        <p className="text-xs text-gold-300">Con tu hora exacta de nacimiento sumamos: {dimension.faltan_por_hora.join(", ")}.</p>
      )}
      <div className="text-right text-sm">
        <button type="button" onClick={() => setOpen(!open)} className="text-violet-400">
          {open ? "Ocultar en qué se basa" : "En qué se basa →"}
        </button>
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

// Tu cielo como una pestaña más (pedido de German): la rueda más chica y tus signos explicados.
function Cielo({ style }: { style: Style }) {
  const sign = (p: string) => {
    const lon = style.cielo.find((c) => c.punto === p)?.lon;
    return lon === undefined ? null : SIGNS[Math.floor(lon / 30) % 12];
  };
  const rows = [
    { glyph: "☉", name: "Sol", sign: sign("sol"), means: "tu esencia, lo que te mueve" },
    { glyph: "☽", name: "Luna", sign: sign("luna"), means: "tus emociones y lo que te da seguridad" },
    { glyph: "AC", name: "Ascendente", sign: sign("asc"), means: "cómo te mostrás y te ven" },
  ].filter((r) => r.sign);
  return (
    <Card className="space-y-4">
      <p className="text-sm text-slate-400">Así estaba el cielo cuando naciste.</p>
      <SkyWheel cielo={style.cielo} compact />
      <ul className="space-y-2">
        {rows.map((r) => (
          <li key={r.name} className="flex gap-3 text-sm">
            <span className="w-6 text-center text-gold-300">{r.glyph + "\uFE0E"}</span>
            <span>
              <span className="block text-slate-100">
                {r.name} en {r.sign}
              </span>
              <span className="block text-xs text-slate-400">{r.means}</span>
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

// Compartir mi carta (spec A9): un toque; Destiny decide qué datos se muestran.
// Va arriba a la derecha, junto al título (pedido de German).
const SHARE_TEXT = "¿Por qué con algunas personas fluye y con otras no? Mirá mi carta en Destiny y descubrí la tuya:";

function useShare(profileId: string | null) {
  const [status, setStatus] = useState<ShareStatus | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (profileId) getShare(profileId).then(setStatus).catch(() => null);
  }, [profileId]);

  async function share() {
    if (!profileId) return;
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

  async function stop() {
    if (!profileId) return;
    await deleteShare(profileId);
    setStatus({ activo: false, vistas: 0 });
  }

  return { status, busy, share, stop };
}

function MiCarta() {
  const profileId = useSessionProfileId();
  const [data, setData] = useState<NatalDimensions | null>(null);
  const [style, setStyle] = useState<Style | null>(null);
  const [personality, setPersonality] = useState<MyPersonality | null>(null);
  const [tab, setTab] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const shared = useShare(profileId);

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

  const tabs = [...data.dimensiones.map((d) => ({ clave: d.clave, label: SHORT[d.clave] ?? d.nombre })), { clave: "cielo", label: "Cielo" }];

  return (
    <>
      <PageTitle
        title="Mi carta"
        subtitle="Lo que dice tu carta natal sobre cuatro áreas de tu vida: una lectura simbólica para pensarte, no una predicción. Si la compartís, se ven solo tus signos y lecturas, nunca tu fecha, hora ni lugar de nacimiento."
        action={
          <button type="button" onClick={shared.share} disabled={shared.busy} className="text-violet-400 disabled:opacity-60">
            Compartir →
          </button>
        }
      />
      {/* Si ya compartiste: vistas y dejar de compartir (qué se comparte va en el subtítulo). */}
      {shared.status?.activo && (
        <p className="-mt-3 text-right text-xs text-slate-500">
          Tu carta se vio {shared.status.vistas} {shared.status.vistas === 1 ? "vez" : "veces"} ·{" "}
          <button type="button" className="underline" onClick={shared.stop}>
            Dejar de compartir
          </button>
        </p>
      )}
      {data.aproximado && (
        <p className="text-xs text-gold-300">
          Sin tu hora exacta, la lectura es aproximada.{" "}
          <Link href={`/onboarding/datos-natales?profileId=${profileId}&editar=1`} className="underline">
            Cargar la hora
          </Link>
        </p>
      )}
      <div role="tablist" className={`${SEGMENTS} grid-cols-5`}>
        {tabs.map((t) => (
          <button
            key={t.clave}
            role="tab"
            aria-selected={t.clave === tab}
            type="button"
            onClick={() => setTab(t.clave)}
            className={segmentClass(t.clave === tab)}
          >
            {t.label}
          </button>
        ))}
      </div>
      {tab === "cielo" ? style && <Cielo style={style} /> : <Dimension profileId={profileId} dimension={current} />}
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
