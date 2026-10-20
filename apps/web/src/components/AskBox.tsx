"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { SectionTitle } from "@/components/ui";

// Acceso a Indagar (Astrochat, specs X3 y U2) desde Hoy y Tu día: la misma pieza en los
// dos lugares. Se escribe acá mismo y "Preguntar" lleva a Indagar con la pregunta
// ya enviada.
export default function AskBox({ title, hint, example }: { title: string; hint: string; example: string }) {
  const router = useRouter();
  const [text, setText] = useState("");

  function submit(e: FormEvent) {
    e.preventDefault();
    const question = text.trim();
    if (!question) return;
    router.push(`/astrochat?q=${encodeURIComponent(question)}&enviar=1`);
  }

  return (
    <section className="space-y-2">
      <SectionTitle>{title}</SectionTitle>
      <form onSubmit={submit} className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/50">
        <p className="text-sm text-slate-300">{hint}</p>
        <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) submit(e);
            }}
            rows={2}
            maxLength={500}
            placeholder={`Ej.: ${example}`}
            className="block w-full resize-none rounded-lg bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-1 ring-slate-700 placeholder:text-slate-500 focus:ring-violet-400"
          />
        {/* Link de texto, como "Leer más" y "Ver el mes" (pedido de German). */}
        <div className="text-right text-sm">
          <button type="submit" disabled={!text.trim()} className="text-violet-400 disabled:opacity-40">
            Preguntar →
          </button>
        </div>
      </form>
    </section>
  );
}
