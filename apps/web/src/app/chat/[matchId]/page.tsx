"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import AppNav from "@/components/AppNav";
import ProfileAvatar from "@/components/ProfileAvatar";
import { ChatMessage, Connection, getConnection, getMessages, respondConnection, sendMessage } from "@/lib/api";
import { useSessionProfileId } from "@/lib/session";

// Chat híbrido (spec B7 v2): primer contacto en Destiny y, cuando los dos
// quieren, "Pasar a WhatsApp" revela el link al número del otro.
const POLL_MS = 4000;

function ChatContent() {
  const { matchId } = useParams<{ matchId: string }>();
  const router = useRouter();
  const profileId = useSessionProfileId();
  const [connection, setConnection] = useState<Connection | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [showMenu, setShowMenu] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!profileId) return;
    const refresh = () => {
      getConnection(matchId).then(setConnection).catch(() => router.replace("/conexiones"));
      getMessages(matchId).then(setMessages);
    };
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [profileId, matchId, router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages.length]);

  async function send() {
    if (!profileId || !draft.trim()) return;
    await sendMessage(matchId, profileId, draft.trim());
    setDraft("");
    setMessages(await getMessages(matchId));
  }

  async function act(action: "whatsapp" | "block") {
    if (!profileId) return;
    const updated = await respondConnection(matchId, profileId, action);
    if (action === "block") router.replace("/conexiones");
    else setConnection(updated);
  }

  if (!profileId || !connection) return <p className="text-slate-400">Cargando…</p>;

  const name = connection.other.display_name ?? "Tu conexión";
  const wa = connection.whatsapp;

  return (
    <div className="flex w-full max-w-sm flex-col space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/conexiones" aria-label="Volver" className="text-xl text-slate-400">
            ‹
          </Link>
          <ProfileAvatar
            photoUrl={connection.other.photo_url}
            avatar={connection.other.avatar}
            sunSign={connection.other.sun_sign}
            size={40}
          />
          <div>
            <p className="font-medium">{name}</p>
            <p className="text-xs text-slate-400">{connection.other.sun_sign}</p>
          </div>
        </div>
        <div className="relative">
          <button onClick={() => setShowMenu((v) => !v)} aria-label="Opciones" className="px-2 text-xl text-slate-400">
            ⋯
          </button>
          {showMenu && (
            <button
              onClick={() => confirm(`¿Bloquear a ${name}? Se cierra el chat para los dos.`) && act("block")}
              className="absolute right-0 top-8 z-10 whitespace-nowrap rounded-md bg-slate-900 px-3 py-2 text-sm text-red-400 ring-1 ring-slate-700"
            >
              Bloquear
            </button>
          )}
        </div>
      </div>

      {connection.status === "pendiente" ? (
        <p className="rounded-md bg-slate-900 p-3 text-sm text-slate-400 ring-1 ring-slate-800">
          {connection.direction === "enviada"
            ? `Esperando que ${name} acepte la conexión.`
            : `${name} quiere conectar con vos. Aceptá desde Conexiones para chatear.`}
        </p>
      ) : (
        <>
          <div className="rounded-md bg-slate-900 p-3 text-sm ring-1 ring-slate-800">
            {wa.link ? (
              <a
                href={wa.link}
                target="_blank"
                rel="noopener noreferrer"
                className="block rounded-md bg-emerald-600 px-3 py-2 text-center font-medium text-white"
              >
                Abrir WhatsApp con {name}
              </a>
            ) : wa.me_ok ? (
              <p className="text-slate-400">Le avisamos a {name} que querés pasar a WhatsApp. Cuando acepte, aparece el botón.</p>
            ) : (
              <div className="space-y-2">
                <p className="text-slate-300">
                  {wa.other_ok
                    ? `${name} quiere seguir la charla por WhatsApp.`
                    : "¿Se entienden? Pueden pasar a WhatsApp cuando los dos quieran."}
                </p>
                <button onClick={() => act("whatsapp")} className="w-full rounded-md px-3 py-1.5 text-emerald-400 ring-1 ring-emerald-700">
                  {wa.other_ok ? "Aceptar y pasar a WhatsApp" : "Quiero pasar a WhatsApp"}
                </button>
                <p className="text-xs text-slate-500">Tu número solo se comparte si los dos aceptan.</p>
              </div>
            )}
          </div>

          <div className="space-y-2">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`rounded-md p-3 text-sm ${
                  m.sender === "system_icebreaker"
                    ? "bg-slate-800 text-gold-200"
                    : m.sender === profileId
                      ? "ml-8 bg-violet-600 text-white"
                      : "mr-8 bg-slate-900 text-slate-200"
                }`}
              >
                {m.sender === "system_icebreaker" && <span className="mb-1 block text-xs text-gold-400">✨ Rompehielos de Destiny</span>}
                {m.text}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send();
            }}
            className="flex gap-2"
          >
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Escribí algo..."
              className="min-w-0 flex-1 rounded-md bg-slate-900 px-3 py-2 text-sm outline-none ring-1 ring-slate-700"
            />
            <button type="submit" className="rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white">
              Enviar
            </button>
          </form>
        </>
      )}
    </div>
  );
}

export default function ChatPage() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <ChatContent />
      </Suspense>
      <AppNav />
    </main>
  );
}
