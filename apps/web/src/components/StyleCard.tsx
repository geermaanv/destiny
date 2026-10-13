"use client";

import { useEffect, useState } from "react";
import { getStyle, Registro, setStyle, Style, StyleChange, Tema } from "@/lib/api";
import { applyLook, Fondo, peekBackground } from "@/lib/theme";

// "Tu estilo" (spec X2): cómo te hablamos y los colores de la app salen de tu
// carta, y los podés cambiar. Mismos nombres que app/personalization/config/estilos_v1.json.
const REGISTROS: { value: Registro; label: string; description: string }[] = [
  { value: "directo", label: "Directo", description: "al grano, franco y motivador" },
  { value: "practico", label: "Práctico", description: "concreto y accionable" },
  { value: "analitico", label: "Analítico", description: "con el porqué y las ideas detrás" },
  { value: "intuitivo", label: "Intuitivo", description: "emocional, con imágenes" },
];

const FONDOS: { value: Fondo; label: string; description: string }[] = [
  { value: "constelacion", label: "Tu constelación", description: "tus planetas como estrellas" },
  { value: "aura", label: "Aura", description: "brillos suaves de tu Sol y tu Luna" },
  { value: "elemental", label: "Elementos", description: "el peso de cada elemento en tu carta" },
  { value: "horizonte", label: "Horizonte", description: "con la luna del día en que naciste" },
  { value: "ninguno", label: "Sin fondo", description: "liso" },
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

  const save = async (change: StyleChange) => {
    setSaving(true);
    try {
      const updated = await setStyle(profileId, change);
      setCurrent(updated);
      applyLook(updated);
    } finally {
      setSaving(false);
    }
  };
  const currentTheme = TEMAS.find((t) => t.value === style.tema);
  const current = REGISTROS.find((r) => r.value === style.registro);

  return (
    <div className="space-y-3 rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
      <div className="space-y-1">
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
          {style.tema_source === "carta"
            ? `${style.tema_por_que} El acento sale de tu Venus, en ${style.acento}.`
            : "Lo elegiste vos. Tu carta sugiere otros colores."}
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
      <div className="flex items-center justify-between gap-3 pt-2">
        <div className="flex gap-2">
          {(["oscuro", "claro"] as const).map((m) => (
            <button
              key={m}
              type="button"
              disabled={saving}
              onClick={() => save({ modo: m })}
              className={`rounded-md px-3 py-1 text-sm ring-1 disabled:opacity-60 ${
                style.modo === m ? "bg-violet-600 text-white ring-violet-500" : "bg-slate-950 text-slate-300 ring-slate-700"
              }`}
            >
              {m === "oscuro" ? "Oscuro" : "Claro"}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-1 pt-2">
        <div className="flex items-baseline justify-between">
          <p className="text-xs uppercase tracking-wide text-slate-500">Tu fondo</p>
          {style.fondo !== "ninguno" && (
            <button type="button" onClick={peekBackground} className="text-sm text-violet-400">
              Ver fondo
            </button>
          )}
        </div>
        <p className="text-xs text-slate-400">Se genera con tu carta: no hay dos iguales.</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {FONDOS.map((f) => (
          <button
            key={f.value}
            type="button"
            disabled={saving}
            onClick={() => save({ fondo: f.value })}
            className={`rounded-md px-2 py-1.5 text-left text-sm ring-1 disabled:opacity-60 ${
              style.fondo === f.value
                ? "bg-violet-600 text-white ring-violet-500"
                : "bg-slate-950 text-slate-300 ring-slate-700 hover:ring-violet-400"
            }`}
          >
            {f.label}
            <span className="block text-xs opacity-70">{f.description}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
