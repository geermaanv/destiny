import Link from "next/link";
import type { PersonalityCompat } from "@/lib/api";

// Bloques de compatibilidad compartidos por Descubrir y el chat:
// astrología y personalidad SIEMPRE por separado (spec A6 / ADR 0011).

export const CONTEXTS = [
  { value: "pareja", label: "Pareja" },
  { value: "amistad", label: "Amistad" },
  { value: "laboral", label: "Trabajo" },
  { value: "ocasional", label: "Casual" },
] as const;

const ASTRO_AXES = [
  { key: "atraccion", label: "Química" },
  { key: "afecto", label: "Afecto" },
  { key: "comunicacion", label: "Comunicación" },
  { key: "compromiso", label: "Compromiso" },
] as const;

const PERSONALITY_AXES = [
  { key: "E1", label: "Atracción" },
  { key: "E2", label: "Afecto" },
  { key: "E3", label: "Comunicación" },
  { key: "E4", label: "Compromiso" },
] as const;

function Bar({ label, value, color }: { label: string; value: number | null | undefined; color: string }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-24 text-slate-400">{label}</span>
      <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-800">
        <span className={`block h-full rounded-full ${color}`} style={{ width: `${value ?? 0}%` }} />
      </span>
      <span className="w-7 text-right text-slate-300">{value === null || value === undefined ? "—" : Math.round(value)}</span>
    </div>
  );
}

export function AstrologyBlock({
  total,
  axes,
  approximate,
}: {
  total: number;
  axes: Partial<Record<(typeof ASTRO_AXES)[number]["key"], number>>;
  approximate: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">✦ Astrología · {total}%</p>
      {ASTRO_AXES.map((a) => (
        <Bar key={a.key} label={a.label} value={axes[a.key]} color="bg-gold-400" />
      ))}
      {approximate && <p className="text-xs text-slate-500">Aproximado: sin hora exacta de nacimiento no se usan las casas.</p>}
    </div>
  );
}

export function PersonalityBlock({ p }: { p: PersonalityCompat | null }) {
  if (!p) {
    return (
      <p className="rounded-md bg-slate-950 p-2.5 text-xs text-slate-400">
        ◉ Personalidad: aparece cuando los dos completen el{" "}
        <Link href="/perfil/test" className="text-violet-400 underline">
          test de personalidad
        </Link>
        .
      </p>
    );
  }
  return (
    <div className="space-y-1.5">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        ◉ Personalidad · {p.total !== null ? `${Math.round(p.total)}%` : "provisorio"}
      </p>
      {PERSONALITY_AXES.map((a) => (
        <Bar key={a.key} label={a.label} value={p.axes[a.key]} color="bg-violet-400" />
      ))}
      {!p.complete && <p className="text-xs text-slate-500">Provisorio: alguno de los dos todavía no completó las 32 preguntas.</p>}
      {p.flags.length > 0 && <p className="text-xs text-gold-300">Diferencia importante en: {p.flags.join(", ").toLowerCase()}.</p>}
    </div>
  );
}
