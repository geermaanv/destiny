"use client";

import { useEffect, useRef, useState } from "react";
import {
  apiUrl,
  AvatarKey,
  deletePhoto,
  EnergyPeriod,
  getProfile,
  Interest,
  Profile,
  setBasicInfo,
  uploadPhoto,
} from "@/lib/api";
import { AVATARS, avatarEmoji, ENERGY_PERIODS, INTERESTS, MAX_INTERESTS } from "@/lib/profile";

const INPUT_CLASS =
  "w-full rounded-md bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-1 ring-slate-700 focus:ring-slate-400";

const chip = (selected: boolean) =>
  `rounded-full px-3 py-1.5 text-sm ring-1 ${
    selected ? "bg-violet-600 text-white ring-violet-500" : "bg-slate-900 text-slate-300 ring-slate-700 hover:ring-violet-400"
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
  const [hasPhoto, setHasPhoto] = useState(false);
  const [photoVersion, setPhotoVersion] = useState(0);
  const [saving, setSaving] = useState(false);
  const [savedFlash, setSavedFlash] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

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
        setHasPhoto(p.has_photo);
      })
      .catch(() => setError("No se pudo cargar tu perfil."));
  }, [profileId]);

  function toggleInterest(value: Interest) {
    setInterests((prev) =>
      prev.includes(value) ? prev.filter((i) => i !== value) : prev.length < MAX_INTERESTS ? [...prev, value] : prev
    );
  }

  async function handlePhoto(file: File) {
    setError(null);
    try {
      await uploadPhoto(profileId, file);
      setHasPhoto(true);
      setPhotoVersion((v) => v + 1);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function removePhoto() {
    await deletePhoto(profileId).catch(() => null);
    setHasPhoto(false);
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
      <div className="flex items-center gap-4">
        {hasPhoto ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`${apiUrl(`/profiles/${profileId}/photo`)}?v=${photoVersion}`}
            alt="Tu foto"
            className="h-20 w-20 rounded-full object-cover"
          />
        ) : (
          <span className="flex h-20 w-20 items-center justify-center rounded-full bg-slate-800 text-4xl text-gold-200 ring-1 ring-gold-400/40">
            {previewEmoji}
          </span>
        )}
        <div className="space-y-1 text-sm">
          <input
            ref={fileInput}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handlePhoto(e.target.files[0])}
          />
          <button type="button" onClick={() => fileInput.current?.click()} className="block text-violet-400 underline">
            {hasPhoto ? "Cambiar foto" : "Subir foto (opcional)"}
          </button>
          {hasPhoto && (
            <button type="button" onClick={removePhoto} className="block text-slate-500 underline">
              Usar avatar en vez de foto
            </button>
          )}
        </div>
      </div>

      {!hasPhoto && (
        <div className="space-y-2">
          <p className="text-sm text-slate-400">Elegí tu avatar</p>
          <div className="flex flex-wrap gap-2">
            {AVATARS.map((a) => (
              <button
                key={a.value}
                type="button"
                onClick={() => setAvatar(a.value)}
                aria-label={a.value === "signo" ? "Mi signo" : a.value}
                className={`flex h-11 w-11 items-center justify-center rounded-full text-xl ring-1 ${
                  avatar === a.value ? "bg-violet-600 ring-violet-400" : "bg-slate-900 ring-slate-700"
                }`}
              >
                {a.value === "signo" ? <span className="text-xs text-slate-200">Signo</span> : a.emoji}
              </button>
            ))}
          </div>
        </div>
      )}

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
                  ? "bg-violet-600 text-white ring-violet-500"
                  : "bg-slate-900 text-slate-300 ring-slate-700 hover:ring-violet-400"
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
