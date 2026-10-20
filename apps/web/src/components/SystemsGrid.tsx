import { AxisKey, DiscoverCandidate } from "@/lib/api";

// Spec B9: una columna de barras por sistema (astrología, test, numerología "pronto")
// y a la derecha el promedio de cada eje. Los colores son los mismos que en el resto
// de la app: dorado para astrología y violeta para el test.
const AXES: { key: AxisKey; label: string }[] = [
  { key: "atraccion", label: "Química" },
  { key: "afecto", label: "Afecto" },
  { key: "comunicacion", label: "Comunicación" },
  { key: "compromiso", label: "Compromiso" },
];

function Bar({ value, color }: { value: number | null | undefined; color: string }) {
  return (
    <span className="block h-1.5 overflow-hidden rounded-full bg-slate-800">
      {value != null && <span className={`block h-full rounded-full ${color}`} style={{ width: `${value}%` }} />}
    </span>
  );
}

export function globalCaption(c: DiscoverCandidate): string {
  const astro = c.systems.astrologia !== null;
  const test = c.systems.personalidad !== null;
  if (astro && test) return "Promedio de astrología y test";
  return test ? "Solo test de personalidad" : "Solo astrología";
}

export default function SystemsGrid({ c, large = false }: { c: DiscoverCandidate; large?: boolean }) {
  const { astrologia, personalidad } = c.systems;
  const text = large ? "text-sm" : "text-xs";
  return (
    <div className={`grid grid-cols-[5.5rem_1fr_1fr_1fr_1.75rem] items-center gap-x-2 gap-y-1.5 ${text}`}>
      <span />
      <span className={astrologia ? "text-slate-300" : "text-slate-500"}>✦ Astro {astrologia?.total ?? "—"}</span>
      <span className={personalidad ? "text-slate-300" : "text-slate-500"}>◉ Test {personalidad?.total ?? "—"}</span>
      <span className="text-slate-500" title="Numerología: pronto"># Numer.</span>
      <span />
      {AXES.map((a) => (
        <div key={a.key} className="contents">
          <span className="text-slate-400">{a.label}</span>
          <Bar value={astrologia?.axes[a.key]} color="bg-gold-400" />
          <Bar value={personalidad?.axes[a.key]} color="bg-violet-400" />
          <Bar value={null} color="" />
          <span className="text-right font-medium text-slate-200">{c.axes_global[a.key] ?? "—"}</span>
        </div>
      ))}
    </div>
  );
}
