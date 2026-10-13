// Fondo con el cielo de nacimiento (spec X2 v3): rueda zodiacal muy tenue con
// los planetas donde estaban al nacer. Con Ascendente, la rueda se orienta
// como una carta (Ascendente a la izquierda); sin hora exacta, Aries a la
// izquierda. Estático: no suma movimiento.
const GLYPHS: Record<string, string> = {
  sol: "☉", luna: "☽", mercurio: "☿", venus: "♀", marte: "♂", jupiter: "♃",
  saturno: "♄", urano: "♅", neptuno: "♆", pluton: "♇",
};
const TEXT = "︎"; // fuerza el glifo como texto (no emoji)

export default function BirthSky({ cielo }: { cielo: { punto: string; lon: number }[] }) {
  const asc = cielo.find((p) => p.punto === "asc")?.lon ?? 0;
  const at = (lon: number, r: number) => {
    const theta = Math.PI + ((lon - asc) * Math.PI) / 180;
    return { x: 50 + r * Math.cos(theta), y: 50 - r * Math.sin(theta) };
  };
  // Estrellas determinísticas: siempre las mismas para la misma carta.
  let seed = Math.round(cielo.reduce((s, p) => s + p.lon * 1000, 0)) % 2147483647 || 1;
  const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const stars = Array.from({ length: 60 }, () => ({ x: rand() * 100, y: rand() * 100, r: 0.12 + rand() * 0.25 }));

  return (
    <svg
      aria-hidden
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid slice"
      className="pointer-events-none fixed inset-0 z-50 h-full w-full text-gold-300 opacity-[0.07]"
    >
      {stars.map((s, i) => (
        <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="currentColor" />
      ))}
      <circle cx="50" cy="50" r="44" fill="none" stroke="currentColor" strokeWidth="0.3" />
      <circle cx="50" cy="50" r="36" fill="none" stroke="currentColor" strokeWidth="0.2" />
      {Array.from({ length: 12 }, (_, i) => {
        const a = at(i * 30, 36);
        const b = at(i * 30, 44);
        return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="currentColor" strokeWidth="0.2" />;
      })}
      {cielo
        .filter((p) => GLYPHS[p.punto])
        .map((p) => {
          const pos = at(p.lon, 31);
          return (
            <text key={p.punto} x={pos.x} y={pos.y} fontSize="3.2" textAnchor="middle" dominantBaseline="central" fill="currentColor">
              {GLYPHS[p.punto] + TEXT}
            </text>
          );
        })}
    </svg>
  );
}
