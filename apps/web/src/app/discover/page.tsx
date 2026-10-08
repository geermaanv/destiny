"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import AppNav from "@/components/AppNav";
import ProfileAvatar from "@/components/ProfileAvatar";
import { createMatch, DiscoverCandidate, getDiscoverCandidates, getExplanation } from "@/lib/api";
import { energyLabel, interestLabel } from "@/lib/profile";

function DiscoverContent() {
  const router = useRouter();
  const profileId = useSearchParams().get("profileId");
  const [candidates, setCandidates] = useState<DiscoverCandidate[] | null>(null);
  const [openId, setOpenId] = useState<string | null>(null);
  const [explanations, setExplanations] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!profileId) return;
    getDiscoverCandidates(profileId)
      .then(setCandidates)
      .catch((e: Error) =>
        setError(
          e.message === "403"
            ? "Para ver Descubrir primero tenés que verificar tu identidad."
            : e.message === "409"
              ? "Te faltan tus datos natales. Volvé a empezar el registro para completarlos."
              : "No pudimos cargar Descubrir. Probá de nuevo en un rato."
        )
      );
  }, [profileId]);

  async function openCandidate(candidateId: string) {
    setOpenId(candidateId);
    if (!profileId || explanations[candidateId]) return;
    const { text } = await getExplanation(profileId, candidateId);
    setExplanations((prev) => ({ ...prev, [candidateId]: text }));
  }

  async function match(candidateId: string) {
    if (!profileId) return;
    const { id } = await createMatch(profileId, candidateId);
    router.push(`/chat/${id}?profileId=${profileId}`);
  }

  if (!profileId) return <p className="text-slate-400">Falta el perfil.</p>;
  if (error) return <p className="text-red-400">{error}</p>;

  return (
    <div className="w-full max-w-sm space-y-4">
      <h1 className="text-2xl font-semibold">Descubrir</h1>
      {candidates === null && <p className="text-slate-400">Cargando...</p>}
      {candidates?.length === 0 && <p className="text-slate-400">Todavía no hay nadie en tu frecuencia.</p>}
      {candidates?.map((c) => (
        <div key={c.profile_id} className="rounded-md bg-slate-900 p-4 ring-1 ring-slate-700">
          <button onClick={() => openCandidate(c.profile_id)} className="flex w-full items-center gap-3 text-left">
            <ProfileAvatar photoUrl={c.photo_url} avatar={c.avatar} sunSign={c.sun_sign} />
            <span className="min-w-0 flex-1">
              <span className="block truncate font-medium">
                {c.display_name ?? "Sin nombre"}
                {c.age !== null && <span className="font-normal text-slate-400">, {c.age}</span>}
              </span>
              <span className="block text-xs text-slate-400">
                {[c.sun_sign, c.neighborhood].filter(Boolean).join(" · ")}
              </span>
              <span className="block text-xs text-gold-300">{c.preview}</span>
            </span>
            <span className="font-semibold text-gold-300">{c.compatibility_pct}%</span>
          </button>
          {openId === c.profile_id && (
            <>
              {(c.bio || c.energy_period || c.interests.length > 0) && (
                <div className="mt-3 space-y-2 text-sm">
                  {c.bio && <p className="text-slate-200">“{c.bio}”</p>}
                  {c.energy_period && (
                    <p className="text-slate-400">
                      {energyLabel(c.energy_period)?.icon} Más energía a la {energyLabel(c.energy_period)?.label.toLowerCase()}
                    </p>
                  )}
                  {c.interests.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {c.interests.map((i) => (
                        <span key={i} className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                          {interestLabel(i)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
              <p className="mt-3 text-sm text-slate-300">{explanations[c.profile_id] ?? "Cargando explicación..."}</p>
              <button
                onClick={() => match(c.profile_id)}
                className="mt-3 w-full rounded-md bg-violet-600 px-3 py-1.5 text-sm font-medium text-white"
              >
                Match
              </button>
            </>
          )}
        </div>
      ))}
    </div>
  );
}

export default function DiscoverPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 py-10 pb-24 text-slate-100">
      <Suspense>
        <DiscoverContent />
      </Suspense>
      <AppNav />
    </main>
  );
}
