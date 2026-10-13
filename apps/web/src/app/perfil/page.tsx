"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import ProfileForm from "@/components/ProfileForm";
import StyleCard from "@/components/StyleCard";
import { getMyPersonality, getProfile, logout, MyPersonality, Profile } from "@/lib/api";

// "Mi perfil": editar el perfil liviano después del onboarding (spec A4).
function MiPerfil() {
  const router = useRouter();
  const profileId = useSessionProfileId();
  const [personality, setPersonality] = useState<MyPersonality | null>(null);
  const [me, setMe] = useState<Profile | null>(null);

  useEffect(() => {
    if (!profileId) return;
    getMyPersonality(profileId).then(setPersonality).catch(() => null);
    getProfile(profileId).then(setMe).catch(() => null);
  }, [profileId]);

  if (!profileId) {
    return <p className="text-slate-400">Cargando…</p>;
  }

  return (
    <div className="w-full max-w-sm space-y-6">
      <h1 className="text-2xl font-semibold">Mi perfil</h1>
      <Link href="/perfil/test" className="block space-y-2 rounded-md bg-slate-900 p-4 ring-1 ring-gold-400/40 hover:ring-gold-400">
        <span className="flex items-center justify-between">
          <span className="font-medium text-gold-300">Test de personalidad</span>
          <span className="text-xs text-slate-400">
            {personality ? `${personality.completed}/${personality.total_questions}` : "…"}
          </span>
        </span>
        <span className="block text-sm text-slate-400">
          32 preguntas sobre atracción, afecto, comunicación y compromiso. Suma una compatibilidad de personalidad,
          aparte de la astrología. Tus respuestas no las ve nadie.
        </span>
        {personality && (
          <span className="block h-1 overflow-hidden rounded-full bg-slate-800">
            <span
              className="block h-full bg-gold-400"
              style={{ width: `${(personality.completed * 100) / personality.total_questions}%` }}
            />
          </span>
        )}
        <span className="block text-sm text-violet-400">
          {!personality || personality.completed === 0
            ? "Empezar →"
            : personality.completed < personality.total_questions
              ? "Continuar →"
              : "Ver o cambiar respuestas →"}
        </span>
      </Link>
      {me && (
        <div className="space-y-2 rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
          <div className="flex items-center justify-between">
            <span className="font-medium">Mis datos de nacimiento</span>
            <Link href={`/onboarding/datos-natales?profileId=${profileId}&editar=1`} className="text-sm text-violet-400">
              Editar
            </Link>
          </div>
          <p className="text-sm text-slate-300">
            {me.birth_date ? me.birth_date.split("-").reverse().join("/") : "—"} ·{" "}
            {me.birth_time_estimated ? `hora estimada (${me.birth_time?.slice(0, 5)})` : `${me.birth_time?.slice(0, 5)} hs`}
          </p>
          <p className="text-sm text-slate-300">{me.birth_place_query ?? "—"}</p>
          {me.sun_sign && <p className="text-xs text-slate-400">Sol en {me.sun_sign}</p>}
          {me.birth_place_lat === null && (
            <p className="text-xs text-gold-300">
              Tu ciudad no está elegida del buscador: no podemos calcular tu Ascendente ni tus casas. Tocá Editar y elegila
              de la lista.
            </p>
          )}
        </div>
      )}
      {me?.birth_date && <StyleCard profileId={profileId} />}
      <ProfileForm profileId={profileId} submitLabel="Guardar cambios" onSaved={() => null} />
      <button
        onClick={async () => {
          await logout();
          router.replace("/");
        }}
        className="w-full text-center text-sm text-slate-500 underline"
      >
        Cerrar sesión
      </button>
    </div>
  );
}

export default function PerfilPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <MiPerfil />
      </Suspense>
      <AppNav />
    </main>
  );
}
