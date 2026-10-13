"use client";

import { useEffect } from "react";
import { getMe, getStyle } from "@/lib/api";
import { applyPalette, applySavedPalette } from "@/lib/theme";

// Aplica el tema de la persona con sesión (spec X2 v2). Primero el recordado en el
// dispositivo (sin parpadeo), después el de la API por si cambió.
export default function ThemeApplier() {
  useEffect(() => {
    applySavedPalette();
    getMe()
      .then((me) => (me ? getStyle(me.id) : null))
      .then((style) => style && applyPalette(style.paleta))
      .catch(() => null);
  }, []);
  return null;
}
