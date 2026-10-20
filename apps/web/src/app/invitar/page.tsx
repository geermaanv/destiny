"use client";

import { Suspense, useEffect, useState } from "react";
import { Page } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import { createInvitation, previewInvitation, SUN_SIGNS } from "@/lib/api";

// Invitar en un paso (spec C12): su nombre y, si lo sabés, su signo. El mensaje se arma solo
// (adelanto astrológico si hay signo, comparar el test si ya lo hiciste) y se ve en vivo.
function InvitarForm() {
  const profileId = useSessionProfileId();
  const [name, setName] = useState("");
  const [sign, setSign] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [sentTo, setSentTo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // El mensaje se actualiza mientras se escribe (sin crear la invitación).
  useEffect(() => {
    if (!profileId) return;
    const friend = name.trim() || "…";
    const id = setTimeout(() => {
      previewInvitation(profileId, friend, sign)
        .then((r) => setMessage(r.message))
        .catch(() => null);
    }, 300);
    return () => clearTimeout(id);
  }, [profileId, name, sign]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!profileId || !name.trim()) {
      setError("Poné su nombre.");
      return;
    }
    setSending(true);
    setError(null);
    // La pestaña se abre antes de esperar a la API: si se abre después, el navegador la bloquea.
    const tab = window.open("", "_blank");
    try {
      const invitation = await createInvitation(profileId, name.trim(), sign);
      if (tab) tab.location.href = invitation.whatsapp_url;
      else window.location.href = invitation.whatsapp_url;
      setSentTo(name.trim());
      setName("");
      setSign("");
    } catch {
      tab?.close();
      setError("No se pudo armar la invitación. Probá de nuevo.");
    } finally {
      setSending(false);
    }
  }

  if (!profileId) return <p className="text-slate-400">Cargando…</p>;

  return (
    <form onSubmit={send} className="w-full space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Invitá a alguien</h1>
        <p className="mt-1 text-sm text-slate-400">Se lo mandás por WhatsApp desde tu celular.</p>
        {/* Spec C11: recompensa por invitar. */}
        <p className="mt-1 text-sm text-gold-300">Por cada amigo que se registre, sumás una pregunta diaria en Indagar.</p>
      </div>

      {sentTo && <p className="text-sm text-gold-300">✓ Invitación lista para {sentTo}. ¿Invitás a alguien más?</p>}

      <div className="space-y-1">
        <label htmlFor="friend-name" className="block text-sm text-slate-400">
          Su nombre
        </label>
        <input
          id="friend-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={40}
          className="w-full rounded-md bg-slate-900 px-3 py-2 ring-1 ring-slate-700"
        />
      </div>

      <div className="space-y-1">
        <label htmlFor="friend-sign" className="block text-sm text-slate-400">
          Su signo <span className="text-slate-500">(si lo sabés, le llega un adelanto de cómo fluyen)</span>
        </label>
        <select
          id="friend-sign"
          value={sign}
          onChange={(e) => setSign(e.target.value)}
          className="w-full rounded-md bg-slate-900 px-3 py-2 ring-1 ring-slate-700"
        >
          <option value="">No lo sé</option>
          {SUN_SIGNS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {message && (
        <div className="space-y-1">
          <p className="text-xs text-slate-500">Así le va a llegar</p>
          <div className="rounded-lg rounded-tl-none bg-emerald-950/60 p-4 text-sm text-slate-100 ring-1 ring-emerald-800">
            {message.replace("[link]", "(link a Destiny)")}
          </div>
        </div>
      )}

      {error && <p className="text-sm text-red-400">{error}</p>}
      <button
        type="submit"
        disabled={sending}
        className="w-full rounded-md bg-emerald-600 px-4 py-2.5 font-medium text-white disabled:opacity-50"
      >
        {sending ? "Armando…" : "Enviar por WhatsApp"}
      </button>
    </form>
  );
}

export default function InvitarPage() {
  return (
    <Page>
      <Suspense>
        <InvitarForm />
      </Suspense>
    </Page>
  );
}
