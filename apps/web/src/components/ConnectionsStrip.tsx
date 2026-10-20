"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ProfileAvatar from "@/components/ProfileAvatar";
import { Connection, getConnections } from "@/lib/api";

// Spec U3: "Tus conexiones" arriba de Descubrir (reemplaza la solapa Mis chats). Primero las
// solicitudes por responder, después las caras (lo más nuevo primero) con un punto si hay
// mensajes nuevos. Sin conexiones ni solicitudes no se muestra.
export default function ConnectionsStrip({ profileId }: { profileId: string }) {
  const [connections, setConnections] = useState<Connection[] | null>(null);

  useEffect(() => {
    getConnections(profileId).then(setConnections).catch(() => setConnections([]));
  }, [profileId]);

  if (!connections) return null;
  const requests = connections.filter((c) => c.status === "pendiente" && c.direction === "recibida").length;
  const chats = connections
    .filter((c) => c.status === "aceptada")
    .sort((a, b) => (b.last_message_at ?? "").localeCompare(a.last_message_at ?? ""));
  if (requests === 0 && chats.length === 0) return null;

  return (
    <section className="space-y-2 border-b border-slate-800 pb-4">
      <div className="flex items-baseline justify-between">
        <h2 className="text-xs font-medium uppercase tracking-wide text-slate-400">Tus conexiones</h2>
        <Link href="/conexiones" className="text-xs text-violet-400">
          Ver todas →
        </Link>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-1 [scrollbar-width:none]">
        {requests > 0 && (
          <Link href="/conexiones" className="flex w-16 shrink-0 flex-col items-center gap-1">
            <span className="flex h-12 w-12 items-center justify-center rounded-full text-lg font-semibold text-gold-300 ring-2 ring-gold-400">
              {requests}
            </span>
            <span className="text-center text-[11px] leading-tight text-gold-300">
              {requests === 1 ? "Quiere conectar" : "Quieren conectar"}
            </span>
          </Link>
        )}
        {chats.map((c) => (
          <Link key={c.match_id} href={`/chat/${c.match_id}`} className="flex w-16 shrink-0 flex-col items-center gap-1">
            <span className="relative">
              <ProfileAvatar photoUrl={c.other.photo_url} avatar={c.other.avatar} sunSign={c.other.sun_sign} size={48} />
              {c.unread && (
                <span
                  aria-label="Mensajes nuevos"
                  className="absolute right-0 top-0 h-3 w-3 rounded-full bg-orange-400 ring-2 ring-slate-950"
                />
              )}
            </span>
            <span className="w-full truncate text-center text-[11px] text-slate-300">{c.other.display_name ?? "Sin nombre"}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
