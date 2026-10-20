"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import GenderPrefs from "@/components/GenderPrefs";
import PlaceField from "@/components/PlaceField";
import ProfileForm from "@/components/ProfileForm";
import { Card, Page, PageTitle, SectionTitle } from "@/components/ui";
import { getProfile, Place, Profile, setResidence } from "@/lib/api";
import { useSessionProfileId } from "@/lib/session";

// Spec B9: dónde vive, para la distancia en Descubrir. Nadie más ve la ciudad.
function Residence({ profile, onSaved }: { profile: Profile; onSaved: (p: Profile) => void }) {
  const [place, setPlace] = useState<Place | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  async function save() {
    if (!place) {
      setStatus("Elegí tu ciudad de la lista.");
      return;
    }
    try {
      onSaved(await setResidence(profile.id, place));
      setStatus("Guardado ✓");
    } catch {
      setStatus("No se pudo guardar. Probá de nuevo.");
    }
  }
  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-400">Dónde vivís</p>
      <PlaceField
        id="residence"
        placeholder="Tu ciudad (ej. Córdoba)"
        selected={place}
        initialText={profile.residence_label ?? ""}
        onSelect={(p) => setPlace(p)}
        onUnavailable={(u) => u && setStatus("El buscador de ciudades no responde. Probá en un rato.")}
      />
      <p className="text-xs text-slate-500">Para mostrar la distancia en Descubrir. Nadie ve tu ciudad, solo los kilómetros.</p>
      {status && <p className="text-sm text-gold-300">{status}</p>}
      <button
        type="button"
        onClick={save}
        className="w-full rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white"
      >
        Guardar ciudad
      </button>
    </div>
  );
}

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
          <Card>
            <Residence profile={profile} onSaved={setProfile} />
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
