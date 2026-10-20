"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { Page } from "@/components/ui";
import { CONTEXTS } from "@/components/CompatibilityView";
import { useSessionProfileId } from "@/lib/session";
import {
  createInvitation,
  getMyPersonality,
  Invitation,
  InvitationKind,
  MyPersonality,
  RelationshipContext,
  SUN_SIGNS,
} from "@/lib/api";

// Invitar (spec C8): adelanto astrológico (v1) o comparar el test de personalidad (v2).
const LOCKED_LABELS: Record<string, string> = {
  hora_de_nacimiento: "su hora de nacimiento",
  ascendente: "su ascendente",
  compatibilidad_exacta: "la compatibilidad exacta",
};

const joinY = (items: string[]) =>
  items.length > 1 ? `${items.slice(0, -1).join(", ")} y ${items[items.length - 1]}` : items[0] ?? "";

function InvitarForm() {
  const profileId = useSessionProfileId();
  const [kind, setKind] = useState<InvitationKind>("test");
  const [name, setName] = useState("");
  const [sign, setSign] = useState("");
  const [relationship, setRelationship] = useState<RelationshipContext>("pareja");
  const [mine, setMine] = useState<MyPersonality | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [invitation, setInvitation] = useState<Invitation | null>(null);

  useEffect(() => {
    if (profileId) getMyPersonality(profileId).then(setMine).catch(() => null);
  }, [profileId]);

  const testComplete = !!mine && mine.completed === mine.total_questions;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!profileId || !name.trim()) return;
    if (kind === "astro" && !sign) return;
    setSending(true);
    setError(null);
    try {
      setInvitation(
        await createInvitation(profileId, name.trim(), kind === "test" ? { kind, relationship } : { kind, friendSunSign: sign })
      );
    } catch {
      setError("No se pudo armar la invitación. Probá de nuevo.");
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
    const locked = invitation.partial_report?.locked_fields.map((f) => LOCKED_LABELS[f] ?? f) ?? [];
    return (
      <div className="w-full space-y-5">
        <h1 className="text-2xl font-semibold">Así le va a llegar a {name}</h1>
        <div className="rounded-lg rounded-tl-none bg-emerald-950/60 p-4 text-sm text-slate-100 ring-1 ring-emerald-800">
          {invitation.message}
        </div>
        <p className="text-sm text-slate-400">
          {invitation.kind === "test"
            ? `Cuando ${name} se registre por este link van a quedar conectados, y en su chat van a ver la compatibilidad (astrología y personalidad, por separado) apenas complete su test.`
            : `Es un adelanto aproximado, calculado solo con su signo. Cuando complete su carta en Destiny van a ver los dos la resonancia real, con ${joinY(locked)}.`}
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
    <form onSubmit={submit} className="w-full space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Invitá a alguien</h1>
        <p className="mt-1 text-sm text-slate-400">Se lo mandás por WhatsApp desde tu celular.</p>
        {/* Spec C11: recompensa por invitar. */}
        <p className="mt-1 text-sm text-gold-300">Por cada amigo que se registre, sumás una pregunta diaria en Indagar.</p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {(
          [
            { value: "test", title: "Comparar test", text: "Para alguien que conocés: pareja, amigo, socio, jefe." },
            { value: "astro", title: "Adelanto astrológico", text: "Un adelanto de su resonancia con vos, con su signo." },
          ] as const
        ).map((k) => (
          <button
            key={k.value}
            type="button"
            onClick={() => setKind(k.value)}
            className={`rounded-xl p-3 text-left ring-1 ${
              kind === k.value ? "bg-slate-800 ring-slate-400" : "bg-slate-900 ring-slate-700 hover:ring-slate-500"
            }`}
          >
            <span className="block text-sm font-medium">{k.title}</span>
            <span className="mt-1 block text-xs text-slate-400">{k.text}</span>
          </button>
        ))}
      </div>

      {kind === "test" && !testComplete ? (
        <div className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/40">
          <p className="text-sm text-slate-300">
            Para invitar a comparar el test, primero completá el tuyo
            {mine ? ` (llevás ${mine.completed}/${mine.total_questions})` : ""}: el mensaje le dice que ya lo hiciste.
          </p>
          <Link href="/perfil/test" className="block rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-medium text-white">
            Completar mi test
          </Link>
        </div>
      ) : (
        <>
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

          {kind === "test" ? (
            <div className="space-y-1">
              <p className="text-sm text-slate-400">¿Qué vínculo quieren mirar?</p>
              <div className="grid grid-cols-4 gap-1.5">
                {CONTEXTS.map((c) => (
                  <button
                    key={c.value}
                    type="button"
                    onClick={() => setRelationship(c.value)}
                    className={`rounded-full px-2 py-1.5 text-xs ring-1 ${
                      relationship === c.value ? "bg-slate-700 text-white ring-slate-400" : "bg-slate-900 text-slate-300 ring-slate-700"
                    }`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            </div>
          ) : (
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
          )}

          {error && <p className="text-sm text-red-400">{error}</p>}
          <button
            type="submit"
            disabled={sending}
            className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white disabled:opacity-50"
          >
            {sending ? "Armando…" : "Ver la invitación"}
          </button>
        </>
      )}
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
