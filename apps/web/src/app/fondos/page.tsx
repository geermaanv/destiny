"use client";

import { useEffect, useState } from "react";
import { BACKGROUNDS } from "@/components/Backgrounds";
import { getMe, getStyle, Style } from "@/lib/api";

// Página de prueba para elegir el fondo (spec X2 v3): las 4 variantes con la carta
// de la persona con sesión y una tarjeta de ejemplo encima.
export default function FondosPage() {
  const [style, setStyle] = useState<Style | null>(null);
  useEffect(() => {
    getMe()
      .then((me) => (me ? getStyle(me.id) : null))
      .then(setStyle)
      .catch(() => null);
  }, []);
  if (!style) return <main className="p-6 text-slate-400">Cargando…</main>;

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-slate-100">
      <h1 className="mb-4 text-xl font-semibold">Fondos posibles</h1>
      <div className="flex flex-wrap gap-6">
        {Object.entries(BACKGROUNDS).map(([key, { label, Component }]) => (
          <figure key={key} className="space-y-2">
            <div className="relative h-[420px] w-[220px] overflow-hidden rounded-2xl bg-slate-950 ring-1 ring-slate-800">
              <Component cielo={style.cielo} elementos={style.elementos} />
              <div className="relative space-y-3 p-4">
                <p className="text-lg font-semibold">Tu Momento</p>
                <div className="rounded-md bg-slate-900 p-3 ring-1 ring-slate-700">
                  <p className="text-xs text-slate-400">TU DÍA</p>
                  <p className="text-sm text-gold-300">Intensidad serena</p>
                  <p className="text-xs text-slate-300">Hoy la Luna te invita a bucear en tus emociones.</p>
                </div>
                <div className="rounded-md bg-slate-900 p-3 ring-1 ring-slate-700">
                  <p className="text-sm">En tu frecuencia</p>
                </div>
              </div>
            </div>
            <figcaption className="text-sm text-slate-300">{label}</figcaption>
          </figure>
        ))}
      </div>
    </main>
  );
}
