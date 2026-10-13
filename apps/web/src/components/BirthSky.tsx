import { BACKGROUNDS } from "@/components/Backgrounds";
import type { Fondo } from "@/lib/theme";
// Cielo de nacimiento (spec X2 v3). Dos piezas:
// - BirthSky (default): fondo de la app generado con la carta (variantes en
//   Backgrounds.tsx, en prueba en /fondos), detrás del contenido.
// - SkyWheel: la rueda zodiacal con los planetas donde estaban al nacer, como pieza
//   visible (arriba de Mi carta). Con Ascendente se orienta como una carta
//   (Ascendente a la izquierda, marcado "AC"); sin hora exacta, Aries a la
//   izquierda. Sol y Luna destacados. Estático: no suma movimiento.
const GLYPHS: Record<string, string> = {
  sol: "☉", luna: "☽", mercurio: "☿", venus: "♀", marte: "♂", jupiter: "♃",
  saturno: "♄", urano: "♅", neptuno: "♆", pluton: "♇",
};
const TEXT = "︎"; // fuerza el glifo como texto (no emoji)
const HIGHLIGHT = new Set(["sol", "luna"]);

type Sky = { punto: string; lon: number }[];

// Fondo de la app: el que eligió la persona (por defecto, su constelación).
export default function BirthSky({ cielo, elementos, fondo }: { cielo: Sky; elementos?: Record<string, number>; fondo: Fondo }) {
  if (fondo === "ninguno") return null;
  const { Component } = BACKGROUNDS[fondo] ?? BACKGROUNDS.constelacion;
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <Component cielo={cielo} elementos={elementos} />
    </div>
  );
}

export function SkyWheel({ cielo, leyenda }: { cielo: Sky; leyenda?: string }) {
  const asc = cielo.find((p) => p.punto === "asc")?.lon ?? 0;
  const hasAsc = cielo.some((p) => p.punto === "asc");
  const at = (lon: number, r: number) => {
    const theta = Math.PI + ((lon - asc) * Math.PI) / 180;
    return { x: Math.round((50 + r * Math.cos(theta)) * 100) / 100, y: Math.round((50 - r * Math.sin(theta)) * 100) / 100 };
  };
  return (
    <figure className="space-y-2">
      <svg viewBox="0 0 100 100" role="img" aria-label={leyenda ?? "Tu cielo de nacimiento"} className="mx-auto w-full max-w-[18rem] text-gold-300">
        <circle cx="50" cy="50" r="47" fill="none" stroke="currentColor" strokeOpacity="0.6" strokeWidth="0.5" />
        <circle cx="50" cy="50" r="36" fill="none" stroke="currentColor" strokeOpacity="0.4" strokeWidth="0.35" />
        {Array.from({ length: 12 }, (_, i) => {
          const a = at(i * 30, 36);
          const b = at(i * 30, 47);
          return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="currentColor" strokeOpacity="0.4" strokeWidth="0.35" />;
        })}
        {hasAsc && (
          <>
            <line x1={at(asc, 24).x} y1={at(asc, 24).y} x2={at(asc, 47).x} y2={at(asc, 47).y} stroke="currentColor" strokeWidth="0.6" />
            <text x={at(asc, 27).x + 3} y={at(asc, 27).y - 2} fontSize="3.6" fill="currentColor">
              AC
            </text>
          </>
        )}
        {cielo
          .filter((p) => GLYPHS[p.punto])
          .map((p) => {
            const pos = at(p.lon, 41.5);
            return (
              <text
                key={p.punto}
                x={pos.x}
                y={pos.y}
                fontSize={HIGHLIGHT.has(p.punto) ? 7 : 5}
                textAnchor="middle"
                dominantBaseline="central"
                fill="currentColor"
              >
                {GLYPHS[p.punto] + TEXT}
              </text>
            );
          })}
      </svg>
      {leyenda && <figcaption className="text-center text-xs text-slate-400">{leyenda}</figcaption>}
    </figure>
  );
}
