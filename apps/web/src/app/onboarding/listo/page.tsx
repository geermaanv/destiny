"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { acceptInvitation, getInvitation, revealInvitation, startSession } from "@/lib/api";

// Fin del registro sin WhatsApp (spec A10): se inicia la sesión en este dispositivo y,
// si vino por una invitación, se resuelve igual que antes después de verificar.
// Si la verificación es obligatoria (interruptor prendido), se va a verificar.
function Listo() {
  const router = useRouter();
  const params = useSearchParams();
  const profileId = params.get("profileId");
  const ref = params.get("ref");
  const started = useRef(false);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reveal, setReveal] = useState<string | null>(null);
  const [invitedBy, setInvitedBy] = useState<{ name: string; matchId: string } | null>(null);
  const [connectFailed, setConnectFailed] = useState<string | null>(null);

  useEffect(() => {
    if (!profileId || started.current) return;
    started.current = true;
    startSession(profileId)
      .then(async (result) => {
        if (result === "verificacion") {
          const next = new URLSearchParams({ profileId });
          if (ref) next.set("ref", ref);
          router.replace(`/onboarding/verificacion?${next.toString()}`);
          return;
        }
        if (ref) {
          const inv = await getInvitation(ref).catch(() => null);
          if (inv?.kind === "test") {
            // Spec C13: si conectar falla, igual se entra a la app (antes quedaba en una pantalla de error).
            const accepted = await acceptInvitation(ref).catch(() => null);
            if (accepted) setInvitedBy({ name: inv.inviter_name ?? "quien te invitó", matchId: accepted.match_id });
            else setConnectFailed(inv.inviter_name ?? "quien te invitó");
          } else if (inv) {
            const r = await revealInvitation(ref, profileId).catch(() => null);
            if (r) setReveal(r.text);
          }
        }
        setReady(true);
      })
      .catch((e: Error) => setError(e.message));
  }, [profileId, ref, router]);

  if (!profileId) return <p className="text-slate-400">Falta el perfil. Volvé a empezar el registro.</p>;
  if (error) return <p className="text-slate-300">{error}</p>;
  if (!ready) return <p className="text-slate-400">Preparando tu cuenta…</p>;

  return (
    <div className="w-full max-w-sm space-y-5 text-center">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/logo.png" alt="" width={80} height={80} className="mx-auto" />
      <h1 className="text-2xl font-semibold">¡Listo!</h1>
      <p className="text-slate-300">Tu cuenta está creada. Ya podés ver tu día, tu carta y con quién fluye.</p>
      {reveal && <p className="rounded-xl bg-slate-900 p-3 text-sm text-gold-200 ring-1 ring-slate-700">{reveal}</p>}
      {invitedBy && (
        <div className="space-y-2 rounded-xl bg-slate-900 p-4 text-left ring-1 ring-slate-700">
          <p className="text-sm text-gold-200">
            Ya estás conectado con {invitedBy.name}. Completá tu test de personalidad para ver qué tan compatibles son.
          </p>
          <Link href="/perfil/test" className="block text-right text-sm text-violet-400">
            Hacer el test →
          </Link>
        </div>
      )}
      {connectFailed && (
        <p className="rounded-xl bg-slate-900 p-3 text-sm text-slate-300 ring-1 ring-slate-700">
          No pudimos conectarte con {connectFailed} en este momento. Podés encontrarle en Círculo.
        </p>
      )}
      <Link href="/home" className="block w-full rounded-md bg-violet-600 px-3 py-2.5 font-medium text-white">
        Entrar
      </Link>
      <p className="text-xs text-slate-500">
        Tu cuenta vive en este dispositivo. Cuando quieras, verificá tu WhatsApp desde tu perfil para no perderla y poder
        entrar desde otro celular.
      </p>
    </div>
  );
}

export default function ListoPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 text-slate-100">
      <Suspense>
        <Listo />
      </Suspense>
    </main>
  );
}
