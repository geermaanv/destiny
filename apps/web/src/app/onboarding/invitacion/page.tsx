"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getInvitation } from "@/lib/api";

function InvitacionContent() {
  const router = useRouter();
  const ref = useSearchParams().get("ref");
  const [teaser, setTeaser] = useState<string | null>(null);

  useEffect(() => {
    if (!ref) return;
    getInvitation(ref).then((r) => setTeaser(r.teaser));
  }, [ref]);

  if (!ref) return <p className="text-slate-400">Link de invitación inválido.</p>;

  return (
    <div className="w-full max-w-sm space-y-5 text-center">
      <h1 className="text-2xl font-semibold">Te invitaron a Destiny</h1>
      <p className="text-slate-300">{teaser ?? "Cargando..."}</p>
      <button
        onClick={() => router.push(`/onboarding/datos-natales?ref=${ref}`)}
        className="w-full rounded-md bg-violet-600 px-3 py-2 font-medium text-white"
      >
        Completar mi carta y ver la revelación
      </button>
    </div>
  );
}

export default function InvitacionPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-6 text-slate-100">
      <Suspense>
        <InvitacionContent />
      </Suspense>
    </main>
  );
}
