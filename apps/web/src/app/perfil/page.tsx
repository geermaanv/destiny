"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ProfileAvatar from "@/components/ProfileAvatar";
import { ListCard, ListRow, Page } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import { getMyPersonality, getProfile, getStyle, logout, MyPersonality, Profile, Style, SUN_SIGNS } from "@/lib/api";

// Perfil corto (spec U1-B): encabezado con los signos principales y una lista de
// filas, cada una a su pantalla.
function signOf(style: Style | null, point: string): string | null {
  const lon = style?.cielo.find((p) => p.punto === point)?.lon;
  return lon === undefined ? null : SUN_SIGNS[Math.floor(lon / 30) % 12];
}

function MiPerfil() {
  const router = useRouter();
  const profileId = useSessionProfileId();
  const [me, setMe] = useState<Profile | null>(null);
  const [style, setStyle] = useState<Style | null>(null);
  const [personality, setPersonality] = useState<MyPersonality | null>(null);
  const [confirmLogout, setConfirmLogout] = useState(false);

  useEffect(() => {
    if (!profileId) return;
    getProfile(profileId).then(setMe).catch(() => null);
    getStyle(profileId).then(setStyle).catch(() => null);
    getMyPersonality(profileId).then(setPersonality).catch(() => null);
  }, [profileId]);

  if (!profileId || !me) return <p className="text-slate-400">Cargando…</p>;

  const sun = signOf(style, "sol") ?? me.sun_sign;
  const moon = signOf(style, "luna");
  const asc = signOf(style, "asc");
  const signs = [sun && `☉ ${sun}`, moon && `☽ ${moon}`, asc && `AC ${asc}`].filter(Boolean).join(" · ");
  const birth = me.birth_date
    ? `${me.birth_date.split("-").reverse().join("/")} · ${me.birth_time_estimated ? "hora estimada" : `${me.birth_time?.slice(0, 5)} hs`}`
    : "Sin cargar";
  const testDetail = personality
    ? personality.completed === personality.total_questions
      ? "Completo"
      : `${personality.completed} de ${personality.total_questions} respuestas`
    : undefined;

  return (
    <>
      <header className="flex items-center gap-4">
        <ProfileAvatar
          photoUrl={me.has_photo ? `/profiles/${profileId}/photo` : null}
          avatar={me.avatar}
          sunSign={me.sun_sign}
          size={64}
        />
        <div>
          <h1 className="text-2xl font-semibold">{me.display_name ?? "Mi perfil"}</h1>
          {signs && <p className="text-sm text-gold-300">{signs}</p>}
        </div>
      </header>
      <ListCard>
        <ListRow href="/perfil/editar" icon="✎" title="Editar perfil" detail="Nombre, avatar, intereses, barrio, género" />
        <ListRow
          href="/perfil/fotos"
          icon="▣"
          title="Tus fotos"
          detail={me.has_photo ? "Hasta 4, la principal se ve en Descubrir" : "Subí una para aparecer en Descubrir"}
        />
        <ListRow
          href={`/onboarding/datos-natales?profileId=${profileId}&editar=1`}
          icon="✶"
          title="Datos de nacimiento"
          detail={birth}
        />
        <ListRow
          href="/perfil/estilo"
          icon="◐"
          title="Tu estilo"
          detail="Cómo te hablamos, colores, modo claro, fondo"
        />
        <ListRow href="/perfil/test" icon="✓" title="Test de personalidad" detail={testDetail} />
        <ListRow href="/invitar" icon="✉" title="Invitar a alguien" detail="A comparar el test o con un adelanto astrológico" />
      </ListCard>
      {/* Spec A10: la verificación por WhatsApp es opcional; acá se ofrece con sus beneficios. */}
      {me.verification_status !== "verificado" ? (
        <div className="space-y-2">
          <ListCard>
            <ListRow
              href={`/onboarding/verificacion?profileId=${profileId}`}
              icon="✓"
              title="Verificá tu WhatsApp"
              detail="Marca de verificado, entrar desde otro celular y pasar a WhatsApp"
            />
          </ListCard>
          <p className="text-xs text-slate-500">Tu cuenta vive en este dispositivo: verificá tu WhatsApp para no perderla.</p>
        </div>
      ) : (
        <p className="text-xs text-gold-300">✓{"\uFE0E"} WhatsApp verificado</p>
      )}
      {me.birth_place_lat === null && (
        <p className="text-xs text-gold-300">
          Tu ciudad no está elegida del buscador: no podemos calcular tu Ascendente ni tus casas. Abrí Datos de nacimiento y
          elegila de la lista.
        </p>
      )}
      <ListCard>
        <ListRow
          icon="⎋"
          title="Cerrar sesión"
          onClick={async () => {
            // Spec R3: cerrar sesión cierra de verdad; sin WhatsApp verificado, la cuenta se pierde.
            if (me.verification_status !== "verificado") {
              setConfirmLogout(true);
              return;
            }
            await logout();
            router.replace("/");
          }}
        />
      </ListCard>
      {confirmLogout && (
        <div className="space-y-3 rounded-xl bg-slate-900 p-4 ring-1 ring-gold-400/50">
          <p className="text-sm text-slate-200">
            Si cerrás sesión sin verificar tu WhatsApp, vas a perder tu cuenta: no hay otra forma de volver a entrar.
          </p>
          <a
            href={`/onboarding/verificacion?profileId=${profileId}`}
            className="block w-full rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-medium text-white"
          >
            Verificar ahora
          </a>
          <button
            onClick={async () => {
              await logout();
              router.replace("/");
            }}
            className="w-full text-center text-sm text-red-400 underline"
          >
            Cerrar igual
          </button>
        </div>
      )}
    </>
  );
}

export default function PerfilPage() {
  return (
    <Page>
      <Suspense>
        <MiPerfil />
      </Suspense>
    </Page>
  );
}
