"use client";

import { Suspense, useState } from "react";
import { useRouter } from "next/navigation";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import ProfileForm from "@/components/ProfileForm";
import { logout } from "@/lib/api";

// "Mi perfil": editar el perfil liviano después del onboarding (spec A4).
function MiPerfil() {
  const router = useRouter();
  const profileId = useSessionProfileId();
  const [saved, setSaved] = useState(false);

  if (!profileId) {
    return <p className="text-slate-400">Cargando…</p>;
  }

  return (
    <div className="w-full max-w-sm space-y-6">
      <h1 className="text-2xl font-semibold">Mi perfil</h1>
      <ProfileForm profileId={profileId} submitLabel="Guardar cambios" onSaved={() => setSaved(true)} />
      {saved && <p className="text-center text-sm text-emerald-400">Perfil guardado.</p>}
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
