"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import AppNav from "@/components/AppNav";
import { useSessionProfileId } from "@/lib/session";
import { ChatMessage, getMessages, sendMessage } from "@/lib/api";

function ChatContent() {
  const { matchId } = useParams<{ matchId: string }>();
  const profileId = useSessionProfileId();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    getMessages(matchId).then(setMessages);
  }, [matchId]);

  async function send() {
    if (!profileId || !draft.trim()) return;
    await sendMessage(matchId, profileId, draft.trim());
    setDraft("");
    setMessages(await getMessages(matchId));
  }

  if (!profileId) return <p className="text-slate-400">Cargando…</p>;

  return (
    <div className="flex w-full max-w-sm flex-col space-y-3">
      <h1 className="text-xl font-semibold">Chat</h1>
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
            {m.text}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Escribí algo..."
          className="flex-1 rounded-md bg-slate-900 px-3 py-2 text-sm outline-none ring-1 ring-slate-700"
        />
        <button onClick={send} className="rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white">
          Enviar
        </button>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <ChatContent />
      </Suspense>
      <AppNav />
    </main>
  );
}
