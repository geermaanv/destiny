// Fondo con el cielo de nacimiento (spec X2 v3): rueda zodiacal con los planetas
// donde estaban al nacer, DETRÁS del contenido (las tarjetas la tapan, nunca queda
// sobre el texto). La rueda entra entera en la pantalla (lado más corto) y las
// estrellas tienen tamaño fijo en píxeles. Con Ascendente, la rueda se orienta
// como una carta (Ascendente a la izquierda); sin hora exacta, Aries a la
// izquierda. Alrededor, la leyenda con el nombre y los datos principales de la
// carta, y esos puntos (Sol, Luna, Ascendente) destacados en la rueda.
// Estático: no suma movimiento.
const GLYPHS: Record<string, string> = {
  sol: "☉", luna: "☽", mercurio: "☿", venus: "♀", marte: "♂", jupiter: "♃",
  saturno: "♄", urano: "♅", neptuno: "♆", pluton: "♇",
};
const TEXT = "︎"; // fuerza el glifo como texto (no emoji)
const OPACITY = { oscuro: { sky: 0.4, legend: 0.8 }, claro: { sky: 0.5, legend: 0.85 } };
const HIGHLIGHT = new Set(["sol", "luna"]);

type Props = { cielo: { punto: string; lon: number }[]; modo: "oscuro" | "claro"; leyenda?: string };

export default function BirthSky({ cielo, modo, leyenda }: Props) {
  const hasAsc = cielo.some((p) => p.punto === "asc");
  const asc = cielo.find((p) => p.punto === "asc")?.lon ?? 0;
  const at = (lon: number, r: number) => {
    const theta = Math.PI + ((lon - asc) * Math.PI) / 180;
    return { x: 50 + r * Math.cos(theta), y: 50 - r * Math.sin(theta) };
  };
  // Estrellas determinísticas: siempre las mismas para la misma carta.
  let seed = Math.round(cielo.reduce((s, p) => s + p.lon * 1000, 0)) % 2147483647 || 1;
  const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const stars = Array.from({ length: 70 }, () => ({ x: rand() * 100, y: rand() * 100, size: rand() < 0.8 ? 1 : 2 }));

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 text-gold-300">
      <div className="absolute inset-0" style={{ opacity: OPACITY[modo].sky }}>
        {stars.map((s, i) => (
          <span
            key={i}
            className="absolute rounded-full bg-current"
            style={{ left: `${s.x}%`, top: `${s.y}%`, width: s.size, height: s.size }}
          />
        ))}
      </div>
      <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" className="absolute inset-0 h-full w-full">
        <defs>
          {/* Círculo para la leyenda: arranca a la izquierda y pasa por arriba (sentido horario). */}
          <path id="sky-legend" d="M 50 50 m -46.5 0 a 46.5 46.5 0 1 1 93 0 a 46.5 46.5 0 1 1 -93 0" />
        </defs>
        <g style={{ opacity: OPACITY[modo].sky }}>
          <circle cx="50" cy="50" r="44" fill="none" stroke="currentColor" strokeWidth="0.25" />
          <circle cx="50" cy="50" r="36" fill="none" stroke="currentColor" strokeWidth="0.18" />
          {Array.from({ length: 12 }, (_, i) => {
            const a = at(i * 30, 36);
            const b = at(i * 30, 44);
            return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="currentColor" strokeWidth="0.18" />;
          })}
          {cielo
            .filter((p) => GLYPHS[p.punto])
            .map((p) => {
              const pos = at(p.lon, 40);
              return (
                <text
                  key={p.punto}
                  x={pos.x}
                  y={pos.y}
                  fontSize={HIGHLIGHT.has(p.punto) ? 4.4 : 2.8}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fill="currentColor"
                >
                  {GLYPHS[p.punto] + TEXT}
                </text>
              );
            })}
          {hasAsc && (
            <>
              <line x1={at(asc, 30).x} y1={at(asc, 30).y} x2={at(asc, 44).x} y2={at(asc, 44).y} stroke="currentColor" strokeWidth="0.45" />
              <text x={at(asc, 32).x + 2.2} y={at(asc, 32).y - 1.4} fontSize="2.2" fill="currentColor">
                AC
              </text>
            </>
          )}
        </g>
        {leyenda && (
          <text fontSize="2.3" letterSpacing="0.25" fill="currentColor" style={{ opacity: OPACITY[modo].legend }}>
            <textPath href="#sky-legend" startOffset="25%" textAnchor="middle">
              {leyenda}
            </textPath>
          </text>
        )}
      </svg>
    </div>
  );
}
