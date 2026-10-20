"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Page, PageTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import {
  CalendarDay,
  CalendarDayDetail,
  getDay,
  getMonth,
  getUpcoming,
  UpcomingEvent,
} from "@/lib/api";

// Calendario de memoria (B6): mes navegable + lista de los próximos 10 tránsitos
// importantes desde hoy, para verlos sin tener que tocar cada día.
const WEEKDAYS = ["L", "M", "M", "J", "V", "S", "D"];
const MONTH_NAMES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

const pad = (n: number) => String(n).padStart(2, "0");
const isoLocal = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const parseIso = (iso: string) => {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
};
const upperFirst = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const shortDate = (iso: string) =>
  upperFirst(parseIso(iso).toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short" }));
const longDate = (iso: string) =>
  upperFirst(parseIso(iso).toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long" }));

function eventDates(e: UpcomingEvent): string {
  if (e.start === e.end) return shortDate(e.start);
  return `${shortDate(e.start)} → ${parseIso(e.end).getDate()}`;
}

function CalendarioContent() {
  const profileId = useSessionProfileId();
  const today = isoLocal(new Date());
  const [cursor, setCursor] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() + 1 };
  });
  const [days, setDays] = useState<CalendarDay[] | null>(null);
  const [upcoming, setUpcoming] = useState<UpcomingEvent[] | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [detail, setDetail] = useState<CalendarDayDetail | null>(null);
  const detailRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!profileId) return;
    setDays(null);
    getMonth(profileId, cursor.year, cursor.month).then(setDays).catch(() => setLoadError(true));
  }, [profileId, cursor]);

  // La lista sigue al mes que se está mirando (B6, corrección 2026-10-12):
  // en el mes actual, desde hoy; en otro mes, desde el día 1 de ese mes.
  const isCurrentMonth = today.startsWith(`${cursor.year}-${pad(cursor.month)}`);
  const listFrom = isCurrentMonth ? today : `${cursor.year}-${pad(cursor.month)}-01`;

  useEffect(() => {
    if (!profileId) return;
    setUpcoming(null);
    getUpcoming(profileId, listFrom).then(setUpcoming).catch(() => setUpcoming([]));
  }, [profileId, listFrom]);

  function moveMonth(delta: number) {
    setCursor(({ year, month }) => {
      const d = new Date(year, month - 1 + delta, 1);
      return { year: d.getFullYear(), month: d.getMonth() + 1 };
    });
  }

  async function openDay(day: string) {
    if (!profileId) return;
    setSelectedDay(day);
    setDetail(await getDay(profileId, day));
    setTimeout(() => detailRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" }), 50);
  }

  function openEvent(e: UpcomingEvent) {
    const d = parseIso(e.start);
    setCursor({ year: d.getFullYear(), month: d.getMonth() + 1 });
    openDay(e.start);
  }

  if (loadError) return <p className="text-slate-400">No pudimos cargar esta pantalla. Revisá tu conexión y probá de nuevo.</p>;
  if (!profileId) return <p className="text-slate-400">Cargando…</p>;

  // La grilla arranca en lunes: celdas vacías antes del día 1.
  const firstWeekday = (new Date(cursor.year, cursor.month - 1, 1).getDay() + 6) % 7;

  return (
    <div className="w-full space-y-6">
      <PageTitle title="Calendario" back={{ href: "/home", label: "Hoy" }} />

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <button onClick={() => moveMonth(-1)} aria-label="Mes anterior" className="px-3 py-1 text-xl text-slate-400">
            ‹
          </button>
          <p className="font-medium">
            {MONTH_NAMES[cursor.month - 1]} {cursor.year}
          </p>
          <button onClick={() => moveMonth(1)} aria-label="Mes siguiente" className="px-3 py-1 text-xl text-slate-400">
            ›
          </button>
        </div>

        <div className="grid grid-cols-7 gap-1 text-center text-xs text-slate-500">
          {WEEKDAYS.map((w, i) => (
            <span key={i}>{w}</span>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {Array.from({ length: firstWeekday }, (_, i) => (
            <span key={`empty-${i}`} />
          ))}
          {days?.map((d) => {
            const dayNum = Number(d.date.split("-")[2]);
            const isToday = d.date === today;
            return (
              <button
                key={d.date}
                onClick={() => openDay(d.date)}
                className={`relative aspect-square rounded-md text-sm ${
                  d.has_key_transit ? "bg-violet-950" : "bg-slate-900"
                } ${
                  selectedDay === d.date
                    ? "ring-2 ring-slate-100"
                    : isToday
                      ? "font-semibold text-gold-300 ring-2 ring-gold-400"
                      : d.has_key_transit
                        ? "ring-1 ring-violet-700"
                        : "ring-1 ring-slate-800"
                }`}
              >
                {dayNum}
                {d.has_key_transit && (
                  <span className="absolute bottom-1 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full bg-violet-400" />
                )}
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-violet-400" /> Tránsito importante
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full ring-2 ring-gold-400" /> Hoy
          </span>
        </div>
      </section>

      {detail && selectedDay && (
        <div ref={detailRef} className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-400">{longDate(selectedDay)}</p>
          {detail.transits[0]?.title ? (
            <div>
              <p className="font-medium text-gold-300">{detail.transits[0].title}</p>
              <p className="text-sm text-slate-300">{detail.transits[0].text}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">Sin tránsitos importantes este día.</p>
          )}
          {/* Spec U2: entender por qué el día es bueno o malo, en Indagar con el día precargado. */}
          <Link
            href={`/astrochat?q=${encodeURIComponent(`¿Qué significa para mí el ${longDate(selectedDay).toLowerCase().replace(",", "")}?`)}&dia=${selectedDay}`}
            className="block text-right text-sm text-violet-400"
          >
            Indagar sobre este día →
          </Link>
        </div>
      )}

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">
          {isCurrentMonth ? "Próximos eventos" : `Eventos desde el 1 de ${MONTH_NAMES[cursor.month - 1].toLowerCase()}`}
        </h2>
        {upcoming === null && <p className="text-sm text-slate-400">Cargando…</p>}
        {upcoming?.length === 0 && <p className="text-sm text-slate-400">No hay tránsitos importantes por ahora.</p>}
        <ul className="space-y-2">
          {upcoming?.map((e) => (
            <li key={e.start}>
              <button
                onClick={() => openEvent(e)}
                className="w-full rounded-xl bg-slate-900 p-3 text-left ring-1 ring-slate-800 hover:ring-violet-400"
              >
                <span className="flex items-baseline justify-between gap-2">
                  <span className="font-medium text-gold-300">{e.title}</span>
                  <span className="shrink-0 text-xs text-slate-400">
                    {e.start === today ? "Hoy" : eventDates(e)}
                  </span>
                </span>
                <span className="mt-1 block text-sm text-slate-300">{e.text}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default function CalendarioPage() {
  return (
    <Page>
      <Suspense>
        <CalendarioContent />
      </Suspense>
    </Page>
  );
}
