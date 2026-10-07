"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getFrequencyCount, getTodayAstroWeather, Mood, submitMoodCheckin } from "@/lib/api";

const MOODS: { value: Mood; label: string }[] = [
  { value: "energico", label: "Enérgico" },
  { value: "tranquilo", label: "Tranquilo" },
  { value: "reflexivo", label: "Reflexivo" },
  { value: "ansioso", label: "Ansioso" },
  { value: "inspirado", label: "Inspirado" },
];

function HomeContent() {
  const profileId = useSearchParams().get("profileId");
  const [astroWeather, setAstroWeather] = useState<string | null>(null);
  const [frequencyCount, setFrequencyCount] = useState<number | null>(null);
  const [selectedMood, setSelectedMood] = useState<Mood | null>(null);

  useEffect(() => {
    getTodayAstroWeather().then((r) => setAstroWeather(r.astro_weather));
    getFrequencyCount().then((r) => setFrequencyCount(r.count));
  }, []);

  async function checkIn(mood: Mood) {
    if (!profileId) return;
    await submitMoodCheckin(profileId, mood);
    setSelectedMood(mood);
  }

  return (
    <div className="w-full max-w-sm space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Tu Momento</h1>
        <p className="mt-2 text-lg text-violet-300">{astroWeather ?? "Calculando..."}</p>
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

      <div className="rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
        <p className="text-sm text-slate-400">En tu frecuencia</p>
        <p className="text-xl font-semibold">{frequencyCount ?? "—"} personas</p>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <Suspense>
        <HomeContent />
      </Suspense>
    </main>
  );
}
