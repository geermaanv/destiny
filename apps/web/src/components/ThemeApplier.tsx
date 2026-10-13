"use client";

import { useEffect, useState } from "react";
import BirthSky from "@/components/BirthSky";
import { getMe, getStyle } from "@/lib/api";
import { applyLook, Look, onLookChange, savedLook } from "@/lib/theme";

// Aplica el estilo visual de la persona con sesión (spec X2 v2 y v3): primero el
// recordado en el dispositivo (sin parpadeo), después el de la API por si cambió.
// También maneja "Ver fondo": oculta el contenido hasta tocar la pantalla.
export default function ThemeApplier() {
  const [look, setLook] = useState<Look | null>(null);
  const [peek, setPeek] = useState(false);

  useEffect(() => {
    const off = onLookChange(setLook);
    const saved = savedLook();
    if (saved) applyLook(saved, false);
    getMe()
      .then((me) => (me ? getStyle(me.id) : null))
      .then((style) => style && applyLook(style))
      .catch(() => null);
    const onPeek = () => setPeek(true);
    window.addEventListener("destiny-peek", onPeek);
    return () => {
      off();
      window.removeEventListener("destiny-peek", onPeek);
    };
  }, []);

  const fondo = look?.fondo && typeof look.fondo === "string" ? look.fondo : "constelacion";
  const sky = Boolean(look?.cielo?.length) && fondo !== "ninguno";
  // Con fondo, el color pasa al <body>, las pantallas quedan transparentes y las tarjetas
  // semitransparentes (globals.css).
  useEffect(() => {
    document.documentElement.classList.toggle("sky-on", sky);
  }, [sky]);
  useEffect(() => {
    document.documentElement.classList.toggle("peek", peek);
  }, [peek]);

  return (
    <>
      {sky && look && <BirthSky cielo={look.cielo} elementos={look.elementos} fondo={fondo} />}
      {peek && (
        <button
          type="button"
          onClick={() => setPeek(false)}
          className="fixed inset-0 z-[100] flex items-end justify-center pb-10 text-sm text-slate-300"
        >
          Tocá para volver
        </button>
      )}
    </>
  );
}
