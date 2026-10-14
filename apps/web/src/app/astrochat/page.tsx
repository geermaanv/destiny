"use client";

import { FormEvent, Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Page, PageTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import { askAstrochat, Astrochat, AstroMessage, clearAstrochat, getAstrochat } from "@/lib/api";

// Consultá tu carta (Astrochat, spec X3). Responde con tu carta y tu día, ya
// calculados por el motor, en tu estilo. El modo no se elige acá (confundía con
// "Tu estilo"): sale del estilo de la persona, que se cambia en Perfil > Tu estilo.
function Chat() {
  const profileId = useSessionProfileId();
  const params = useSearchParams();
  const router = useRouter();
  const [chat, setChat] = useState<Astrochat | null>(null);
  const [mode, setMode] = useState<string>("");
  // Desde Tu día o Mi carta llega una pregunta sugerida (?q=), lista para mandar o editar.
  const [text, setText] = useState(() => params.get("q") ?? "");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  // Desde Hoy o Tu día la pregunta llega ya escrita y con ?enviar=1: se manda sola, una vez.
  const autoSent = useRef(false);
  const [sending, setSending] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (!profileId) return;
    getAstrochat(profileId)
      .then((c) => {
        setChat(c);
        setMode(c.modo);
        setTimeout(() => inputRef.current?.focus(), 0);
      })
      .catch(() => setNotice("No pudimos abrir el Astrochat. Probá en un rato."));
  }, [profileId]);

  useEffect(() => {
    if (chat && !autoSent.current && params.get("enviar") === "1" && params.get("q")) {
      autoSent.current = true;
      router.replace("/astrochat");
      send(params.get("q")!);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chat]);

  async function send(question: string) {
    if (!profileId || !chat || !question.trim() || sending) return;
    setSending(true);
    setNotice(null);
    const mine: AstroMessage = { rol: "persona", texto: question.trim(), modo: mode, creado: new Date().toISOString() };
    setChat({ ...chat, mensajes: [...chat.mensajes, mine] });
    setText("");
    try {
      const answer = await askAstrochat(profileId, question.trim());
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

  // Preguntas y respuestas en pares, lo más nuevo arriba (pedido de German): no es un
  // chat largo de ida y vuelta, sino consultas.
  const pairs: { question: AstroMessage; answer?: AstroMessage }[] = [];
  for (const m of chat.mensajes) {
    if (m.rol === "persona") pairs.push({ question: m });
    else if (pairs.length && !pairs[pairs.length - 1].answer) pairs[pairs.length - 1].answer = m;
  }
  pairs.reverse();

  return (
    <>
      <PageTitle
        title="Consultá tu carta"
        subtitle="Preguntá lo que quieras sobre vos, tu momento o tus vínculos. Te respondemos con tu carta y tu día, en tu estilo."
      />

      <form onSubmit={submit} className="space-y-2 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/50">
        <textarea
          ref={inputRef}
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
          placeholder={chat.restantes_hoy > 0 ? "Ej.: ¿Por qué me cuesta tanto decidir?" : "Llegaste a las preguntas de hoy"}
          disabled={chat.restantes_hoy === 0}
          className="block w-full resize-none rounded-lg bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-1 ring-slate-700 placeholder:text-slate-500 focus:ring-violet-400 disabled:opacity-50"
        />
        <div className="flex items-center justify-between text-sm">
          <span className="text-xs text-slate-500">
            Te {chat.restantes_hoy === 1 ? "queda 1 pregunta" : `quedan ${chat.restantes_hoy} preguntas`} hoy
          </span>
          <button
            type="submit"
            disabled={sending || !text.trim() || chat.restantes_hoy === 0}
            className="text-violet-400 disabled:opacity-40"
          >
            Preguntar →
          </button>
        </div>
      </form>

      {notice && <p className="text-sm text-gold-300">{notice}</p>}

      {chat.mensajes.length === 0 && !text && (
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

      <div className="space-y-4">
        {pairs.map((pair, i) => (
          <section key={pairs.length - i} className="space-y-2 rounded-xl bg-slate-900 p-4 ring-1 ring-slate-700">
            <p className="text-sm font-medium text-gold-300">{pair.question.texto}</p>
            <p className="whitespace-pre-line text-sm leading-relaxed text-slate-200">
              {pair.answer ? pair.answer.texto : sending && i === 0 ? "Destiny está leyendo tu cielo…" : ""}
            </p>
          </section>
        ))}
      </div>

      {chat.mensajes.length > 0 && (
        <div className="space-y-2 text-xs text-slate-500">
          <p>
            Una lectura simbólica para pensarte: no predice el futuro ni decide por vos. En temas de salud, dinero o
            decisiones importantes, consultá a un profesional.
          </p>
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
        </div>
      )}
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
