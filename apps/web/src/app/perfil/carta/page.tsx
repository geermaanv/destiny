"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import AppNav from "@/components/AppNav";
import { SkyWheel } from "@/components/BirthSky";
import { useSessionProfileId } from "@/lib/session";
import { getNatalDimensions, getNatalSynthesis, getStyle, NatalDimension, NatalDimensions, NatalFoundation, Style } from "@/lib/api";

// Nombres para mostrar los fundamentos (los textos vienen de la API).
const POINT_NAMES: Record<string, string> = {
  sol: "Sol", luna: "Luna", mercurio: "Mercurio", venus: "Venus", marte: "Marte", jupiter: "Júpiter",
  saturno: "Saturno", urano: "Urano", neptuno: "Neptuno", pluton: "Plutón", asc: "Ascendente",
  mc: "Medio Cielo", desc: "Descendente", ic: "Fondo de Cielo",
};
const ASPECT_NAMES: Record<string, string> = {
  conjuncion: "conjunción", sextil: "sextil", cuadratura: "cuadratura", trigono: "trígono", oposicion: "oposición",
};

function label(f: NatalFoundation): string {
  const point = POINT_NAMES[f.punto] ?? f.punto;
  if (f.tipo === "signo") return `${point} en ${f.signo}`;
  if (f.tipo === "casa") return `${point} en casa ${f.casa}`;
  return `${point} en ${ASPECT_NAMES[f.aspecto ?? ""] ?? f.aspecto} con ${POINT_NAMES[f.otro ?? ""] ?? f.otro}`;
}

function DimensionCard({ profileId, dimension }: { profileId: string; dimension: NatalDimension }) {
  const [synthesis, setSynthesis] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    getNatalSynthesis(profileId, dimension.clave)
      .then((s) => setSynthesis(s.texto))
      .catch(() => setSynthesis(""));
  }, [profileId, dimension.clave]);

  return (
    <section className="space-y-3 rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
      <div>
        <h2 className="font-medium text-gold-300">{dimension.nombre}</h2>
        <p className="text-sm text-slate-400">{dimension.pregunta}</p>
      </div>
      <p className="text-sm leading-relaxed text-slate-200">{synthesis === null ? "Leyendo tu carta…" : synthesis}</p>
      {dimension.faltan_por_hora.length > 0 && (
        <p className="text-xs text-gold-300">
          Con tu hora exacta de nacimiento sumamos: {dimension.faltan_por_hora.join(", ")}.
        </p>
      )}
      <button type="button" onClick={() => setOpen(!open)} className="text-sm text-violet-400">
        {open ? "Ocultar en qué se basa" : "En qué se basa →"}
      </button>
      {open && (
        <div className="space-y-3">
          <ul className="space-y-2">
            {dimension.fundamentos.map((f, i) => (
              <li key={i} className="text-sm">
                <span className="block text-slate-300">{label(f)}</span>
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
    </section>
  );
}

function MiCarta() {
  const profileId = useSessionProfileId();
  const [data, setData] = useState<NatalDimensions | null>(null);
  const [error, setError] = useState(false);
  const [style, setStyle] = useState<Style | null>(null);

  useEffect(() => {
    if (!profileId) return;
    getNatalDimensions(profileId).then(setData).catch(() => setError(true));
    getStyle(profileId).then(setStyle).catch(() => null);
  }, [profileId]);

  if (error) return <p className="text-slate-400">No pudimos leer tu carta. Revisá tus datos de nacimiento.</p>;
  if (!profileId || !data) return <p className="text-slate-400">Cargando…</p>;

  return (
    <div className="w-full max-w-sm space-y-4">
      <div className="space-y-1">
        <Link href="/perfil" className="text-sm text-slate-400">
          ← Mi perfil
        </Link>
        <h1 className="text-2xl font-semibold">Mi carta</h1>
        <p className="text-sm text-slate-400">
          Lo que dice tu carta natal sobre cuatro áreas de tu vida. Es una lectura simbólica para pensarte, no una
          predicción.
        </p>
        {data.aproximado && (
          <p className="text-xs text-gold-300">
            Sin tu hora exacta, la lectura es aproximada.{" "}
            <Link href={`/onboarding/datos-natales?profileId=${profileId}&editar=1`} className="underline">
              Cargar la hora
            </Link>
          </p>
        )}
      </div>
      {style && <SkyWheel cielo={style.cielo} leyenda={style.cielo_leyenda} />}
      {data.dimensiones.map((d) => (
        <DimensionCard key={d.clave} profileId={profileId} dimension={d} />
      ))}
    </div>
  );
}

export default function MiCartaPage() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <MiCarta />
      </Suspense>
      <AppNav />
    </main>
  );
}
