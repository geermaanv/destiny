"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { Card, ListCard, ListRow, Page, SectionTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import {
  getConnections,
  getFrequencyCount,
  getMyDay,
  getMyInvitations,
  getTodayAstroWeather,
  getUpcoming,
  Mood,
  MyDay,
  MyInvitation,
  submitMoodCheckin,
  UpcomingEvent,
} from "@/lib/api";

// Hoy (spec U1-C): Tu día como protagonista, el ánimo, los próximos días importantes
// y lo social en una sola tarjeta.
const MOODS: { value: Mood; label: string }[] = [
  { value: "energico", label: "Enérgico" },
  { value: "tranquilo", label: "Tranquilo" },
  { value: "reflexivo", label: "Reflexivo" },
  { value: "ansioso", label: "Ansioso" },
  { value: "inspirado", label: "Inspirado" },
];

const pad = (n: number) => String(n).padStart(2, "0");
const isoLocal = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const shortDate = (iso: string) => {
  const [y, m, d] = iso.split("-").map(Number);
  const s = new Date(y, m - 1, d).toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short" });
  return s.charAt(0).toUpperCase() + s.slice(1);
};

function invitationText(inv: MyInvitation): string {
  if (inv.status === "test_completo") return `${inv.friend_name} completó el test: mirá su compatibilidad`;
  if (inv.status === "registrado") return `${inv.friend_name} se sumó y está haciendo el test`;
  return `Esperando que ${inv.friend_name} se sume`;
}

function HomeContent() {
  const profileId = useSessionProfileId();
  const [astroWeather, setAstroWeather] = useState<string | null>(null);
  const [myDay, setMyDay] = useState<MyDay | null>(null);
  const [upcoming, setUpcoming] = useState<UpcomingEvent[]>([]);
  const [selectedMood, setSelectedMood] = useState<Mood | null>(null);
  const [frequencyCount, setFrequencyCount] = useState<number | null>(null);
  const [pendingRequests, setPendingRequests] = useState(0);
  const [invitations, setInvitations] = useState<MyInvitation[]>([]);

  useEffect(() => {
    getTodayAstroWeather().then((r) => setAstroWeather(r.astro_weather)).catch(() => null);
  }, []);

  useEffect(() => {
    if (!profileId) return;
    const today = isoLocal(new Date());
    const tomorrow = isoLocal(new Date(Date.now() + 86400000));
    getMyDay(profileId, today).then(setMyDay).catch(() => null);
    getUpcoming(profileId, tomorrow, 3).then(setUpcoming).catch(() => null);
    getFrequencyCount(profileId).then((r) => setFrequencyCount(r.count)).catch(() => null);
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
    <>
      <header className="flex items-center gap-3">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.png" alt="" width={40} height={40} />
        <div>
          <h1 className="text-2xl font-semibold">Hoy</h1>
          <p className="text-sm text-gold-300">{astroWeather ?? "Leyendo el cielo…"}</p>
        </div>
      </header>

      {myDay && (
        <Card highlight className="space-y-2">
          <p className="text-xs uppercase tracking-wide text-slate-400">Tu día · Luna en {myDay.moon_sign}</p>
          <p className="text-xl font-medium text-gold-300">{myDay.title}</p>
          <p className="leading-relaxed text-slate-200">{myDay.text}</p>
        </Card>
      )}

      <section className="space-y-2">
        <SectionTitle>¿Cómo estás hoy?</SectionTitle>
        <div className="flex flex-wrap gap-2">
          {MOODS.map((m) => (
            <button
              key={m.value}
              onClick={() => checkIn(m.value)}
              className={`rounded-full px-3 py-1.5 text-sm ring-1 ${
                selectedMood === m.value ? "bg-violet-600 text-white ring-violet-600" : "bg-slate-900 ring-slate-700 hover:ring-violet-400"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
        {selectedMood && <p className="text-sm text-gold-300">Anotado ✓ Gracias por contarnos.</p>}
      </section>

      <section className="space-y-2">
        <SectionTitle action={<Link href="/calendario" className="text-violet-400">Ver el mes →</Link>}>
          Próximos días
        </SectionTitle>
        {upcoming.length > 0 ? (
          <ListCard>
            {upcoming.map((e) => (
              <ListRow key={e.start} href="/calendario" title={e.title} detail={`${shortDate(e.start)} · ${e.text}`} />
            ))}
          </ListCard>
        ) : (
          <p className="text-sm text-slate-400">Sin tránsitos fuertes en los próximos días.</p>
        )}
      </section>

      <section className="space-y-2">
        <SectionTitle>Tu gente</SectionTitle>
        <ListCard>
          {pendingRequests > 0 && (
            <ListRow
              href="/conexiones"
              icon="✉"
              title={pendingRequests === 1 ? "1 persona quiere conectar con vos" : `${pendingRequests} personas quieren conectar con vos`}
            />
          )}
          {invitations.map((inv) => (
            <ListRow
              key={inv.ref_id}
              href={inv.match_id ? `/chat/${inv.match_id}` : "/invitar"}
              icon="✓"
              title={invitationText(inv)}
            />
          ))}
          <ListRow
            href="/discover"
            icon="✦"
            title={frequencyCount === null ? "Gente en tu frecuencia" : `${frequencyCount} personas en tu frecuencia`}
            detail="Descubrí con quién resonás"
          />
          <ListRow href="/invitar" icon="+" title="Invitá a alguien" detail="A comparar el test o con un adelanto astrológico" />
        </ListCard>
      </section>

      <ListCard>
        <ListRow href="/carta" icon="☉" title="Mi carta" detail="Identidad, amor, vocación y emociones" />
      </ListCard>
    </>
  );
}

export default function HomePage() {
  return (
    <Page>
      <Suspense>
        <HomeContent />
      </Suspense>
    </Page>
  );
}
