"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import AppNav from "@/components/AppNav";
import ProfileAvatar from "@/components/ProfileAvatar";
import { Connection, getConnections, respondConnection } from "@/lib/api";
import { useSessionProfileId } from "@/lib/session";

// Conexiones (spec B7 v2): solicitudes recibidas, chats y solicitudes enviadas.
function Person({ c }: { c: Connection }) {
  return (
    <span className="flex min-w-0 items-center gap-3">
      <ProfileAvatar photoUrl={c.other.photo_url} avatar={c.other.avatar} sunSign={c.other.sun_sign} size={44} />
      <span className="min-w-0">
        <span className="block truncate font-medium">
          {c.other.display_name ?? "Sin nombre"}
          {c.other.age !== null && <span className="font-normal text-slate-400">, {c.other.age}</span>}
        </span>
        <span className="block truncate text-xs text-slate-400">{c.other.sun_sign}</span>
      </span>
    </span>
  );
}

function ConexionesContent() {
  const profileId = useSessionProfileId();
  const [connections, setConnections] = useState<Connection[] | null>(null);

  useEffect(() => {
    if (profileId) getConnections(profileId).then(setConnections);
  }, [profileId]);

  async function respond(c: Connection, action: "accept" | "reject") {
    if (!profileId) return;
    await respondConnection(c.match_id, profileId, action);
    setConnections(await getConnections(profileId));
  }

  if (!profileId || connections === null) return <p className="text-slate-400">Cargando…</p>;

  const received = connections.filter((c) => c.status === "pendiente" && c.direction === "recibida");
  const chats = connections.filter((c) => c.status === "aceptada");
  const sent = connections.filter((c) => c.status === "pendiente" && c.direction === "enviada");

  return (
    <div className="w-full max-w-sm space-y-6">
      <h1 className="text-2xl font-semibold">Conexiones</h1>

      {connections.length === 0 && (
        <p className="text-slate-400">
          Todavía no tenés conexiones. Encontrá personas con las que resonás en{" "}
          <Link href="/discover" className="text-violet-400 underline">
            Descubrir
          </Link>
          .
        </p>
      )}

      {received.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-sm font-medium text-gold-300">Quieren conectar con vos ({received.length})</h2>
          {received.map((c) => (
            <div key={c.match_id} className="space-y-3 rounded-md bg-slate-900 p-3 ring-1 ring-gold-400/40">
              <Person c={c} />
              <div className="flex gap-2">
                <button
                  onClick={() => respond(c, "accept")}
                  className="flex-1 rounded-md bg-violet-600 px-3 py-1.5 text-sm font-medium text-white"
                >
                  Aceptar
                </button>
                <button
                  onClick={() => respond(c, "reject")}
                  className="flex-1 rounded-md px-3 py-1.5 text-sm text-slate-400 ring-1 ring-slate-700"
                >
                  Ahora no
                </button>
              </div>
            </div>
          ))}
        </section>
      )}

      {chats.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-sm font-medium text-slate-400">Chats</h2>
          {chats.map((c) => (
            <Link
              key={c.match_id}
              href={`/chat/${c.match_id}`}
              className="block space-y-1 rounded-md bg-slate-900 p-3 ring-1 ring-slate-800 hover:ring-violet-400"
            >
              <Person c={c} />
              {c.last_message && <p className="truncate pl-14 text-sm text-slate-400">{c.last_message}</p>}
              {c.whatsapp.link && <p className="pl-14 text-xs text-emerald-400">Ya pueden seguir por WhatsApp</p>}
            </Link>
          ))}
        </section>
      )}

      {sent.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-sm font-medium text-slate-400">Esperando respuesta</h2>
          {sent.map((c) => (
            <div key={c.match_id} className="rounded-md bg-slate-900 p-3 opacity-70 ring-1 ring-slate-800">
              <Person c={c} />
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

export default function ConexionesPage() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <ConexionesContent />
      </Suspense>
      <AppNav />
    </main>
  );
}
