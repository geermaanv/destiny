"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { claimSession, getLoginStatus, LoginStart, simulateWhatsappMessage, startLogin } from "@/lib/api";

// "Ya tengo cuenta" (spec A5): se entra mandando un código por WhatsApp desde
// el número con el que la persona se verificó. Mismo mecanismo que A3.
const POLL_MS = 3000;

export default function EntrarPage() {
  const router = useRouter();
  const [login, setLogin] = useState<LoginStart | null>(null);
  const [status, setStatus] = useState<"pendiente" | "sin_cuenta" | "vencido" | "error">("pendiente");
  const [devPhone, setDevPhone] = useState("");
  const started = useRef(false);

  const begin = useCallback(async () => {
    setStatus("pendiente");
    try {
      setLogin(await startLogin());
    } catch {
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    begin();
  }, [begin]);

  useEffect(() => {
    if (!login || status !== "pendiente") return;
    const id = setInterval(async () => {
      const s = await getLoginStatus(login.login_id).catch(() => null);
      if (s === "listo") {
        clearInterval(id);
        await claimSession(login.claim_token)
          .then(() => router.replace("/home"))
          .catch(() => setStatus("error"));
      } else if (s === "sin_cuenta" || s === "vencido") {
        setStatus(s);
      }
    }, POLL_MS);
    return () => clearInterval(id);
  }, [login, status, router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <div className="w-full max-w-sm space-y-5 text-center">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.png" alt="" width={72} height={72} className="mx-auto" />
        <h1 className="text-2xl font-semibold">Entrar a Destiny</h1>

        {status === "sin_cuenta" ? (
          <div className="space-y-3">
            <p className="text-slate-400">Ese número de WhatsApp todavía no tiene una cuenta en Destiny.</p>
            <Link href="/onboarding/datos-natales" className="block rounded-md bg-violet-600 px-3 py-2 font-medium text-white">
              Crear mi cuenta
            </Link>
          </div>
        ) : status === "vencido" || status === "error" ? (
          <div className="space-y-3">
            <p className="text-slate-400">
              {status === "vencido" ? "El código venció." : "No pudimos iniciar la sesión."}
            </p>
            <button onClick={begin} className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white">
              Generar un código nuevo
            </button>
          </div>
        ) : login ? (
          <div className="space-y-3">
            <p className="text-slate-400">Mandanos el código desde el WhatsApp con el que te registraste.</p>
            <a
              href={login.wa_link}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full rounded-md bg-emerald-600 px-3 py-2 font-medium text-white"
            >
              Entrar con WhatsApp
            </a>
            <p className="text-sm text-slate-400">
              Tu código es <span className="font-mono text-slate-200">{login.code}</span>. Esperando tu mensaje…
            </p>
            {login.mock && (
              <div className="space-y-2 rounded-md border border-dashed border-amber-700 p-3 text-left">
                <p className="text-xs font-medium text-amber-400">Modo desarrollo: WhatsApp no está configurado</p>
                <input
                  value={devPhone}
                  onChange={(e) => setDevPhone(e.target.value)}
                  placeholder="Número verificado (ej. 54911...)"
                  className="w-full rounded-md bg-slate-900 px-2 py-1 font-mono text-slate-100"
                />
                <button
                  onClick={() => simulateWhatsappMessage(devPhone, `Mi código Destiny: ${login.code}`)}
                  className="w-full rounded-md bg-amber-700 px-3 py-1.5 text-sm font-medium text-white"
                >
                  Simular envío (dev)
                </button>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Generando tu código…</p>
        )}

        <Link href="/" className="block text-sm text-slate-500 underline">
          Volver
        </Link>
      </div>
    </main>
  );
}
