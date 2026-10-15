"use client";

import { useEffect, useState } from "react";
import { AvatarKey, EnergyPeriod, getProfile, Interest, Profile, setBasicInfo } from "@/lib/api";
import { AVATARS, avatarEmoji, ENERGY_PERIODS, INTERESTS, MAX_INTERESTS } from "@/lib/profile";

const INPUT_CLASS =
  "w-full rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400";

const chip = (selected: boolean) =>
  `rounded-full px-3 py-1.5 text-sm ring-1 ${
    selected ? "bg-slate-700 text-white ring-slate-400" : "bg-slate-900 text-slate-300 ring-slate-700 hover:ring-slate-500"
  }`;

// Formulario del perfil liviano (spec A4): se usa en el onboarding y en "Mi perfil".
export default function ProfileForm({
  profileId,
  submitLabel,
  onSaved,
}: {
  profileId: string;
  submitLabel: string;
  onSaved: (profile: Profile) => void;
}) {
  const [loaded, setLoaded] = useState<Profile | null>(null);
  const [name, setName] = useState("");
  const [energy, setEnergy] = useState<EnergyPeriod | null>(null);
  const [interests, setInterests] = useState<Interest[]>([]);
  const [bio, setBio] = useState("");
  const [neighborhood, setNeighborhood] = useState("");
  const [avatar, setAvatar] = useState<AvatarKey>("signo");
  const [saving, setSaving] = useState(false);
  const [savedFlash, setSavedFlash] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProfile(profileId)
      .then((p) => {
        setLoaded(p);
        setName(p.display_name ?? "");
        setEnergy(p.energy_period);
        setInterests(p.interests ?? []);
        setBio(p.bio ?? "");
        setNeighborhood(p.neighborhood ?? "");
        setAvatar(p.avatar ?? "signo");
      })
      .catch(() => setError("No se pudo cargar tu perfil."));
  }, [profileId]);

  function toggleInterest(value: Interest) {
    setInterests((prev) =>
      prev.includes(value) ? prev.filter((i) => i !== value) : prev.length < MAX_INTERESTS ? [...prev, value] : prev
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError("Poné tu nombre o un apodo.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const profile = await setBasicInfo(profileId, {
        display_name: name.trim(),
        energy_period: energy,
        interests,
        bio: bio.trim() || null,
        neighborhood: neighborhood.trim() || null,
        avatar,
      });
      setSaving(false);
      setSavedFlash(true);
      setTimeout(() => setSavedFlash(false), 2500);
      onSaved(profile);
    } catch {
      setError("No se pudo guardar el perfil. Probá de nuevo.");
      setSaving(false);
    }
  }

  if (!loaded && !error) return <p className="text-slate-400">Cargando…</p>;

  const previewEmoji = avatarEmoji(avatar, loaded?.sun_sign ?? null);

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-6">
      {/* Spec A11: las fotos ya no van acá (ni en el registro); se cargan en Perfil → Tus fotos y en Descubrir. */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <span className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-800 text-3xl text-gold-200 ring-1 ring-gold-400/40">
            {previewEmoji}
          </span>
          <p className="text-sm text-slate-400">
            Elegí tu avatar <span className="block text-xs text-slate-500">Se ve mientras no tengas fotos.</span>
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {AVATARS.map((a) => (
            <button
              key={a.value}
              type="button"
              onClick={() => setAvatar(a.value)}
              aria-label={a.value === "signo" ? "Mi signo" : a.value}
              className={`flex h-11 w-11 items-center justify-center rounded-full text-xl ring-1 ${
                avatar === a.value ? "bg-slate-700 ring-slate-300" : "bg-slate-900 ring-slate-700"
              }`}
            >
              {a.value === "signo" ? <span className="text-xs text-slate-200">Signo</span> : a.emoji}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-1">
        <label htmlFor="display-name" className="block text-sm text-slate-400">
          Nombre o apodo
        </label>
        <input
          id="display-name"
          required
          maxLength={40}
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={INPUT_CLASS}
        />
      </div>

      <div className="space-y-2">
        <p className="text-sm text-slate-400">¿En qué momento del día tenés más energía?</p>
        <div className="grid grid-cols-4 gap-2">
          {ENERGY_PERIODS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => setEnergy(energy === p.value ? null : p.value)}
              className={`rounded-md px-1 py-2 text-xs ring-1 ${
                energy === p.value
                  ? "bg-slate-700 text-white ring-slate-400"
                  : "bg-slate-900 text-slate-300 ring-slate-700 hover:ring-slate-500"
              }`}
            >
              <span className="block text-lg">{p.icon}</span>
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-sm text-slate-400">
          Intereses <span className="text-slate-500">(hasta {MAX_INTERESTS})</span>
        </p>
        <div className="flex flex-wrap gap-2">
          {INTERESTS.map((i) => (
            <button key={i.value} type="button" onClick={() => toggleInterest(i.value)} className={chip(interests.includes(i.value))}>
              {i.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-1">
        <label htmlFor="bio" className="block text-sm text-slate-400">
          Algo sobre vos <span className="text-slate-500">(opcional)</span>
        </label>
        <textarea
          id="bio"
          maxLength={140}
          rows={2}
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          className={INPUT_CLASS}
        />
        <p className="text-right text-xs text-slate-500">{bio.length}/140</p>
      </div>

      <div className="space-y-1">
        <label htmlFor="neighborhood" className="block text-sm text-slate-400">
          Barrio <span className="text-slate-500">(opcional)</span>
        </label>
        <input
          id="neighborhood"
          maxLength={40}
          placeholder="Ej. Palermo"
          value={neighborhood}
          onChange={(e) => setNeighborhood(e.target.value)}
          className={INPUT_CLASS}
        />
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <button
        type="submit"
        disabled={saving}
        className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white disabled:opacity-50"
      >
        {saving ? "Guardando…" : savedFlash ? "Guardado ✓" : submitLabel}
      </button>
    </form>
  );
}
