"use client";

import { Suspense } from "react";
import StyleCard from "@/components/StyleCard";
import { Page, PageTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";

// Tu estilo (spec X2), como pantalla propia desde Perfil (spec U1-B).
function Estilo() {
  const profileId = useSessionProfileId();
  if (!profileId) return <p className="text-slate-400">Cargando…</p>;
  return (
    <>
      <PageTitle
        title="Tu estilo"
        subtitle="Cómo te hablamos y cómo se ve la app: sale de tu carta y lo podés cambiar."
        back={{ href: "/perfil", label: "Perfil" }}
      />
      <StyleCard profileId={profileId} />
    </>
  );
}

export default function EstiloPage() {
  return (
    <Page>
      <Suspense>
        <Estilo />
      </Suspense>
    </Page>
  );
}
