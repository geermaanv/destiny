"use client";

import { Suspense } from "react";
import { useRouter } from "next/navigation";
import ProfileForm from "@/components/ProfileForm";
import { Page, PageTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";

// Editar el perfil liviano (spec A4), como pantalla propia desde Perfil (spec U1-B).
function Editar() {
  const router = useRouter();
  const profileId = useSessionProfileId();
  if (!profileId) return <p className="text-slate-400">Cargando…</p>;
  return (
    <>
      <PageTitle title="Editar perfil" back={{ href: "/perfil", label: "Mi perfil" }} />
      <ProfileForm profileId={profileId} submitLabel="Guardar cambios" onSaved={() => router.push("/perfil")} />
    </>
  );
}

export default function EditarPage() {
  return (
    <Page>
      <Suspense>
        <Editar />
      </Suspense>
    </Page>
  );
}
