"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Page } from "@/components/ui";
import {
  acceptPrivacy,
  getMyPersonality,
  getPersonalityTest,
  getProfile,
  PersonalityTest,
  RelationshipContext,
  savePersonality,
} from "@/lib/api";
import { PRIVACY_VERSION, TEST_PRIVACY } from "@/lib/privacy";
import { useSessionProfileId } from "@/lib/session";

// Test de personalidad de Pablo dentro del perfil (spec A6): un eje por vez,
// 1 o 2 opciones por pregunta (principal 70 % / secundaria 30 %), se guarda solo.
// Spec A12: aviso de privacidad antes de empezar, grupos ordenados según lo que busca
// la persona y pantalla de entrada a Atracción.
type Axis = "E1" | "E2" | "E3" | "E4";
const BASE_ORDER: Axis[] = ["E2", "E3", "E4", "E1"];
const SEEKS_ATTRACTION: (RelationshipContext | null)[] = ["pareja", "ocasional"];
const LETTERS = ["A", "B", "C", "D", "E"];

function TestContent() {
  const profileId = useSessionProfileId();
  const router = useRouter();
  const params = useSearchParams();
  const [test, setTest] = useState<PersonalityTest | null>(null);
  const [answers, setAnswers] = useState<Record<string, number[]>>({});
  const [AXES, setAxes] = useState<Axis[]>(BASE_ORDER);
  const [axis, setAxis] = useState<Axis | null>(null);
  const [accepted, setAccepted] = useState<boolean | null>(null);
  const [lookingFor, setLookingFor] = useState<RelationshipContext | null>(null);
  const [attractionIntroSeen, setAttractionIntroSeen] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (!profileId) return;
    const failed = () => setNotice("No pudimos cargar esta pantalla. Revisá tu conexión y probá de nuevo.");
    getPersonalityTest().then(setTest).catch(failed);
    getProfile(profileId)
      .then((p) => setLookingFor(p.looking_for))
      .catch(() => null);
    getMyPersonality(profileId)
      .then((m) => {
        setAnswers(m.answers);
        setAxes(m.axis_order);
        setAccepted(m.privacy_accepted);
        // Arranca en el grupo pedido (?eje=, desde Círculo) o en el primero que no terminó.
        const wanted = params.get("eje") as Axis | null;
        setAxis(wanted && m.axis_order.includes(wanted) ? wanted : m.axis_order[0]);
      })
      .catch(failed);
  }, [profileId, params]);

  async function save(qid: string, choices: number[]) {
    if (!profileId) return;
    const next = { ...answers };
    if (choices.length) next[qid] = choices;
    else delete next[qid];
    setAnswers(next);
    if (choices.length) await savePersonality(profileId, { [qid]: choices }).catch(() => setNotice("No se pudo guardar. Probá de nuevo."));
  }

  function toggle(qid: string, option: number) {
    const current = answers[qid] ?? [];
    if (current.includes(option)) return save(qid, current.filter((o) => o !== option));
    if (current.length >= (test?.max_choices ?? 2)) {
      setNotice("Podés marcar como máximo dos opciones. Desmarcá una antes de elegir otra.");
      return;
    }
    setNotice(null);
    save(qid, [...current, option]);
  }

  if (!profileId || !test || accepted === null || axis === null) return <p className="text-slate-400">{notice ?? "Cargando…"}</p>;

  if (!accepted) {
    return (
      <div className="w-full space-y-5">
        <Link href="/perfil" className="text-xs text-slate-300">
          ‹ Mi perfil
        </Link>
        <h1 className="text-2xl font-semibold">Test de personalidad</h1>
        <div className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/50">
          <p className="font-medium">Antes de empezar</p>
          <p className="text-sm text-slate-300">{TEST_PRIVACY}</p>
          <button
            onClick={async () => {
              try {
                await acceptPrivacy(profileId, "test", PRIVACY_VERSION);
                setAccepted(true);
              } catch {
                setNotice("No se pudo guardar. Probá de nuevo.");
              }
            }}
            className="w-full rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white"
          >
            Entiendo, empezar
          </button>
        </div>
        {notice && <p className="text-sm text-gold-300">{notice}</p>}
      </div>
    );
  }

  const questions = test.questions.filter((q) => q.axis === axis);
  const attractionEmpty = !test.questions.some((q) => q.axis === "E1" && answers[q.id]?.length);
  const showAttractionIntro = axis === "E1" && attractionEmpty && !attractionIntroSeen;
  const answered = test.questions.filter((q) => answers[q.id]?.length).length;
  const axisIndex = AXES.indexOf(axis);

  return (
    <div className="w-full space-y-5">
      <div className="flex items-center justify-between text-xs">
        <Link href="/perfil" className="text-slate-300">
          ‹ Mi perfil
        </Link>
        <span className="text-slate-400">
          {answered}/{test.questions.length} respondidas
        </span>
      </div>
      <div className="h-1 overflow-hidden rounded-full bg-slate-800">
        <span className="block h-full bg-gold-400" style={{ width: `${(answered * 100) / test.questions.length}%` }} />
      </div>
      <div>
        <h1 className="text-2xl font-semibold">Test de personalidad</h1>
        <p className="mt-1 text-sm text-slate-400">
          Elegí una opción, o dos si dudás: la primera cuenta 70 % y la segunda 30 %. Se guarda solo y podés seguir otro
          día.
        </p>
        <p className="mt-2 text-xs text-slate-500">
          Hay preguntas íntimas. Tus respuestas nunca se muestran a nadie: los demás solo ven el resultado de la
          compatibilidad, separado de la astrología.
        </p>
      </div>

      <div className="grid grid-cols-4 gap-1.5">
        {AXES.map((a) => {
          const done = test.questions.filter((q) => q.axis === a && answers[q.id]?.length).length;
          return (
            <button
              key={a}
              onClick={() => setAxis(a)}
              className={`rounded-md px-1 py-2 text-xs ring-1 ${
                axis === a ? "bg-slate-700 text-white ring-slate-400" : "bg-slate-900 text-slate-300 ring-slate-700"
              }`}
            >
              {test.axes[a]?.short}
              <span className="block text-[10px] opacity-75">{done}/8</span>
            </button>
          );
        })}
      </div>
      <p className="text-sm text-gold-300">{test.axes[axis]?.title}</p>

      {showAttractionIntro && (
        <div className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-200">
            Las próximas preguntas son sobre atracción. Son privadas, nadie las ve, y solo pesan si buscás pareja o algo
            casual.
          </p>
          <button
            onClick={() => setAttractionIntroSeen(true)}
            className="w-full rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white"
          >
            Responder ahora
          </button>
          {!SEEKS_ATTRACTION.includes(lookingFor) && (
            <button
              onClick={() => {
                const next = AXES[AXES.indexOf("E1") + 1];
                if (next) setAxis(next);
                else router.push("/perfil");
              }}
              className="w-full text-center text-sm text-slate-400 underline"
            >
              Responder más tarde
            </button>
          )}
        </div>
      )}

      {!showAttractionIntro && questions.map((q) => {
        const selected = answers[q.id] ?? [];
        return (
          <fieldset key={q.id} className="space-y-2 rounded-xl bg-slate-900 p-3 ring-1 ring-slate-800">
            <legend className="sr-only">{q.id}</legend>
            <p className="text-sm font-medium">{q.question}</p>
            {q.options.map((option, i) => {
              const rank = selected.indexOf(i) + 1;
              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => toggle(q.id, i)}
                  className={`flex w-full items-start gap-2 rounded-md px-2.5 py-2 text-left text-sm ring-1 ${
                    rank === 1
                      ? "bg-violet-950 ring-violet-500"
                      : rank === 2
                        ? "bg-slate-800 ring-gold-400/60"
                        : "bg-slate-950 ring-slate-800 hover:ring-slate-600"
                  }`}
                >
                  <span className="font-semibold text-gold-300">{LETTERS[i]})</span>
                  <span className="flex-1">{option}</span>
                  {rank > 0 && (
                    <span className="shrink-0 text-[10px] text-slate-400">
                      {rank === 1 ? (selected.length === 1 ? "100%" : "70% · principal") : "30%"}
                    </span>
                  )}
                </button>
              );
            })}
            {selected.length === 2 && (
              <button type="button" onClick={() => save(q.id, [selected[1], selected[0]])} className="text-xs text-slate-400 underline">
                ⇄ Invertir principal y secundaria
              </button>
            )}
          </fieldset>
        );
      })}

      {notice && <p className="text-sm text-gold-300">{notice}</p>}

      <div className="flex gap-2">
        {axisIndex > 0 && (
          <button onClick={() => setAxis(AXES[axisIndex - 1])} className="flex-1 rounded-md px-3 py-2 text-sm ring-1 ring-slate-700">
            ← Anterior
          </button>
        )}
        {axisIndex < AXES.length - 1 ? (
          <button
            onClick={() => {
              setAxis(AXES[axisIndex + 1]);
              window.scrollTo({ top: 0 });
            }}
            className="flex-1 rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white"
          >
            Siguiente eje →
          </button>
        ) : (
          <Link href="/perfil" className="flex-1 rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-medium text-white">
            {answered === test.questions.length ? "Listo ✓" : "Guardar y seguir después"}
          </Link>
        )}
      </div>
    </div>
  );
}

export default function TestPersonalidadPage() {
  return (
    <Page>
      <Suspense>
        <TestContent />
      </Suspense>
    </Page>
  );
}
