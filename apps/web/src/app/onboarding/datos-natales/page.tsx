"use client";

import { useEffect, useState } from "react";
import { createProfile, setBirthData } from "@/lib/api";

export default function DatosNatalesPage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [birthDate, setBirthDate] = useState("");
  const [birthPlace, setBirthPlace] = useState("");
  const [birthTime, setBirthTime] = useState("");
  const [timeUnknown, setTimeUnknown] = useState(false);
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    createProfile()
      .then((profile) => setProfileId(profile.id))
      .catch(() => setError("No se pudo conectar con la API."));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!profileId) return;
    setStatus("submitting");
    setError(null);
    try {
      await setBirthData(profileId, {
        birth_date: birthDate,
        birth_time: timeUnknown || !birthTime ? undefined : birthTime,
        birth_place: { query: birthPlace },
      });
      setStatus("done");
    } catch {
      setError("No se pudieron guardar los datos. Probá de nuevo.");
      setStatus("error");
    }
  }

  if (status === "done") {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
        <h1 className="text-2xl font-semibold">Listo.</h1>
        <p className="mt-2 text-slate-400">Guardamos tu carta natal. Vamos a calcular tu momento astrológico.</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-5">
        <h1 className="text-2xl font-semibold">Tus datos natales</h1>

        <div className="space-y-1">
          <label htmlFor="birth-date" className="block text-sm text-slate-400">
            Fecha de nacimiento
          </label>
          <input
            id="birth-date"
            type="date"
            required
            value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)}
            className="w-full rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="birth-place" className="block text-sm text-slate-400">
            Lugar de nacimiento
          </label>
          <input
            id="birth-place"
            type="text"
            required
            placeholder="Ciudad, país"
            value={birthPlace}
            onChange={(e) => setBirthPlace(e.target.value)}
            className="w-full rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="birth-time" className="block text-sm text-slate-400">
            Hora de nacimiento
          </label>
          <input
            id="birth-time"
            type="time"
            disabled={timeUnknown}
            value={birthTime}
            onChange={(e) => setBirthTime(e.target.value)}
            className="w-full rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400 disabled:opacity-40"
          />
          <label className="flex items-center gap-2 pt-1 text-sm text-slate-400">
            <input
              type="checkbox"
              checked={timeUnknown}
              onChange={(e) => setTimeUnknown(e.target.checked)}
            />
            No sé mi hora exacta
          </label>
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={!profileId || status === "submitting"}
          className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white disabled:opacity-50"
        >
          {status === "submitting" ? "Guardando..." : "Continuar"}
        </button>
      </form>
    </main>
  );
}
