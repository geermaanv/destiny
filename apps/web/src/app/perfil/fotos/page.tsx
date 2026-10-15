"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Page, PageTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import { apiUrl, deletePhoto, getPhotos, Photos, setPrincipalPhoto, uploadPhoto } from "@/lib/api";
import { shrinkPhoto } from "@/lib/photo";

// Tus fotos (spec A11): hasta 4; la principal es la que se ve en Descubrir.
function TusFotos() {
  const profileId = useSessionProfileId();
  const fromDiscover = useSearchParams().get("desde") === "descubrir";
  const [data, setData] = useState<Photos | null>(null);
  const [menu, setMenu] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // La principal se sirve siempre en la misma URL: se fuerza a recargarla cuando cambia.
  const [version, setVersion] = useState(0);
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!profileId) return;
    getPhotos(profileId)
      .then(setData)
      .catch(() => setError("No pudimos cargar tus fotos. Probá de nuevo."));
  }, [profileId]);

  async function run(action: () => Promise<Photos>) {
    setError(null);
    setMenu(null);
    try {
      setData(await action());
      setVersion((v) => v + 1);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function handleFile(file: File) {
    if (!profileId) return;
    setUploading(true);
    await run(async () => uploadPhoto(profileId, await shrinkPhoto(file)));
    setUploading(false);
    if (fileInput.current) fileInput.current.value = "";
  }

  if (!profileId || (!data && !error)) return <p className="text-slate-400">Cargando…</p>;

  const photos = data?.photos ?? [];
  const max = data?.max ?? 4;
  const empty = Math.max(0, max - photos.length);

  return (
    <>
      <PageTitle
        title="Tus fotos"
        subtitle={`Hasta ${max}. La principal es la que se ve en Descubrir; las demás, al abrir tu perfil.`}
        back={fromDiscover ? { href: "/discover", label: "Descubrir" } : { href: "/perfil", label: "Mi perfil" }}
      />
      <input
        ref={fileInput}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
      <div className="grid grid-cols-2 gap-3">
        {photos.map((p) => (
          <div key={p.id} className="relative aspect-[3/4] overflow-hidden rounded-xl bg-slate-900 ring-1 ring-slate-700">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={`${apiUrl(p.url)}?v=${version}`} alt="" className="h-full w-full object-cover" />
            {p.principal && (
              <span className="absolute left-2 top-2 rounded-full bg-slate-950/80 px-2 py-0.5 text-xs text-gold-200">Principal</span>
            )}
            <button
              type="button"
              aria-label="Opciones de la foto"
              onClick={() => setMenu(menu === p.id ? null : p.id)}
              className="absolute right-2 top-2 rounded-full bg-slate-950/80 px-2 text-lg leading-6 text-slate-200"
            >
              ⋯
            </button>
            {menu === p.id && (
              <div className="absolute right-2 top-10 z-10 overflow-hidden rounded-md bg-slate-900 text-sm ring-1 ring-slate-700">
                {!p.principal && (
                  <button
                    type="button"
                    onClick={() => run(() => setPrincipalPhoto(profileId, p.id))}
                    className="block w-full whitespace-nowrap px-3 py-2 text-left hover:bg-slate-800"
                  >
                    Usar como principal
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => confirm("¿Borrar esta foto?") && run(() => deletePhoto(profileId, p.id))}
                  className="block w-full px-3 py-2 text-left text-red-400 hover:bg-slate-800"
                >
                  Borrar
                </button>
              </div>
            )}
          </div>
        ))}
        {Array.from({ length: empty }, (_, i) => (
          <button
            key={i}
            type="button"
            disabled={uploading}
            onClick={() => fileInput.current?.click()}
            className="flex aspect-[3/4] flex-col items-center justify-center gap-1 rounded-xl border border-dashed border-slate-600 bg-slate-900/80 text-sm text-slate-400 hover:border-slate-400 disabled:opacity-60"
          >
            {uploading && i === 0 ? (
              "Revisando la foto…"
            ) : (
              <>
                <span className="text-2xl">+</span>
                Agregar
              </>
            )}
          </button>
        ))}
      </div>
      {error && <p className="text-sm text-gold-300">{error}</p>}
      <p className="text-xs text-slate-500">
        Cada foto se revisa automáticamente al subirla: sin desnudos, violencia ni menores, y en la principal tiene que verse
        una persona.
      </p>
    </>
  );
}

export default function FotosPage() {
  return (
    <Page>
      <Suspense>
        <TusFotos />
      </Suspense>
    </Page>
  );
}
