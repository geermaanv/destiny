import { AxisKey, SystemScore } from "@/lib/api";

// Specs B9 y B12: por cada eje, primero el total (promedio de los sistemas) y después cada
// sistema con su número y una barra de 5 tramos de 20 %. La misma grilla en Círculo y en el chat.
// Colores de la app: dorado para astrología y violeta para el test.
const AXES: { key: AxisKey; label: string }[] = [
  { key: "atraccion", label: "Química" },
  { key: "afecto", label: "Afecto" },
  { key: "comunicacion", label: "Comunicación" },
  { key: "compromiso", label: "Compromiso" },
];

type Systems = { astrologia: SystemScore | null; personalidad: SystemScore | null };

function Score({ value, color }: { value: number | null | undefined; color: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="w-6 shrink-0 text-right text-slate-300">{value ?? "—"}</span>
      <span className="flex flex-1 gap-0.5">
        {[0, 1, 2, 3, 4].map((i) => {
          const fill = value == null ? 0 : Math.max(0, Math.min(1, (value - i * 20) / 20));
          return (
            <span key={i} className="block h-1.5 flex-1 overflow-hidden rounded-sm bg-slate-800">
              {fill > 0 && <span className={`block h-full ${color}`} style={{ width: `${fill * 100}%` }} />}
            </span>
          );
        })}
      </span>
    </span>
  );
}

export function globalCaption(systems: Systems): string {
  const astro = systems.astrologia !== null;
  const test = systems.personalidad !== null;
  if (astro && test) return "Promedio de astrología y test";
  return test ? "Solo test de personalidad" : "Solo astrología";
}

export type VinculoRow = { vinculo: string; global_pct: number | null; astrologia: number | null; personalidad: number | null };
const VINCULO_LABELS: Record<string, string> = { pareja: "Pareja", amistad: "Amistad", laboral: "Trabajo", ocasional: "Casual" };

// Número de la tabla de vínculos, en la misma posición que el número de cada eje (spec B12:
// las dos tablas encolumnadas, con la misma letra).
function Plain({ value }: { value: number | null | undefined }) {
  return <span className="block w-6 text-right text-slate-300">{value ?? "—"}</span>;
}

export default function SystemsGrid({
  systems,
  axesGlobal,
  vinculos,
  large = false,
}: {
  systems: Systems;
  axesGlobal: Partial<Record<AxisKey, number | null>>;
  vinculos?: VinculoRow[];
  large?: boolean;
}) {
  const { astrologia, personalidad } = systems;
  return (
    <div
      className={`grid grid-cols-[5.5rem_1.75rem_1fr_1fr_1fr] items-center gap-x-2 gap-y-1.5 ${large ? "text-sm" : "text-xs"}`}
    >
      <span />
      <span className="text-slate-500">Total</span>
      <span className={astrologia ? "text-slate-300" : "text-slate-500"}>✦ Astro {astrologia?.total ?? "—"}</span>
      <span className={personalidad ? "text-slate-300" : "text-slate-500"}>◉ Test {personalidad?.total ?? "—"}</span>
      <span className="text-slate-500" title="Numerología: pronto">
        # Numer.
      </span>
      {AXES.map((a) => (
        <div key={a.key} className="contents">
          <span className="text-slate-400">{a.label}</span>
          <span className="font-semibold text-gold-300">{axesGlobal[a.key] ?? "—"}</span>
          <Score value={astrologia?.axes[a.key]} color="bg-gold-400" />
          <Score value={personalidad?.axes[a.key]} color="bg-violet-400" />
          <Score value={null} color="" />
        </div>
      ))}
      {vinculos && (
        <>
          <span className="col-span-5 my-1 border-t border-slate-800" />
          <span className="text-slate-500">Vínculo</span>
          <span className="text-slate-500">Global</span>
          <span className="col-span-3" />
          {vinculos.map((v) => (
            <div key={v.vinculo} className="contents">
              <span className="text-slate-400">{VINCULO_LABELS[v.vinculo] ?? v.vinculo}</span>
              <span className="font-semibold text-gold-300">{v.global_pct ?? "—"}</span>
              <Plain value={v.astrologia} />
              <Plain value={v.personalidad} />
              <Plain value={null} />
            </div>
          ))}
        </>
      )}
    </div>
  );
}
