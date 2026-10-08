"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMe } from "@/lib/api";

// Sesión con WhatsApp (spec A5): las pantallas de la app toman el perfil de la
// sesión (cookie), no de la URL. Sin sesión → pantalla de inicio.
export function useSessionProfileId(): string | null {
  const router = useRouter();
  const [profileId, setProfileId] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then((me) => (me ? setProfileId(me.id) : router.replace("/")))
      .catch(() => router.replace("/"));
  }, [router]);

  return profileId;
}
