"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { SkyWheel } from "@/components/BirthSky";
import { onboardingHref } from "@/components/OnboardingSteps";
import { getNatalDimensions, getNatalSynthesis, NatalDimensions } from "@/lib/api";

// "Tu carta" en el registro (spec A8 v2): el momento wow antes de pedir el resto.
// Muestra la rueda y la lectura de Identidad; las otras áreas, al terminar.
function TuCarta() {
  const router = useRouter();
  const params = useSearchParams();
  const profileId = params.get("profileId");
  const ref = params.get("ref");
  const [data, setData] = useState<NatalDimensions | null>(null);
  const [synthesis, setSynthesis] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!profileId) return;
    getNatalDimensions(profileId).then(setData).catch(() => setError(true));
    getNatalSynthesis(profileId, "identidad")
      .then((s) => setSynthesis(s.texto))
      .catch(() => setSynthesis(""));
  }, [profileId]);

  const next = () => router.push(onboardingHref("/onboarding/perfil", profileId, ref));

  if (!profileId || error) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-slate-400">No pudimos leer tu carta. Sigamos con el registro.</p>
        {profileId && (
          <button type="button" onClick={next} className="w-full rounded-md bg-violet-600 px-3 py-2.5 font-medium text-white">
            Continuar
          </button>
        )}
      </div>
    );
  }
  if (!data) return <p className="text-slate-400">Leyendo tu cielo…</p>;

  const identidad = data.dimensiones.find((d) => d.clave === "identidad");
  const others = data.dimensiones.filter((d) => d.clave !== "identidad");

  return (
    <div className="w-full max-w-sm space-y-6">
      <div className="space-y-1 text-center">
        <p className="text-xs uppercase tracking-wide text-gold-300">Así estaba el cielo cuando naciste</p>
        <h1 className="text-2xl font-semibold">Tu carta</h1>
      </div>
      <SkyWheel cielo={data.cielo} />
      {identidad && (
        <section className="space-y-2 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/50">
          <h2 className="text-lg font-medium text-gold-300">{identidad.nombre}</h2>
          <p className="text-sm text-slate-400">{identidad.pregunta}</p>
          <p className="text-sm leading-relaxed text-slate-200">{synthesis ?? "Leyendo tu carta…"}</p>
        </section>
      )}
      <section className="space-y-2 rounded-xl bg-slate-900 p-4 ring-1 ring-slate-700">
        <p className="text-sm text-slate-300">
          Terminá tu registro y ves el resto: {others.map((d) => d.nombre.toLowerCase()).join(", ")}. Y con quién resonás.
        </p>
      </section>
      {data.aproximado && (
        <p className="text-xs text-gold-300">Sin tu hora exacta, la lectura es aproximada. La podés cargar después desde tu perfil.</p>
      )}
      <button type="button" onClick={next} className="w-full rounded-md bg-violet-600 px-3 py-2.5 font-medium text-white">
        Seguir: armá tu perfil
      </button>
      <p className="text-center text-xs text-slate-500">Una lectura simbólica para conocerte: no predice el futuro ni decide por vos.</p>
    </div>
  );
}

export default function TuCartaPage() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-slate-950 px-5 py-10 text-slate-100">
      <Suspense>
        <TuCarta />
      </Suspense>
    </main>
  );
}
