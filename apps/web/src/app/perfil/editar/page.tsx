"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import GenderPrefs from "@/components/GenderPrefs";
import ProfileForm from "@/components/ProfileForm";
import { Card, Page, PageTitle, SectionTitle } from "@/components/ui";
import { getProfile, Profile } from "@/lib/api";
import { useSessionProfileId } from "@/lib/session";

// Editar el perfil liviano (spec A4), como pantalla propia desde Perfil (spec U1-B).
function Editar() {
  const router = useRouter();
  const profileId = useSessionProfileId();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [prefsSaved, setPrefsSaved] = useState(false);
  useEffect(() => {
    if (profileId) getProfile(profileId).then(setProfile).catch(() => null);
  }, [profileId]);
  if (!profileId) return <p className="text-slate-400">Cargando…</p>;
  return (
    <>
      <PageTitle title="Editar perfil" back={{ href: "/perfil", label: "Mi perfil" }} />
      <ProfileForm profileId={profileId} submitLabel="Guardar cambios" onSaved={() => router.push("/perfil")} />
      {/* Spec B8: género y "Mostrame", guardado aparte del formulario de arriba. */}
      {profile && (
        <div className="max-w-sm space-y-3">
          <SectionTitle>Descubrir</SectionTitle>
          <Card>
            <GenderPrefs
              profile={profile}
              submitLabel={prefsSaved ? "Guardado ✓" : "Guardar"}
              onSaved={(p) => {
                setProfile(p);
                setPrefsSaved(true);
                setTimeout(() => setPrefsSaved(false), 2500);
              }}
            />
          </Card>
        </div>
      )}
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
