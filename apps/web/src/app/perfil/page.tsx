"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import AppNav from "@/components/AppNav";
import ProfileForm from "@/components/ProfileForm";

// "Mi perfil": editar el perfil liviano después del onboarding (spec A4).
function MiPerfil() {
  const profileId = useSearchParams().get("profileId");
  const [saved, setSaved] = useState(false);

  if (!profileId) {
    return <p className="text-slate-400">Falta el perfil.</p>;
  }

  return (
    <div className="w-full max-w-sm space-y-6">
      <h1 className="text-2xl font-semibold">Mi perfil</h1>
      <ProfileForm profileId={profileId} submitLabel="Guardar cambios" onSaved={() => setSaved(true)} />
      {saved && <p className="text-center text-sm text-emerald-400">Perfil guardado.</p>}
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
