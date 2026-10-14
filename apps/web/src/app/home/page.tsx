"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import AskBox from "@/components/AskBox";
import { ListCard, ListRow, Page, SectionTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import {
  getConnections,
  getFrequencyCount,
  getMyDay,
  getMyInvitations,
  getTodayAstroWeather,
  getUpcoming,
  MyDay,
  MyInvitation,
  UpcomingEvent,
} from "@/lib/api";

// Hoy (spec U1-C): Tu día como protagonista, los próximos días importantes y lo
// social en una sola tarjeta. (El check-in de ánimo se sacó: no devolvía nada.)
// Ejemplos para el acceso a Consultá tu carta (los mismos de astrochat_v1.json); rota por día.
const CONSULT_EXAMPLES = [
  "¿Por qué me cuesta tanto decidir?",
  "¿Qué dice mi carta sobre cómo me vinculo?",
  "¿Con qué tiene que ver cómo me siento esta semana?",
  "¿En qué me conviene poner energía este mes?",
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
  const [frequencyCount, setFrequencyCount] = useState<number | null>(null);
  const [pendingRequests, setPendingRequests] = useState(0);
  const [invitations, setInvitations] = useState<MyInvitation[]>([]);

  useEffect(() => {
    getTodayAstroWeather(isoLocal(new Date())).then((r) => setAstroWeather(r.astro_weather)).catch(() => null);
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

  return (
    <>
      {/* Encabezado según el boceto de German: Hoy + título del día, la Luna abajo y el texto. */}
      <header className="flex items-start gap-3">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.png" alt="" width={44} height={44} className="shrink-0" />
        <div className="min-w-0">
          <h1 className="text-2xl font-semibold">
            Hoy:{myDay && <span className="font-normal text-slate-200"> {myDay.title}</span>}
          </h1>
          <p className="text-sm text-gold-300">{astroWeather ?? "Leyendo el cielo…"}</p>
        </div>
      </header>

      {myDay && (
        <section className="space-y-3">
          <p className="leading-relaxed text-slate-200">{myDay.text}</p>
          <div className="text-right text-sm">
            <Link href="/dia" className="text-violet-400">
              Leer más →
            </Link>
          </div>
        </section>
      )}

      {/* Consultá tu carta (Respuestas, spec X3): se escribe acá y se envía. */}
      <AskBox
        title="Consultá tu carta"
        hint="Preguntá lo que quieras sobre vos, tu momento o tus vínculos."
        example={CONSULT_EXAMPLES[new Date().getDate() % CONSULT_EXAMPLES.length]}
      />

      <section className="space-y-2">
        <SectionTitle>Próximos días</SectionTitle>
        <ListCard>
          {upcoming.length > 0 ? (
            upcoming.map((e) => (
              <ListRow key={e.start} href="/calendario" title={`${shortDate(e.start)} · ${e.title}`} detail={e.text} />
            ))
          ) : (
            <p className="px-4 py-3 text-sm text-slate-400">Sin tránsitos fuertes en los próximos días.</p>
          )}
          <Link href="/calendario" className="block px-4 py-3 text-right text-sm text-violet-400 hover:bg-slate-800/60">
            Ver el mes →
          </Link>
        </ListCard>
      </section>

      <section className="space-y-2">
        <SectionTitle>Tu círculo</SectionTitle>
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
