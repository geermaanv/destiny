"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import AppNav from "@/components/AppNav";
import { createMatch, DiscoverCandidate, getDiscoverCandidates, getExplanation } from "@/lib/api";

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
          <button onClick={() => openCandidate(c.profile_id)} className="flex w-full items-center justify-between text-left">
            <span>{c.preview}</span>
            <span className="font-semibold text-violet-300">{c.compatibility_pct}%</span>
          </button>
          {openId === c.profile_id && (
            <>
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
