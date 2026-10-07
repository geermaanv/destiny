"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  getVerification,
  revealInvitation,
  simulateWhatsappMessage,
  startWhatsappVerification,
  VerificationResult,
  WhatsappCode,
} from "@/lib/api";

// v1: verificación por WhatsApp "al revés" (spec A3, ADR 0008). La captura de
// selfie/video en vivo vuelve en v2, sobre el mismo adapter de KYC.

const POLL_MS = 3000;

const STATUS_COPY: Record<string, string> = {
  verificado: "Número verificado. Ya podés acceder a descubrimiento.",
  duplicado_detectado: "Ese número de WhatsApp ya está asociado a otra cuenta. Probá con otro número o contactanos si es un error.",
};

function randomDevPhone(): string {
  return `54911${Math.floor(10_000_000 + Math.random() * 90_000_000)}`;
}

function VerificacionForm() {
  const params = useSearchParams();
  const profileId = params.get("profileId");
  const ref = params.get("ref");
  const [code, setCode] = useState<WhatsappCode | null>(null);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [expired, setExpired] = useState(false);
  const [error, setError] = useState(false);
  const [reveal, setReveal] = useState<string | null>(null);
  const [devPhone, setDevPhone] = useState(randomDevPhone);
  // Evita pedir dos códigos al montar (React StrictMode corre los effects dos
  // veces en dev, y el segundo código invalidaría al que se muestra).
  const started = useRef(false);

  const requestCode = useCallback(async () => {
    if (!profileId) return;
    setError(false);
    setExpired(false);
    setResult(null);
    try {
      setCode(await startWhatsappVerification(profileId));
    } catch {
      setError(true);
    }
  }, [profileId]);

  // Al entrar: si ya está verificado se muestra el resultado; si no, se pide código.
  useEffect(() => {
    if (!profileId || started.current) return;
    started.current = true;
    getVerification(profileId)
      .then((v) => (v.status === "verificado" ? setResult(v) : requestCode()))
      .catch(() => setError(true));
  }, [profileId, requestCode]);

  // Polling mientras se espera el mensaje de WhatsApp.
  useEffect(() => {
    if (!profileId || !code || result || expired) return;
    const id = setInterval(async () => {
      if (new Date(code.expires_at) <= new Date()) {
        setExpired(true);
        return;
      }
      const v = await getVerification(profileId).catch(() => null);
      if (v && (v.status === "verificado" || v.status === "duplicado_detectado")) setResult(v);
    }, POLL_MS);
    return () => clearInterval(id);
  }, [profileId, code, result, expired]);

  useEffect(() => {
    if (result?.status === "verificado" && ref && profileId) {
      revealInvitation(ref, profileId).then((r) => setReveal(r.text));
    }
  }, [result, ref, profileId]);

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
        {result.status === "duplicado_detectado" && (
          <button onClick={requestCode} className="text-violet-400 underline">
            Probar con otro número
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="w-full max-w-sm space-y-5 text-center">
      <h1 className="text-2xl font-semibold">Verificá tu identidad</h1>
      <p className="text-slate-400">
        Mandanos un mensaje por WhatsApp para confirmar que sos una persona real. Es obligatorio antes de acceder a
        descubrimiento.
      </p>
      <p className="text-xs text-slate-500">
        Usamos tu número solo para verificarte y evitar cuentas duplicadas. Nunca se lo mostramos a otros usuarios.
      </p>

      {error && <p className="text-sm text-red-400">No se pudo generar el código. Probá de nuevo.</p>}

      {expired ? (
        <div className="space-y-3">
          <p className="text-sm text-slate-400">El código venció.</p>
          <button onClick={requestCode} className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white">
            Generar un código nuevo
          </button>
        </div>
      ) : code ? (
        <div className="space-y-3">
          <a
            href={code.wa_link}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full rounded-md bg-emerald-600 px-3 py-2 font-medium text-white"
          >
            Verificar con WhatsApp
          </a>
          <p className="text-sm text-slate-400">
            Se abre WhatsApp con el mensaje listo: solo tocá enviar. Tu código es{" "}
            <span className="font-mono text-slate-200">{code.code}</span>.
          </p>
          <p className="text-xs text-slate-500">Esperando tu mensaje…</p>
        </div>
      ) : (
        !error && <p className="text-sm text-slate-500">Generando tu código…</p>
      )}

      {code?.mock && !expired && (
        <div className="space-y-2 rounded-md border border-dashed border-amber-700 p-3 text-left">
          <p className="text-xs font-medium text-amber-400">Modo desarrollo: WhatsApp no está configurado</p>
          <label className="block text-xs text-slate-400">
            Número desde el que se simula el envío
            <input
              value={devPhone}
              onChange={(e) => setDevPhone(e.target.value)}
              className="mt-1 w-full rounded-md bg-slate-900 px-2 py-1 font-mono text-slate-100"
            />
          </label>
          <button
            onClick={() => simulateWhatsappMessage(devPhone, `Mi código Destiny: ${code.code}`)}
            className="w-full rounded-md bg-amber-700 px-3 py-1.5 text-sm font-medium text-white"
          >
            Simular envío (dev)
          </button>
        </div>
      )}
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
