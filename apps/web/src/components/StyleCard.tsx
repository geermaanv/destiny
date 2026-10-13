"use client";

import { useEffect, useState } from "react";
import { getStyle, Registro, setStyle, Style } from "@/lib/api";

// "Cómo te hablamos" (spec X2): el estilo sale de tu carta y lo podés cambiar.
// Mismos nombres que app/personalization/config/estilos_v1.json.
const REGISTROS: { value: Registro; label: string; description: string }[] = [
  { value: "directo", label: "Directo", description: "al grano, franco y motivador" },
  { value: "practico", label: "Práctico", description: "concreto y accionable" },
  { value: "analitico", label: "Analítico", description: "con el porqué y las ideas detrás" },
  { value: "intuitivo", label: "Intuitivo", description: "emocional, con imágenes" },
];

export default function StyleCard({ profileId }: { profileId: string }) {
  const [style, setCurrent] = useState<Style | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getStyle(profileId).then(setCurrent).catch(() => null);
  }, [profileId]);

  if (!style) return null;

  const choose = async (registro: Registro | null) => {
    setSaving(true);
    try {
      setCurrent(await setStyle(profileId, registro));
    } finally {
      setSaving(false);
    }
  };
  const current = REGISTROS.find((r) => r.value === style.registro);

  return (
    <div className="space-y-3 rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
      <div className="space-y-1">
        <span className="font-medium">Cómo te hablamos</span>
        <p className="text-sm text-slate-300">
          <span className="text-gold-300">{current?.label}</span>: {current?.description}. Lo usamos en tus explicaciones y en
          tu día.
        </p>
        <p className="text-xs text-slate-400">
          {style.source === "carta" ? style.por_que : "Lo elegiste vos. Tu carta sugiere otro estilo."}
        </p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {REGISTROS.map((r) => (
          <button
            key={r.value}
            type="button"
            disabled={saving}
            onClick={() => choose(r.value === style.registro_carta ? null : r.value)}
            className={`rounded-md px-2 py-1.5 text-left text-sm ring-1 disabled:opacity-60 ${
              style.registro === r.value
                ? "bg-violet-600 text-white ring-violet-500"
                : "bg-slate-950 text-slate-300 ring-slate-700 hover:ring-violet-400"
            }`}
          >
            {r.label}
            {r.value === style.registro_carta && <span className="block text-xs opacity-70">el de tu carta</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
