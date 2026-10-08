"use client";

import { Suspense, useEffect, useState } from "react";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import Link from "next/link";
import { getConnections, getFrequencyCount, getTodayAstroWeather, Mood, submitMoodCheckin } from "@/lib/api";

const MOODS: { value: Mood; label: string }[] = [
  { value: "energico", label: "Enérgico" },
  { value: "tranquilo", label: "Tranquilo" },
  { value: "reflexivo", label: "Reflexivo" },
  { value: "ansioso", label: "Ansioso" },
  { value: "inspirado", label: "Inspirado" },
];

function HomeContent() {
  const profileId = useSessionProfileId();
  const [astroWeather, setAstroWeather] = useState<string | null>(null);
  const [frequencyCount, setFrequencyCount] = useState<number | null>(null);
  const [selectedMood, setSelectedMood] = useState<Mood | null>(null);

  useEffect(() => {
    getTodayAstroWeather().then((r) => setAstroWeather(r.astro_weather));
  }, []);

  const [pendingRequests, setPendingRequests] = useState(0);

  useEffect(() => {
    if (!profileId) return;
    getFrequencyCount(profileId).then((r) => setFrequencyCount(r.count));
    getConnections(profileId)
      .then((cs) => setPendingRequests(cs.filter((c) => c.status === "pendiente" && c.direction === "recibida").length))
      .catch(() => null);
  }, [profileId]);

  async function checkIn(mood: Mood) {
    if (!profileId) return;
    await submitMoodCheckin(profileId, mood);
    setSelectedMood(mood);
  }

  return (
    <div className="w-full max-w-sm space-y-8">
      <div>
        <div className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="" width={40} height={40} />
          <h1 className="text-2xl font-semibold">Tu Momento</h1>
        </div>
        <p className="mt-2 text-lg text-gold-300">{astroWeather ?? "Calculando..."}</p>
      </div>

      <div>
        <p className="mb-2 text-sm text-slate-400">¿Cómo estás hoy?</p>
        <div className="flex flex-wrap gap-2">
          {MOODS.map((m) => (
            <button
              key={m.value}
              onClick={() => checkIn(m.value)}
              className={`rounded-full px-3 py-1.5 text-sm ring-1 ${
                selectedMood === m.value
                  ? "bg-violet-600 ring-violet-600"
                  : "bg-slate-900 ring-slate-700 hover:ring-violet-400"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {pendingRequests > 0 && (
        <Link href="/conexiones" className="block rounded-md bg-slate-900 p-4 ring-1 ring-gold-400/60">
          <p className="font-medium text-gold-300">
            {pendingRequests === 1 ? "1 persona quiere conectar con vos" : `${pendingRequests} personas quieren conectar con vos`}
          </p>
          <p className="text-sm text-slate-400">Ver en Conexiones →</p>
        </Link>
      )}

      <div className="rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
        <p className="text-sm text-slate-400">En tu frecuencia</p>
        <p className="text-xl font-semibold">{frequencyCount ?? "—"} personas</p>
      </div>

      <Link href="/invitar" className="block rounded-md bg-slate-900 p-4 ring-1 ring-slate-700 hover:ring-violet-400">
        <p className="font-medium">Invitá a un amigo</p>
        <p className="text-sm text-slate-400">Mandale por WhatsApp un adelanto de su resonancia con vos →</p>
      </Link>
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <HomeContent />
      </Suspense>
      <AppNav />
    </main>
  );
}
