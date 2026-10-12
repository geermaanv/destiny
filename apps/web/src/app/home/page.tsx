"use client";

import { Suspense, useEffect, useState } from "react";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import Link from "next/link";
import {
  getConnections,
  getFrequencyCount,
  getMyDay,
  getMyInvitations,
  getTodayAstroWeather,
  Mood,
  MyDay,
  MyInvitation,
  submitMoodCheckin,
} from "@/lib/api";

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
  const [invitations, setInvitations] = useState<MyInvitation[]>([]);
  const [myDay, setMyDay] = useState<MyDay | null>(null);

  useEffect(() => {
    if (!profileId) return;
    getFrequencyCount(profileId).then((r) => setFrequencyCount(r.count));
    const now = new Date();
    const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
    getMyDay(profileId, today).then(setMyDay).catch(() => null);
    getConnections(profileId)
      .then((cs) => setPendingRequests(cs.filter((c) => c.status === "pendiente" && c.direction === "recibida").length))
      .catch(() => null);
    getMyInvitations(profileId)
      .then((all) => setInvitations(all.filter((i) => i.kind === "test").slice(0, 3)))
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

      {myDay && (
        <Link href="/calendario" className="block space-y-1 rounded-md bg-slate-900 p-4 ring-1 ring-gold-400/40 hover:ring-gold-400">
          <p className="text-xs uppercase tracking-wide text-slate-400">Tu día · Luna en {myDay.moon_sign}</p>
          <p className="font-medium text-gold-300">{myDay.title}</p>
          <p className="text-sm text-slate-300">{myDay.text}</p>
          <p className="pt-1 text-xs text-violet-400">Ver tu calendario →</p>
        </Link>
      )}

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
        {selectedMood && (
          <p className="mt-2 text-sm text-gold-300">
            Anotado ✓ Gracias por contarnos cómo estás hoy.
          </p>
        )}
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

      {invitations.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-slate-400">Tus invitaciones a comparar el test</p>
          {invitations.map((inv) => {
            const text =
              inv.status === "test_completo"
                ? `${inv.friend_name} completó el test: mirá su compatibilidad →`
                : inv.status === "registrado"
                  ? `${inv.friend_name} se sumó y está haciendo el test`
                  : `Esperando que ${inv.friend_name} se sume`;
            const style = inv.status === "test_completo" ? "ring-gold-400/60 text-gold-300" : "ring-slate-800 text-slate-300";
            return inv.match_id ? (
              <Link key={inv.ref_id} href={`/chat/${inv.match_id}`} className={`block rounded-md bg-slate-900 p-3 text-sm ring-1 ${style}`}>
                {text}
              </Link>
            ) : (
              <p key={inv.ref_id} className={`rounded-md bg-slate-900 p-3 text-sm ring-1 ${style}`}>
                {text}
              </p>
            );
          })}
        </div>
      )}

      <Link href="/invitar" className="block rounded-md bg-slate-900 p-4 ring-1 ring-slate-700 hover:ring-violet-400">
        <p className="font-medium">Invitá a alguien</p>
        <p className="text-sm text-slate-400">A comparar el test de personalidad, o con un adelanto astrológico →</p>
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
