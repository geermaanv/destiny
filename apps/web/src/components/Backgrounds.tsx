// Fondos generativos según la carta (spec X2 v3, en prueba): cada variante se
// dibuja dentro de un contenedor posicionado (pantalla completa o una vista previa).
// Todas son estáticas y van detrás del contenido.
type Sky = { punto: string; lon: number }[];
export type BackgroundProps = { cielo: Sky; elementos?: Record<string, number> };

const ELEMENTS = ["fuego", "tierra", "aire", "agua"] as const;
// Colores suaves por elemento (paleta orientativa del whitepaper), solo para los fondos.
const ELEMENT_COLOR: Record<string, string> = {
  fuego: "224 103 61",
  tierra: "79 138 99",
  aire: "143 179 217",
  agua: "91 95 199",
};
const element = (lon: number) => ELEMENTS[Math.floor(lon / 30) % 4];
const lonOf = (cielo: Sky, p: string) => cielo.find((c) => c.punto === p)?.lon;

function seeded(cielo: Sky) {
  let seed = Math.round(cielo.reduce((s, p) => s + p.lon * 1000, 0)) % 2147483647 || 1;
  return () => (seed = (seed * 16807) % 2147483647) / 2147483647;
}

// A · Aura sutil: solo los tonos del tema (fondo y acción), sin mezclar colores que ensucian.
export function AuraSutil({ cielo }: BackgroundProps) {
  const sol = lonOf(cielo, "sol") ?? 0;
  const luna = lonOf(cielo, "luna") ?? 180;
  const pos = (lon: number) => ({ x: 50 + 35 * Math.cos((lon * Math.PI) / 180), y: 50 - 35 * Math.sin((lon * Math.PI) / 180) });
  const a = pos(sol);
  const b = pos(luna);
  return (
    <div
      className="absolute inset-0"
      style={{
        backgroundImage: [
          `radial-gradient(ellipse 70% 50% at ${a.x}% ${a.y}%, rgb(var(--violet-700) / 0.35), transparent 70%)`,
          `radial-gradient(ellipse 80% 60% at ${b.x}% ${b.y}%, rgb(var(--slate-600) / 0.45), transparent 70%)`,
        ].join(", "),
      }}
    />
  );
}

// B · Tu constelación: tus planetas como estrellas unidas por líneas finas, en el orden del
// zodíaco. Repartidas a lo ancho (por orden) y a lo alto según su longitud, sin deformarse.
export function Constelacion({ cielo }: BackgroundProps) {
  const rand = seeded(cielo);
  const planets = cielo.filter((p) => !["asc", "mc"].includes(p.punto)).sort((a, b) => a.lon - b.lon);
  const stars = planets.map((p, i) => ({
    ...p,
    x: 10 + (80 * i) / Math.max(1, planets.length - 1),
    y: 90 + 70 * Math.sin((p.lon * 7 * Math.PI) / 180) * 0.8 + (rand() - 0.5) * 20,
  }));
  const dust = Array.from({ length: 50 }, () => ({ x: rand() * 100, y: rand() * 200 }));
  return (
    <svg className="absolute inset-0 h-full w-full text-gold-300" viewBox="0 0 100 200" preserveAspectRatio="xMidYMid slice">
      <defs>
        <radialGradient id="glow">
          <stop offset="0%" stopColor="currentColor" stopOpacity="0.9" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
        </radialGradient>
      </defs>
      {dust.map((d, i) => (
        <circle key={i} cx={d.x} cy={d.y} r="0.3" fill="currentColor" opacity="0.35" />
      ))}
      <polyline
        points={stars.map((s) => `${s.x},${s.y}`).join(" ")}
        fill="none"
        stroke="currentColor"
        strokeOpacity="0.35"
        strokeWidth="0.3"
      />
      {stars.map((s) => (
        <circle key={s.punto} cx={s.x} cy={s.y} r={s.punto === "sol" || s.punto === "luna" ? 3 : 2} fill="url(#glow)" />
      ))}
    </svg>
  );
}

// C · Degradado elemental: franjas suaves con el peso de cada elemento en tu carta.
export function DegradadoElemental({ elementos }: BackgroundProps) {
  const weights = ELEMENTS.map((e) => ({ e, w: elementos?.[e] ?? 25 })).filter((x) => x.w > 0);
  let acc = 0;
  const stops = weights.map(({ e, w }) => {
    const mid = acc + w / 2;
    acc += w;
    return `rgb(${ELEMENT_COLOR[e]} / 0.45) ${mid}%`;
  });
  return (
    <div
      className="absolute inset-0"
      style={{ backgroundImage: `linear-gradient(160deg, ${stops.join(", ")})` }}
    />
  );
}

// D · Horizonte con tu luna: cielo de atardecer del color del elemento de tu Sol y la fase
// de la Luna del día en que naciste.
export function HorizonteLuna({ cielo }: BackgroundProps) {
  const sol = lonOf(cielo, "sol") ?? 0;
  const luna = lonOf(cielo, "luna") ?? 90;
  const phase = (((luna - sol) % 360) + 360) % 360; // 0 nueva, 180 llena
  const r = 6;
  const dx = phase <= 180 ? (2 * r * phase) / 180 : (-2 * r * (360 - phase)) / 180;
  return (
    <div className="absolute inset-0" style={{ backgroundImage: `linear-gradient(180deg, transparent 45%, rgb(${ELEMENT_COLOR[element(sol)]} / 0.32) 100%)` }}>
      <svg className="absolute right-[8%] top-[6%] h-16 w-16 text-gold-200" viewBox="-10 -10 20 20">
        <defs>
          <mask id="moon-phase">
            <circle r={r} fill="white" />
            <circle r={r} cx={dx} fill="black" />
          </mask>
        </defs>
        <circle r={r} fill="currentColor" opacity="0.12" />
        <circle r={r} fill="currentColor" opacity="0.75" mask="url(#moon-phase)" />
      </svg>
    </div>
  );
}

export const BACKGROUNDS = {
  aura: { label: "A · Aura sutil", Component: AuraSutil },
  constelacion: { label: "B · Tu constelación", Component: Constelacion },
  elemental: { label: "C · Degradado elemental", Component: DegradadoElemental },
  horizonte: { label: "D · Horizonte con tu luna", Component: HorizonteLuna },
};
