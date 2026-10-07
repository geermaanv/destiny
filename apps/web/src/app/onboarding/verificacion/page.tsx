"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { revealInvitation, startVerification, VerificationResult } from "@/lib/api";

const STATUS_COPY: Record<string, string> = {
  verificado: "Identidad verificada. Ya podés acceder a descubrimiento.",
  rechazado: "No pudimos verificarte con esa foto/video. Probá de nuevo.",
  duplicado_detectado: "Detectamos este dispositivo en otra cuenta. Contactanos si es un error.",
  en_revision: "Estamos revisando tu verificación.",
};

function VerificacionForm() {
  const params = useSearchParams();
  const profileId = params.get("profileId");
  const ref = params.get("ref");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [reveal, setReveal] = useState<string | null>(null);

  useEffect(() => {
    if (result?.status === "verificado" && ref && profileId) {
      revealInvitation(ref, profileId).then((r) => setReveal(r.text));
    }
  }, [result, ref, profileId]);

  async function handleFile(file: File) {
    if (!profileId) return;
    setStatus("submitting");
    try {
      const res = await startVerification(profileId, file);
      setResult(res);
      setStatus("idle");
    } catch {
      setStatus("error");
    }
  }

  if (!profileId) {
    return <p className="text-slate-400">Falta el perfil. Volvé a empezar el onboarding.</p>;
  }

  if (result) {
    return (
      <div className="w-full max-w-sm space-y-3 text-center">
        <h1 className="text-2xl font-semibold capitalize">{result.status.replace("_", " ")}</h1>
        <p className="text-slate-400">{STATUS_COPY[result.status] ?? ""}</p>
        {reveal && <p className="rounded-md bg-violet-950 p-3 text-sm text-violet-200">{reveal}</p>}
        {result.status === "verificado" && (
          <a href={`/home?profileId=${profileId}`} className="inline-block text-violet-400 underline">
            Ir a Tu Momento
          </a>
        )}
      </div>
    );
  }

  return (
    <div className="w-full max-w-sm space-y-5 text-center">
      <h1 className="text-2xl font-semibold">Verificá tu identidad</h1>
      <p className="text-slate-400">Selfie o video en vivo. Es obligatorio antes de acceder a descubrimiento.</p>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*,video/*"
        capture="user"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={status === "submitting"}
        className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white disabled:opacity-50"
      >
        {status === "submitting" ? "Verificando..." : "Tomar selfie / video"}
      </button>
      {status === "error" && <p className="text-sm text-red-400">No se pudo verificar. Probá de nuevo.</p>}
    </div>
  );
}

export default function VerificacionPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <Suspense>
        <VerificacionForm />
      </Suspense>
    </main>
  );
}
