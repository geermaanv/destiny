// Genera tests/fixtures/pablo_golden.json ejecutando el cálculo ORIGINAL del HTML
// de Pablo sobre parejas de prueba. Los tests de la API tienen que dar los mismos números.
// Uso: node scripts/pablo_golden.mjs
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const html = fs.readFileSync(path.join(root, "docs/referencias/pablo_test_express_v4.html"), "utf8");
const script = html.match(/<script>([\s\S]*)<\/script>/)[1].replace(/load\(\);render\(\);ingestShareHash\(\);\s*$/, "");

// DOM mínimo de mentira: solo para que el script cargue (no se renderiza nada).
const el = new Proxy(function () {}, { get: (t, k) => (k === "style" ? {} : el), set: () => true, apply: () => el });
const ctx = { document: el, localStorage: { getItem: () => null, setItem: () => {} }, location: { hash: "", protocol: "file:" }, history: el, window: el, navigator: {}, console, crypto: { randomUUID: () => Math.random().toString(36).slice(2) } };
vm.createContext(ctx);
vm.runInContext(script + "\n;globalThis.__api = {QUESTIONS, compareAxis, MODES, store};", ctx);
const { QUESTIONS, compareAxis, MODES } = ctx.__api;

// Generador pseudoaleatorio con semilla (reproducible).
let seed = 20261012;
const rand = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
const pick = () => Math.floor(rand() * 5);
function randomAnswers(coverage = 1) {
  const a = {};
  for (const q of QUESTIONS) {
    if (rand() > coverage) continue;
    const first = pick();
    let second = pick();
    a[q.id] = rand() < 0.4 && second !== first ? [first, second] : [first];
  }
  return a;
}
const all = (v) => Object.fromEntries(QUESTIONS.map((q) => [q.id, v]));

const pairs = [
  { name: "identicos_una_opcion", a: all([2]), b: all([2]) },
  { name: "opuestos_extremos", a: all([0]), b: all([4]) },
  { name: "dos_opciones_cruzadas", a: all([1, 3]), b: all([3, 1]) },
  { name: "tope_hijos", a: { ...all([2]), "E4.08": [0] }, b: { ...all([2]), "E4.08": [4] } },
  { name: "tope_convivencia", a: { ...all([3]), "E4.07": [0] }, b: { ...all([3]), "E4.07": [4] } },
  { name: "parcial_media", a: randomAnswers(0.5), b: randomAnswers(0.6) },
];
for (let i = 0; i < 12; i++) pairs.push({ name: `azar_${i}`, a: randomAnswers(), b: randomAnswers() });

const out = pairs.map(({ name, a, b }) => {
  const A = { answers: a }, B = { answers: b };
  const axes = ["E1", "E2", "E3", "E4"].map((ax) => {
    const r = compareAxis(ax, A, B);
    return { axis: ax, raw: r.raw, score: r.score, coverage: r.coverage, flags: r.flags.map((f) => f.id) };
  });
  const totals = Object.fromEntries(
    Object.entries(MODES).map(([k, m]) => [k, axes.every((v, i) => m.weights[i] === 0 || v.score !== null) ? axes.reduce((s, r, i) => s + (r.score || 0) * m.weights[i] / 100, 0) : null])
  );
  return { name, a, b, axes, totals };
});
const file = path.join(here, "../tests/fixtures/pablo_golden.json");
fs.writeFileSync(file, JSON.stringify(out, null, 1) + "\n");
console.log(`Escrito ${file}: ${out.length} parejas`);
console.log(out.slice(0, 5).map((p) => `${p.name}: ${p.axes.map((x) => x.score?.toFixed(1)).join(" / ")} | formal ${p.totals.formal?.toFixed(2)}`).join("\n"));
