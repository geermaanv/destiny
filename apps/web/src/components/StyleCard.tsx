"use client";

import { useEffect, useState } from "react";
import { getStyle, Registro, setStyle, Style, Tema } from "@/lib/api";
import { applyPalette } from "@/lib/theme";

// "Tu estilo" (spec X2): cómo te hablamos y los colores de la app salen de tu
// carta, y los podés cambiar. Mismos nombres que app/personalization/config/estilos_v1.json.
const REGISTROS: { value: Registro; label: string; description: string }[] = [
  { value: "directo", label: "Directo", description: "al grano, franco y motivador" },
  { value: "practico", label: "Práctico", description: "concreto y accionable" },
  { value: "analitico", label: "Analítico", description: "con el porqué y las ideas detrás" },
  { value: "intuitivo", label: "Intuitivo", description: "emocional, con imágenes" },
];

const TEMAS: { value: Tema; label: string; description: string }[] = [
  { value: "fuego", label: "Fuego", description: "rojo profundo, terracota y dorado" },
  { value: "tierra", label: "Tierra", description: "verde bosque, arena y cobre" },
  { value: "aire", label: "Aire", description: "azul claro, plata y lavanda" },
  { value: "agua", label: "Agua", description: "índigo, océano y violeta" },
  { value: "clasico", label: "Clásico", description: "los colores del logo" },
];

export default function StyleCard({ profileId }: { profileId: string }) {
  const [style, setCurrent] = useState<Style | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getStyle(profileId).then(setCurrent).catch(() => null);
  }, [profileId]);

  if (!style) return null;

  const save = async (change: { registro?: Registro | null; tema?: Tema | null }) => {
    setSaving(true);
    try {
      const updated = await setStyle(profileId, change);
      setCurrent(updated);
      applyPalette(updated.paleta);
    } finally {
      setSaving(false);
    }
  };
  const currentTheme = TEMAS.find((t) => t.value === style.tema);
  const current = REGISTROS.find((r) => r.value === style.registro);

  return (
    <div className="space-y-3 rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
      <div className="space-y-1">
        <span className="font-medium">Tu estilo</span>
        <p className="text-xs uppercase tracking-wide text-slate-500">Cómo te hablamos</p>
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
            onClick={() => save({ registro: r.value === style.registro_carta ? null : r.value })}
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
      <div className="space-y-1 pt-2">
        <p className="text-xs uppercase tracking-wide text-slate-500">Tus colores</p>
        <p className="text-sm text-slate-300">
          <span className="text-gold-300">{currentTheme?.label}</span>: {currentTheme?.description}.
        </p>
        <p className="text-xs text-slate-400">
          {style.tema_source === "carta" ? style.tema_por_que : "Lo elegiste vos. Tu carta sugiere otros colores."}
        </p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {TEMAS.map((t) => (
          <button
            key={t.value}
            type="button"
            disabled={saving}
            onClick={() => save({ tema: t.value === style.tema_carta ? null : t.value })}
            className={`rounded-md px-2 py-1.5 text-left text-sm ring-1 disabled:opacity-60 ${
              style.tema === t.value
                ? "bg-violet-600 text-white ring-violet-500"
                : "bg-slate-950 text-slate-300 ring-slate-700 hover:ring-violet-400"
            }`}
          >
            {t.label}
            {t.value === style.tema_carta && <span className="block text-xs opacity-70">el de tu carta</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
