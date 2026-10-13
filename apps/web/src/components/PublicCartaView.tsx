"use client";

import Link from "next/link";
import { CSSProperties } from "react";
import { BACKGROUNDS } from "@/components/Backgrounds";
import { SkyWheel } from "@/components/BirthSky";
import type { PublicCarta } from "@/lib/api";

// La carta compartida (spec A9), con los colores, la tipografía y el fondo de quien
// la compartió. Las variables de color se definen en el contenedor, así no pisan
// el tema de quien la mira.
function themeVars(c: PublicCarta): CSSProperties {
  const vars: Record<string, string> = {
    "--font-display": c.tipografia === "clasica" ? "inherit" : `var(--font-${c.tipografia})`,
  };
  for (const [scale, steps] of Object.entries(c.paleta)) {
    for (const [step, hex] of Object.entries(steps)) {
      vars[`--${scale}-${step}`] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(" ");
    }
  }
  return { ...vars, backgroundColor: "rgb(var(--slate-950))" } as CSSProperties;
}

export default function PublicCartaView({ carta, signLine, hook }: { carta: PublicCarta; signLine: string; hook: string }) {
  const background = carta.fondo !== "ninguno" ? BACKGROUNDS[carta.fondo] ?? BACKGROUNDS.constelacion : null;
  return (
    <div style={themeVars(carta)} className="relative min-h-screen text-slate-100">
      {background && (
        <div aria-hidden className="pointer-events-none fixed inset-0 overflow-hidden">
          <background.Component cielo={carta.cielo} elementos={carta.elementos} />
        </div>
      )}
      <div className="relative mx-auto w-full max-w-md space-y-6 px-5 py-8">
        <header className="space-y-1 text-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="Destiny" width={56} height={56} className="mx-auto" />
          <h1 className="text-2xl font-semibold">La carta de {carta.nombre}</h1>
          <p className="text-sm text-gold-300">{signLine}</p>
        </header>
        <SkyWheel cielo={carta.cielo} />
        {carta.dimensiones.map((d) => (
          <section key={d.clave} className="space-y-1 rounded-xl bg-slate-900/80 p-4 ring-1 ring-slate-700 backdrop-blur">
            <h2 className="text-lg font-medium text-gold-300">{d.nombre}</h2>
            <p className="text-sm text-slate-400">{d.pregunta}</p>
            <p className="pt-1 text-sm leading-relaxed text-slate-200">{d.sintesis}</p>
          </section>
        ))}
        <section className="space-y-3 rounded-xl bg-slate-900/80 p-5 text-center ring-1 ring-gold-400/50 backdrop-blur">
          <p className="text-lg font-semibold">{hook}</p>
          <p className="text-sm text-slate-300">Descubrí tu carta y con quién resonás. Es gratis.</p>
          <Link href="/" className="block w-full rounded-md bg-violet-600 px-3 py-2.5 font-medium text-white">
            Descubrí tu carta
          </Link>
          <p className="text-xs text-slate-500">Una lectura simbólica para conocerte: no predice el futuro ni decide por vos.</p>
        </section>
      </div>
    </div>
  );
}
