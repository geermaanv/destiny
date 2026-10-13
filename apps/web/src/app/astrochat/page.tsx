"use client";

import { FormEvent, Suspense, useEffect, useRef, useState } from "react";
import { Page, PageTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import { askAstrochat, Astrochat, AstroMessage, clearAstrochat, getAstrochat } from "@/lib/api";

// Astrochat (spec X3): preguntale a Destiny. Responde con tu carta y tu día, ya
// calculados por el motor, en tu estilo y en el modo que elijas.
function Chat() {
  const profileId = useSessionProfileId();
  const [chat, setChat] = useState<Astrochat | null>(null);
  const [mode, setMode] = useState<string>("");
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!profileId) return;
    getAstrochat(profileId)
      .then((c) => {
        setChat(c);
        setMode(c.modo);
      })
      .catch(() => setNotice("No pudimos abrir el Astrochat. Probá en un rato."));
  }, [profileId]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chat?.mensajes.length, sending]);

  async function send(question: string) {
    if (!profileId || !chat || !question.trim() || sending) return;
    setSending(true);
    setNotice(null);
    const mine: AstroMessage = { rol: "persona", texto: question.trim(), modo: mode, creado: new Date().toISOString() };
    setChat({ ...chat, mensajes: [...chat.mensajes, mine] });
    setText("");
    try {
      const answer = await askAstrochat(profileId, question.trim(), mode);
      setChat((c) => (c ? { ...c, mensajes: [...c.mensajes, answer.respuesta], restantes_hoy: answer.restantes_hoy } : c));
    } catch (e) {
      setChat((c) => (c ? { ...c, mensajes: c.mensajes.filter((m) => m !== mine) } : c));
      setText(question);
      setNotice((e as Error).message);
    } finally {
      setSending(false);
    }
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    send(text);
  }

  if (!profileId || !chat) return <p className="text-slate-400">{notice ?? "Abriendo el Astrochat…"}</p>;
  const current = chat.modos.find((m) => m.clave === mode);

  return (
    <>
      <PageTitle
        title="Preguntale a Destiny"
        subtitle="Responde con tu carta y tu día, calculados por Destiny, y en tu estilo."
      />

      <div className="space-y-2">
        <div className="grid grid-cols-2 gap-1 rounded-xl bg-slate-900 p-1 ring-1 ring-slate-700 sm:grid-cols-4">
          {chat.modos.map((m) => (
            <button
              key={m.clave}
              type="button"
              onClick={() => setMode(m.clave)}
              className={`rounded-lg px-2 py-1.5 text-sm ${m.clave === mode ? "bg-violet-600 text-white" : "text-slate-300 hover:bg-slate-800"}`}
            >
              {m.nombre}
            </button>
          ))}
        </div>
        {current && <p className="text-xs text-slate-400">{current.nombre}: {current.descripcion.toLowerCase()}.</p>}
      </div>

      <div className="space-y-3">
        {chat.mensajes.length === 0 && (
          <div className="space-y-2">
            <p className="text-sm text-slate-400">Podés empezar por acá:</p>
            {chat.ejemplos.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => send(q)}
                className="block w-full rounded-xl bg-slate-900 px-4 py-3 text-left text-sm text-slate-200 ring-1 ring-slate-700 hover:ring-violet-400"
              >
                {q}
              </button>
            ))}
          </div>
        )}
        {chat.mensajes.map((m, i) => (
          <div key={i} className={`flex ${m.rol === "persona" ? "justify-end" : "justify-start"}`}>
            <p
              className={`max-w-[85%] whitespace-pre-line rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.rol === "persona" ? "bg-violet-600 text-white" : "bg-slate-900 text-slate-200 ring-1 ring-slate-700"
              }`}
            >
              {m.texto}
            </p>
          </div>
        ))}
        {sending && <p className="text-sm text-slate-400">Destiny está leyendo tu cielo…</p>}
        <div ref={endRef} />
      </div>

      {notice && <p className="text-sm text-gold-300">{notice}</p>}

      <form onSubmit={submit} className="space-y-2">
        <div className="flex items-end gap-2">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(text);
              }
            }}
            maxLength={500}
            rows={2}
            placeholder={chat.restantes_hoy > 0 ? "Escribí tu pregunta…" : "Llegaste a las preguntas de hoy"}
            disabled={chat.restantes_hoy === 0}
            className="flex-1 resize-none rounded-xl bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-violet-400 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={sending || !text.trim() || chat.restantes_hoy === 0}
            className="rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-medium text-white disabled:opacity-40"
          >
            Enviar
          </button>
        </div>
        <p className="flex justify-between text-xs text-slate-500">
          <span>
            Te {chat.restantes_hoy === 1 ? "queda 1 pregunta" : `quedan ${chat.restantes_hoy} preguntas`} hoy
          </span>
          {chat.mensajes.length > 0 && (
            <button
              type="button"
              className="underline"
              onClick={async () => {
                await clearAstrochat(profileId);
                setChat({ ...chat, mensajes: [] });
              }}
            >
              Borrar conversación
            </button>
          )}
        </p>
        <p className="text-xs text-slate-500">
          Una lectura simbólica para pensarte: no predice el futuro ni decide por vos. En temas de salud, dinero o
          decisiones importantes, consultá a un profesional.
        </p>
      </form>
    </>
  );
}

export default function AstrochatPage() {
  return (
    <Page>
      <Suspense>
        <Chat />
      </Suspense>
    </Page>
  );
}
