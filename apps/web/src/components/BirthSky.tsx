// Cielo de nacimiento (spec X2 v3). Dos piezas:
// - BirthSky (default): fondo de la app, un "aura" de color única por persona
//   (manchas de luz con los colores de su tema, ubicadas según su carta) y
//   algunas estrellas tenues, detrás del contenido. La rueda como fondo no se veía.
// - SkyWheel: la rueda zodiacal con los planetas donde estaban al nacer, como pieza
//   visible (arriba de Mi carta). Con Ascendente se orienta como una carta
//   (Ascendente a la izquierda, marcado "AC"); sin hora exacta, Aries a la
//   izquierda. Sol y Luna destacados. Estático: no suma movimiento.
const GLYPHS: Record<string, string> = {
  sol: "☉", luna: "☽", mercurio: "☿", venus: "♀", marte: "♂", jupiter: "♃",
  saturno: "♄", urano: "♅", neptuno: "♆", pluton: "♇",
};
const TEXT = "︎"; // fuerza el glifo como texto (no emoji)
const STARS_OPACITY = { oscuro: 0.45, claro: 0.55 };
const HIGHLIGHT = new Set(["sol", "luna"]);

type Sky = { punto: string; lon: number }[];

function seededStars(cielo: Sky, count: number) {
  // Determinísticas: siempre las mismas para la misma carta.
  let seed = Math.round(cielo.reduce((s, p) => s + p.lon * 1000, 0)) % 2147483647 || 1;
  const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  return Array.from({ length: count }, () => ({ x: rand() * 100, y: rand() * 100, size: rand() < 0.8 ? 1 : 2 }));
}

const ELEMENTS = ["fuego", "tierra", "aire", "agua"];
// Aura: cada mancha sale de un punto de la carta (posición en pantalla según su
// longitud), con un color del tema y un tamaño según el peso de su elemento.
const AURA = [
  { punto: "sol", color: "--violet-500" },
  { punto: "luna", color: "--gold-400" },
  { punto: "asc", fallback: "venus", color: "--slate-600" },
];
const AURA_OPACITY = { oscuro: 0.38, claro: 0.3 };

export default function BirthSky({ cielo, modo, elementos }: { cielo: Sky; modo: "oscuro" | "claro"; elementos?: Record<string, number> }) {
  const lon = (p: string) => cielo.find((c) => c.punto === p)?.lon;
  const blobs = AURA.flatMap((a) => {
    const l = lon(a.punto) ?? (a.fallback ? lon(a.fallback) : undefined);
    if (l === undefined) return [];
    const theta = (l * Math.PI) / 180;
    const weight = elementos?.[ELEMENTS[Math.floor(l / 30) % 4]] ?? 33;
    return [{ x: 50 + 38 * Math.cos(theta), y: 50 - 38 * Math.sin(theta), size: 45 + weight * 0.5, color: a.color }];
  });
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div
        className="absolute inset-0"
        style={{
          opacity: AURA_OPACITY[modo],
          backgroundImage: blobs
            .map((b) => `radial-gradient(circle ${b.size}vmax at ${b.x}% ${b.y}%, rgb(var(${b.color})) 0%, transparent 70%)`)
            .join(", "),
        }}
      />
      <div className="absolute inset-0 text-gold-300" style={{ opacity: STARS_OPACITY[modo] * 0.6 }}>
        {seededStars(cielo, 50).map((s, i) => (
          <span
            key={i}
            className="absolute rounded-full bg-current"
            style={{ left: `${s.x}%`, top: `${s.y}%`, width: s.size, height: s.size }}
          />
        ))}
      </div>
    </div>
  );
}

export function SkyWheel({ cielo, leyenda }: { cielo: Sky; leyenda?: string }) {
  const asc = cielo.find((p) => p.punto === "asc")?.lon ?? 0;
  const hasAsc = cielo.some((p) => p.punto === "asc");
  const at = (lon: number, r: number) => {
    const theta = Math.PI + ((lon - asc) * Math.PI) / 180;
    return { x: 50 + r * Math.cos(theta), y: 50 - r * Math.sin(theta) };
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
