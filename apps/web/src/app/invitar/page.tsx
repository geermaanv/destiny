"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { createInvitation, Invitation, SUN_SIGNS } from "@/lib/api";

function InvitarForm() {
  const profileId = useSearchParams().get("profileId");
  const [name, setName] = useState("");
  const [sign, setSign] = useState("");
  const [invitation, setInvitation] = useState<Invitation | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!profileId || !name || !sign) return;
    setInvitation(await createInvitation(profileId, name, sign));
  }

  if (!profileId) return <p className="text-slate-400">Falta el perfil.</p>;

  if (invitation) {
    return (
      <div className="w-full max-w-sm space-y-4 text-center">
        <h1 className="text-2xl font-semibold">Reporte parcial</h1>
        <p className="text-slate-300">{invitation.partial_report.teaser}</p>
        <p className="text-sm text-slate-500">
          Bloqueado: {invitation.partial_report.locked_fields.join(", ")}
        </p>
        <a
          href={invitation.whatsapp_url}
          target="_blank"
          className="inline-block rounded-md bg-green-600 px-4 py-2 font-medium text-white"
        >
          Compartir por WhatsApp
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="w-full max-w-sm space-y-4">
      <h1 className="text-2xl font-semibold">Invitar a un amigo</h1>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Nombre"
        required
        className="w-full rounded-md bg-slate-900 px-3 py-2 ring-1 ring-slate-700"
      />
      <select
        value={sign}
        onChange={(e) => setSign(e.target.value)}
        required
        className="w-full rounded-md bg-slate-900 px-3 py-2 ring-1 ring-slate-700"
      >
        <option value="">Signo solar</option>
        {SUN_SIGNS.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <button type="submit" className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white">
        Generar reporte
      </button>
    </form>
  );
}

export default function InvitarPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <Suspense>
        <InvitarForm />
      </Suspense>
    </main>
  );
}
