"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import ProfileForm from "@/components/ProfileForm";

// Paso del onboarding entre datos natales y ritmo (spec A4).
function PerfilStep() {
  const router = useRouter();
  const params = useSearchParams();
  const profileId = params.get("profileId");
  const ref = params.get("ref");

  if (!profileId) {
    return <p className="text-slate-400">Falta el perfil. Volvé a empezar el onboarding.</p>;
  }

  function next() {
    const nextParams = new URLSearchParams({ profileId: profileId! });
    if (ref) nextParams.set("ref", ref);
    router.push(`/onboarding/ritmo-notificaciones?${nextParams.toString()}`);
  }

  return (
    <div className="w-full max-w-sm space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Tu perfil</h1>
        <p className="mt-1 text-sm text-slate-400">
          Lo que van a ver los demás. Solo el nombre es obligatorio; el resto lo podés completar después.
        </p>
      </div>
      <ProfileForm profileId={profileId} submitLabel="Continuar" onSaved={next} />
    </div>
  );
}

export default function OnboardingPerfilPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 text-slate-100">
      <Suspense>
        <PerfilStep />
      </Suspense>
    </main>
  );
}
