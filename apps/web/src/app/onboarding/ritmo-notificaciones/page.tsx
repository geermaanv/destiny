"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import OnboardingSteps, { onboardingHref } from "@/components/OnboardingSteps";
import { NotificationRhythm, setNotificationPreference } from "@/lib/api";

const OPTIONS: { value: NotificationRhythm; title: string; description: string }[] = [
  {
    value: "ritmo_diario",
    title: "Ritmo Diario",
    description: "Un mensaje a la mañana con el pulso astrológico del día.",
  },
  {
    value: "pulso_cosmos",
    title: "Pulso del Cosmos",
    description: "Alertas en tiempo real cuando un tránsito exacto afecta tu carta.",
  },
];

function RitmoNotificacionesForm() {
  const router = useRouter();
  const params = useSearchParams();
  const profileId = params.get("profileId");
  const ref = params.get("ref");
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");

  async function choose(rhythm: NotificationRhythm) {
    if (!profileId) return;
    setStatus("submitting");
    try {
      await setNotificationPreference(profileId, rhythm);
      const next = new URLSearchParams({ profileId });
      if (ref) next.set("ref", ref);
      router.push(`/onboarding/verificacion?${next.toString()}`);
    } catch {
      setStatus("error");
    }
  }

  if (!profileId) {
    return <p className="text-slate-400">Falta el perfil. Volvé a empezar el onboarding.</p>;
  }

  return (
    <div className="w-full max-w-sm space-y-5">
      <OnboardingSteps step={3} backHref={onboardingHref("/onboarding/perfil", profileId, ref)} />
      <div>
        <h1 className="text-2xl font-semibold">¿Cómo querés que te avisemos?</h1>
        <p className="mt-1 text-sm text-slate-400">
          Destiny te va a mandar avisos sobre tu clima astrológico. Elegí con qué frecuencia. Las notificaciones
          todavía no están activas: por ahora guardamos tu preferencia y la podés cambiar después.
        </p>
      </div>
      <div className="space-y-3">
        {OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => choose(option.value)}
            disabled={status === "submitting"}
            className="w-full rounded-md bg-slate-900 p-4 text-left ring-1 ring-slate-700 hover:ring-violet-400 disabled:opacity-50"
          >
            <p className="font-medium">{option.title}</p>
            <p className="mt-1 text-sm text-slate-400">{option.description}</p>
          </button>
        ))}
      </div>
      {status === "error" && (
        <p className="text-sm text-red-400">No se pudo guardar tu elección. Probá de nuevo.</p>
      )}
    </div>
  );
}

export default function RitmoNotificacionesPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <Suspense>
        <RitmoNotificacionesForm />
      </Suspense>
    </main>
  );
}
