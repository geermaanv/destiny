"use client";

import { useState } from "react";
import { Gender, Profile, setPreferences } from "@/lib/api";

// Spec B8: género y a quién ver en Descubrir ("pareja"). No se pregunta la orientación.
const GENDERS: { value: Gender; label: string; plural: string }[] = [
  { value: "mujer", label: "Mujer", plural: "Mujeres" },
  { value: "hombre", label: "Hombre", plural: "Hombres" },
  { value: "no_binario", label: "No binario", plural: "Personas no binarias" },
];
const ALL: Gender[] = ["mujer", "hombre", "no_binario"];

const chip = (selected: boolean) =>
  `rounded-full px-3 py-1.5 text-sm ring-1 ${
    selected ? "bg-slate-700 text-white ring-slate-400" : "bg-slate-900 text-slate-300 ring-slate-700 hover:ring-slate-500"
  }`;

function toggle<T>(list: T[], value: T): T[] {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
}

export default function GenderPrefs({
  profile,
  submitLabel,
  onSaved,
}: {
  profile: Profile;
  submitLabel: string;
  onSaved: (profile: Profile) => void;
}) {
  const [gender, setGender] = useState<Gender | null>(profile.gender);
  const [detail, setDetail] = useState(profile.gender_detail ?? "");
  const [showMe, setShowMe] = useState<Gender[]>(profile.show_me ?? []);
  const [appearIn, setAppearIn] = useState<("mujer" | "hombre")[]>(
    profile.appear_in?.length ? profile.appear_in : ["mujer", "hombre"]
  );
  const [showGender, setShowGender] = useState(profile.show_gender);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function save() {
    if (!gender || showMe.length === 0) {
      setError("Elegí tu género y a quién querés ver.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const saved = await setPreferences(profile.id, {
        gender,
        gender_detail: detail.trim() || null,
        show_me: showMe,
        appear_in: gender === "no_binario" ? appearIn : [],
        show_gender: showGender,
      });
      onSaved(saved);
    } catch {
      setError("No se pudo guardar. Probá de nuevo.");
    }
    setSaving(false);
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <p className="text-sm text-slate-400">Tu género</p>
        <div className="flex flex-wrap gap-2">
          {GENDERS.map((g) => (
            <button key={g.value} type="button" onClick={() => setGender(g.value)} className={chip(gender === g.value)}>
              {g.label}
            </button>
          ))}
        </div>
        <input
          maxLength={40}
          value={detail}
          onChange={(e) => setDetail(e.target.value)}
          placeholder="Si querés, precisalo (ej. mujer trans)"
          className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400"
        />
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input type="checkbox" checked={showGender} onChange={(e) => setShowGender(e.target.checked)} />
          Mostrar mi género en mi perfil
        </label>
      </div>

      {gender === "no_binario" && (
        <div className="space-y-2">
          <p className="text-sm text-slate-400">¿En qué búsquedas querés aparecer?</p>
          <div className="flex flex-wrap gap-2">
            {(["mujer", "hombre"] as const).map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => setAppearIn(toggle(appearIn, g))}
                className={chip(appearIn.includes(g))}
              >
                {g === "mujer" ? "De mujeres" : "De hombres"}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        <p className="text-sm text-slate-400">Para pareja, mostrame</p>
        <div className="flex flex-wrap gap-2">
          {GENDERS.map((g) => (
            <button key={g.value} type="button" onClick={() => setShowMe(toggle(showMe, g.value))} className={chip(showMe.includes(g.value))}>
              {g.plural}
            </button>
          ))}
          <button type="button" onClick={() => setShowMe(ALL)} className={chip(showMe.length === ALL.length)}>
            Todas las personas
          </button>
        </div>
        <p className="text-xs text-slate-500">
          Es mutuo: solo ves a quien también quiere ver a alguien como vos. Para amistad o trabajo se ve a todos.
        </p>
      </div>

      {error && <p className="text-sm text-gold-300">{error}</p>}
      <button
        type="button"
        onClick={save}
        disabled={saving}
        className="w-full rounded-md bg-violet-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {saving ? "Guardando…" : submitLabel}
      </button>
    </div>
  );
}
