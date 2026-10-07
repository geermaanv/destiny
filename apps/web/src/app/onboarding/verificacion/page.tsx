"use client";

import { Suspense, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { startVerification, VerificationResult } from "@/lib/api";

const STATUS_COPY: Record<string, string> = {
  verificado: "Identidad verificada. Ya podés acceder a descubrimiento.",
  rechazado: "No pudimos verificarte con esa foto/video. Probá de nuevo.",
  duplicado_detectado: "Detectamos este dispositivo en otra cuenta. Contactanos si es un error.",
  en_revision: "Estamos revisando tu verificación.",
};

function VerificacionForm() {
  const profileId = useSearchParams().get("profileId");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");
  const [result, setResult] = useState<VerificationResult | null>(null);

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
