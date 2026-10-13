"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getMe } from "@/lib/api";

// Pantalla de inicio (spec A5): con sesión va directo a Home; sin sesión,
// "Empezar" (registro) o "Ya tengo cuenta" (login por WhatsApp).
export default function Landing() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    getMe()
      .then((me) => (me ? router.replace("/home") : setChecking(false)))
      .catch(() => setChecking(false));
  }, [router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <div className="w-full max-w-sm space-y-8 text-center">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.png" alt="Destiny" width={110} height={110} className="mx-auto" />
        {/* Gancho elegido por German (análisis de competencia, 2026-10-13): une autoconocimiento y vínculos. */}
        <div className="space-y-3">
          <h1 className="text-3xl font-semibold leading-tight">¿Por qué con algunas personas fluye y con otras no?</h1>
          <p className="text-slate-300">
            Destiny lee tu carta natal para entenderte a vos y a tus vínculos: quién sos, cómo amás y con quién resonás.
          </p>
          <p className="text-xs text-slate-500">No predice el futuro ni decide por vos. Es una lectura para conocerte.</p>
        </div>
        {!checking && (
          <div className="space-y-3">
            <Link
              href="/onboarding/datos-natales"
              className="block w-full rounded-md bg-violet-600 px-3 py-2.5 font-medium text-white"
            >
              Descubrilo gratis
            </Link>
            <Link href="/entrar" className="block w-full rounded-md px-3 py-2.5 text-gold-300 ring-1 ring-slate-700">
              Ya tengo cuenta
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
