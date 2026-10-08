"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import {
  addAnnotation,
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
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [detail, setDetail] = useState<CalendarDayDetail | null>(null);
  const [note, setNote] = useState("");
  const detailRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!profileId) return;
    setDays(null);
    getMonth(profileId, cursor.year, cursor.month).then(setDays);
  }, [profileId, cursor]);

  useEffect(() => {
    if (profileId) getUpcoming(profileId, today).then(setUpcoming);
  }, [profileId, today]);

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

  async function submitNote() {
    if (!profileId || !selectedDay || !note.trim()) return;
    await addAnnotation(profileId, selectedDay, note.trim());
    setNote("");
    setDetail(await getDay(profileId, selectedDay));
    getUpcoming(profileId, today).then(setUpcoming);
  }

  if (!profileId) return <p className="text-slate-400">Cargando…</p>;

  // La grilla arranca en lunes: celdas vacías antes del día 1.
  const firstWeekday = (new Date(cursor.year, cursor.month - 1, 1).getDay() + 6) % 7;

  return (
    <div className="w-full max-w-sm space-y-6">
      <h1 className="text-2xl font-semibold">Calendario</h1>

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
        <div ref={detailRef} className="space-y-3 rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-400">{longDate(selectedDay)}</p>
          {detail.transits[0]?.title ? (
            <div>
              <p className="font-medium text-gold-300">{detail.transits[0].title}</p>
              <p className="text-sm text-slate-300">{detail.transits[0].text}</p>
            </div>
          ) : (
            <p className="text-sm text-slate-400">Sin tránsitos importantes este día.</p>
          )}
          {detail.annotations.length > 0 && (
            <div className="space-y-1">
              {detail.annotations.map((a, i) => (
                <p key={i} className="text-sm text-slate-300">
                  • {a.text}
                </p>
              ))}
            </div>
          )}
          <div className="flex gap-2">
            <input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Agregar una nota a este día"
              className="min-w-0 flex-1 rounded-md bg-slate-800 px-2 py-1 text-sm outline-none ring-1 ring-slate-700"
            />
            <button onClick={submitNote} className="rounded-md bg-violet-600 px-3 py-1 text-sm">
              Agregar
            </button>
          </div>
        </div>
      )}

      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Próximos eventos</h2>
        {upcoming === null && <p className="text-sm text-slate-400">Cargando…</p>}
        {upcoming?.length === 0 && <p className="text-sm text-slate-400">No hay tránsitos importantes por ahora.</p>}
        <ul className="space-y-2">
          {upcoming?.map((e) => (
            <li key={e.start}>
              <button
                onClick={() => openEvent(e)}
                className="w-full rounded-md bg-slate-900 p-3 text-left ring-1 ring-slate-800 hover:ring-violet-400"
              >
                <span className="flex items-baseline justify-between gap-2">
                  <span className="font-medium text-gold-300">{e.title}</span>
                  <span className="shrink-0 text-xs text-slate-400">
                    {e.start === today ? "Hoy" : eventDates(e)}
                  </span>
                </span>
                <span className="mt-1 block text-sm text-slate-300">{e.text}</span>
                {e.has_notes && <span className="mt-1 block text-xs text-slate-500">📝 Tenés notas</span>}
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
    <main className="flex min-h-screen flex-col items-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <CalendarioContent />
      </Suspense>
      <AppNav />
    </main>
  );
}
