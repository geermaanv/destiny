"use client";

import { Suspense, useState } from "react";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import { createInvitation, Invitation, SUN_SIGNS } from "@/lib/api";

// Invitar a un amigo (C8, mejora #4 de la revisión): explica qué recibe el
// amigo y muestra el mensaje antes de mandarlo por WhatsApp.
const LOCKED_LABELS: Record<string, string> = {
  hora_de_nacimiento: "su hora de nacimiento",
  ascendente: "su ascendente",
  compatibilidad_exacta: "la compatibilidad exacta",
};

function InvitarForm() {
  const profileId = useSessionProfileId();
  const [name, setName] = useState("");
  const [sign, setSign] = useState("");
  const [sending, setSending] = useState(false);
  const [invitation, setInvitation] = useState<Invitation | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!profileId || !name.trim() || !sign) return;
    setSending(true);
    try {
      setInvitation(await createInvitation(profileId, name.trim(), sign));
    } finally {
      setSending(false);
    }
  }

  function reset() {
    setInvitation(null);
    setName("");
    setSign("");
  }

  if (!profileId) return <p className="text-slate-400">Cargando…</p>;

  if (invitation) {
    const locked = invitation.partial_report.locked_fields.map((f) => LOCKED_LABELS[f] ?? f);
    return (
      <div className="w-full max-w-sm space-y-5">
        <h1 className="text-2xl font-semibold">Así le va a llegar a {name}</h1>
        <div className="rounded-lg rounded-tl-none bg-emerald-950/60 p-4 text-sm text-slate-100 ring-1 ring-emerald-800">
          {invitation.message}
        </div>
        <p className="text-sm text-slate-400">
          Es un adelanto aproximado, calculado solo con su signo. Cuando complete su carta en Destiny van a ver los
          dos la resonancia real, con {locked.length > 1 ? `${locked.slice(0, -1).join(", ")} y ${locked[locked.length - 1]}` : locked[0]}.
        </p>
        <a
          href={invitation.whatsapp_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block rounded-md bg-emerald-600 px-4 py-2.5 text-center font-medium text-white"
        >
          Enviar por WhatsApp
        </a>
        <button onClick={reset} className="w-full text-center text-sm text-slate-400 underline">
          Invitar a otra persona
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="w-full max-w-sm space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Invitá a un amigo</h1>
        <p className="mt-1 text-sm text-slate-400">
          Con su nombre y su signo te armamos un adelanto de la resonancia entre ustedes. Se lo mandás por WhatsApp
          y, cuando complete su carta, los dos ven el resultado real.
        </p>
      </div>
      <div className="space-y-1">
        <label htmlFor="friend-name" className="block text-sm text-slate-400">
          Su nombre
        </label>
        <input
          id="friend-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={40}
          required
          className="w-full rounded-md bg-slate-900 px-3 py-2 ring-1 ring-slate-700"
        />
      </div>
      <div className="space-y-1">
        <label htmlFor="friend-sign" className="block text-sm text-slate-400">
          Su signo solar
        </label>
        <select
          id="friend-sign"
          value={sign}
          onChange={(e) => setSign(e.target.value)}
          required
          className="w-full rounded-md bg-slate-900 px-3 py-2 ring-1 ring-slate-700"
        >
          <option value="">Elegí un signo</option>
          {SUN_SIGNS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>
      <button
        type="submit"
        disabled={sending}
        className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white disabled:opacity-50"
      >
        {sending ? "Armando…" : "Ver la invitación"}
      </button>
    </form>
  );
}

export default function InvitarPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <InvitarForm />
      </Suspense>
      <AppNav />
    </main>
  );
}
