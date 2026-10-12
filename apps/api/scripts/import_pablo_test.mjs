// Extrae del HTML de Pablo (docs/referencias/pablo_test_express_v4.html) todo el
// modelo del test de personalidad y lo escribe como configuración para la API
// (app/personality/config/test_v4.json). Pablo es la fuente de verdad: no se
// transcribe nada a mano, se ejecuta su propio código.
//
// Uso: node scripts/import_pablo_test.mjs
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../..");
const html = fs.readFileSync(path.join(root, "docs/referencias/pablo_test_express_v4.html"), "utf8");
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];
// Solo la parte del modelo (antes de la app): datos + defaultMatrix.
const model = script.split("/* App multipersona express V4.0 */")[0];

const ctx = {};
vm.createContext(ctx);
vm.runInContext(model + "\n;globalThis.__out = {QUESTIONS, AXES, MODES, CROSS, ITEMS, ORDINAL, RITMO, FRECUENCIA, CRITICO, RELATED, defaultMatrix};", ctx);
const m = ctx.__out;

// Topes de E4 y preferencias 70/30: están dentro de funciones de la app; se leen del texto.
const capsMatch = script.match(/for\(const \[id,max,label\] of (\[\[.*?\]\])\)/);
const caps = JSON.parse(capsMatch[1].replace(/'/g, '"')).map(([id, max, label]) => ({ id, max, label }));
const pref = script.match(/return picks\.length===1\?\[1\]:\[([.\d]+),([.\d]+)\]/);

const items = m.ITEMS.map((it) => ({
  id: it.id,
  axis: it.axis,
  kind: it.kind,
  weight: it.weight,
  ...(it.q ? { question: it.q, options: it.o } : {}),
  ...(it.need ? { name: it.name, need: it.need, give: it.give, description: it.desc } : {}),
  matrix: m.defaultMatrix(it),
}));

const config = {
  version: "pablo-v4",
  source: "docs/referencias/pablo_test_express_v4.html (Pablo Maiztegui). Generado por scripts/import_pablo_test.mjs: no editar a mano lo que viene de Pablo; si cambia el HTML, se vuelve a importar.",
  axes: m.AXES,
  modes: Object.fromEntries(Object.entries(m.MODES).map(([k, v]) => [k, { name: v.name, weights: { E1: v.weights[0], E2: v.weights[1], E3: v.weights[2], E4: v.weights[3] } }])),
  preference_weights: { one: [1], two: [Number(pref[1]), Number(pref[2])] },
  max_choices: 2,
  cross_direction_weight_factor: 0.5,
  e4_caps: { enabled: true, rule: "Si las respuestas principales de A y B están en extremos opuestos (A y E), el eje E4 no puede superar el tope.", caps },
  scales: { ordinal: m.ORDINAL, ritmo: m.RITMO, frecuencia: m.FRECUENCIA, critico: m.CRITICO, nominal: { same: 100, related: 65, different: 35 } },
  questions: items.filter((x) => !x.need),
  crosses: items.filter((x) => x.need),
};

const out = path.join(root, "apps/api/app/personality/config/test_v4.json");
let text = JSON.stringify(config, null, 1).replace(/\[\s+([^\[\]{}]*?)\s+\]/g, (_, inner) => "[" + inner.split(/\s+/).join(" ") + "]");
fs.writeFileSync(out, text + "\n");
console.log(`Escrito ${out}: ${config.questions.length} preguntas, ${config.crosses.length} cruces, ${caps.length} topes`);
