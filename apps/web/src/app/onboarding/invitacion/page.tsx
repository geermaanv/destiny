"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getInvitation, InvitationPreload } from "@/lib/api";

function InvitacionContent() {
  const router = useRouter();
  const ref = useSearchParams().get("ref");
  const [invitation, setInvitation] = useState<InvitationPreload | null>(null);

  useEffect(() => {
    if (!ref) return;
    getInvitation(ref).then(setInvitation);
  }, [ref]);

  if (!ref) return <p className="text-slate-400">Link de invitación inválido.</p>;

  return (
    <div className="w-full max-w-sm space-y-5 text-center">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/logo.png" alt="Destiny" width={96} height={96} className="mx-auto" />
      <h1 className="text-2xl font-semibold">
        {invitation?.inviter_name ? `${invitation.inviter_name} te invitó a Destiny` : "Te invitaron a Destiny"}
      </h1>
      <p className="text-slate-300">{invitation?.teaser ?? "Cargando..."}</p>
      {invitation?.kind === "test" && (
        <p className="text-sm text-slate-400">
          Primero creás tu cuenta (tus datos de nacimiento y una verificación por WhatsApp). Después quedan conectados y
          hacés el test.
        </p>
      )}
      <button
        onClick={() => router.push(`/onboarding/datos-natales?ref=${ref}`)}
        className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white"
      >
        {invitation?.kind === "test" ? "Crear mi cuenta" : "Completar mi carta y ver la revelación"}
      </button>
    </div>
  );
}

export default function InvitacionPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <Suspense>
        <InvitacionContent />
      </Suspense>
    </main>
  );
}
