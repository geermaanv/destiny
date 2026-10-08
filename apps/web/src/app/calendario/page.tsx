"use client";

import { Suspense, useEffect, useState } from "react";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import { addAnnotation, CalendarDay, CalendarDayDetail, getDay, getMonth } from "@/lib/api";

function CalendarioContent() {
  const profileId = useSessionProfileId();
  const now = new Date();
  const [year] = useState(now.getUTCFullYear());
  const [month] = useState(now.getUTCMonth() + 1);
  const [days, setDays] = useState<CalendarDay[] | null>(null);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [detail, setDetail] = useState<CalendarDayDetail | null>(null);
  const [note, setNote] = useState("");

  useEffect(() => {
    if (!profileId) return;
    getMonth(profileId, year, month).then(setDays);
  }, [profileId, year, month]);

  async function openDay(day: string) {
    if (!profileId) return;
    setSelectedDay(day);
    setDetail(await getDay(profileId, day));
  }

  async function submitNote() {
    if (!profileId || !selectedDay || !note.trim()) return;
    await addAnnotation(profileId, selectedDay, note.trim());
    setNote("");
    setDetail(await getDay(profileId, selectedDay));
  }

  if (!profileId) return <p className="text-slate-400">Cargando…</p>;

  return (
    <div className="w-full max-w-sm space-y-4">
      <h1 className="text-2xl font-semibold">Calendario de memoria</h1>
      <div className="grid grid-cols-7 gap-1">
        {days?.map((d) => {
          const dayNum = Number(d.date.split("-")[2]);
          return (
            <button
              key={d.date}
              onClick={() => openDay(d.date)}
              className={`aspect-square rounded-md text-sm ring-1 ${
                d.has_key_transit ? "bg-violet-900 ring-violet-500" : "bg-slate-900 ring-slate-700"
              } ${selectedDay === d.date ? "ring-2 ring-white" : ""}`}
            >
              {dayNum}
            </button>
          );
        })}
      </div>

      {detail && selectedDay && (
        <div className="space-y-3 rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-400">{selectedDay}</p>
          <p>Tránsito: {detail.transits[0]?.aspect}</p>
          <div className="space-y-1">
            {detail.annotations.map((a, i) => (
              <p key={i} className="text-sm text-slate-300">
                • {a.text}
              </p>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Agregar anotación"
              className="flex-1 rounded-md bg-slate-800 px-2 py-1 text-sm outline-none ring-1 ring-slate-700"
            />
            <button onClick={submitNote} className="rounded-md bg-violet-600 px-3 py-1 text-sm">
              Agregar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function CalendarioPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <CalendarioContent />
      </Suspense>
      <AppNav />
    </main>
  );
}
