"use client";

import { useEffect, useState } from "react";
import BirthSky from "@/components/BirthSky";
import { getMe, getStyle } from "@/lib/api";
import { applyLook, Look, onLookChange, savedLook } from "@/lib/theme";

// Aplica el estilo visual de la persona con sesión (spec X2 v2 y v3): primero el
// recordado en el dispositivo (sin parpadeo), después el de la API por si cambió.
export default function ThemeApplier() {
  const [look, setLook] = useState<Look | null>(null);

  useEffect(() => {
    const off = onLookChange(setLook);
    const saved = savedLook();
    if (saved) applyLook(saved, false);
    getMe()
      .then((me) => (me ? getStyle(me.id) : null))
      .then((style) => style && applyLook(style))
      .catch(() => null);
    return off;
  }, []);

  return look?.fondo && look.cielo?.length ? <BirthSky cielo={look.cielo} modo={look.modo} /> : null;
}
