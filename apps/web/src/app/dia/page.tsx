"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import AskBox from "@/components/AskBox";
import { Card, ListCard, Page, PageTitle, SectionTitle } from "@/components/ui";
import { useSessionProfileId } from "@/lib/session";
import { DayDetail, getMyDayDetail } from "@/lib/api";

// Tu día completo (spec B4 v3): el motor calcula clima, tránsitos y áreas; la IA redacta la lectura.
const STATE = {
  fluye: { label: "Fluye", className: "text-gold-300" },
  cuidado: { label: "Pide cuidado", className: "text-violet-400" },
  tranquilo: { label: "Tranquilo", className: "text-slate-400" },
};
const ASPECTS: Record<string, string> = {
  conjuncion: "conjunción", sextil: "sextil", cuadratura: "cuadratura", trigono: "trígono", oposicion: "oposición",
};
const NAMES: Record<string, string> = {
  sol: "Sol", luna: "Luna", mercurio: "Mercurio", venus: "Venus", marte: "Marte", jupiter: "Júpiter",
  saturno: "Saturno", urano: "Urano", neptuno: "Neptuno", pluton: "Plutón", asc: "Ascendente", mc: "Medio Cielo",
};

const pad = (n: number) => String(n).padStart(2, "0");
const isoLocal = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const dayLabel = (iso: string) => {
  const [y, m, d] = iso.split("-").map(Number);
  const s = new Date(y, m - 1, d).toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long" });
  return s.charAt(0).toUpperCase() + s.slice(1);
};
const shortDay = (iso: string) => iso.split("-").reverse().slice(0, 2).join("/");

function Dia() {
  const profileId = useSessionProfileId();
  const [detail, setDetail] = useState<DayDetail | null>(null);
  const [error, setError] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!profileId) return;
    getMyDayDetail(profileId, isoLocal(new Date())).then(setDetail).catch(() => setError(true));
  }, [profileId]);

  if (error) return <p className="text-slate-400">No pudimos leer tu día. Probá de nuevo en un rato.</p>;
  if (!profileId || !detail) return <p className="text-slate-400">Leyendo tu cielo de hoy…</p>;
  const { luna } = detail;

  return (
    <>
      <PageTitle title="Tu día" subtitle={dayLabel(detail.date)} back={{ href: "/home", label: "Hoy" }} />

      <section className="space-y-2">
        <SectionTitle>
          {luna.fase} en {luna.signo}
        </SectionTitle>
        <Card className="space-y-2">
          {luna.casa && (
            <p className="text-sm text-slate-400">
              Pasa por tu casa {luna.casa}: el foco está en {luna.tema_casa}.
            </p>
          )}
          <p className="leading-relaxed text-slate-200">{detail.lectura.texto}</p>
          <p className="text-sm italic text-gold-300">{detail.pregunta}</p>
        </Card>
      </section>

      <section className="space-y-2">
        <SectionTitle>Tu día por área</SectionTitle>
        <ListCard>
          {detail.areas.map((a) => (
            <div key={a.clave} className="flex items-start justify-between gap-3 px-4 py-3">
              <div>
                <p className="text-sm text-slate-100">{a.nombre}</p>
                {a.motivo && <p className="text-xs text-slate-400">{a.motivo}</p>}
              </div>
              <span className={`shrink-0 text-sm ${STATE[a.estado].className}`}>{STATE[a.estado].label}</span>
            </div>
          ))}
        </ListCard>
      </section>

      <section className="space-y-2">
        <SectionTitle action={<button type="button" onClick={() => setOpen(!open)} className="text-violet-400">{open ? "Ocultar" : "En qué se basa →"}</button>}>
          Tus tránsitos de hoy
        </SectionTitle>
        {detail.transitos.length === 0 ? (
          <p className="text-sm text-slate-400">Hoy no hay tránsitos fuertes sobre tu carta: un día para ir a tu ritmo.</p>
        ) : (
          <ListCard>
            {detail.transitos.map((t) => (
              <div key={`${t.planeta}-${t.punto}`} className="px-4 py-3">
                <p className="text-sm text-slate-100">{t.texto}</p>
                {open && (
                  <p className="text-xs text-slate-400">
                    {NAMES[t.planeta]} en {ASPECTS[t.aspecto]} con tu {NAMES[t.punto]} · orbe {t.orbe.toFixed(1)}°
                    {t.exacto ? ` · exacto el ${shortDay(t.exacto)}` : ""}
                  </p>
                )}
              </div>
            ))}
          </ListCard>
        )}
        {detail.aproximado && (
          <p className="text-xs text-gold-300">
            Sin tu hora exacta no vemos tus casas, tu Ascendente ni tu Medio Cielo.{" "}
            <Link href={`/onboarding/datos-natales?profileId=${profileId}&editar=1`} className="underline">
              Cargar la hora
            </Link>
          </p>
        )}
      </section>

      <AskBox
        title="Consultá sobre tu día"
        hint="Preguntá lo que quieras sobre lo que te trae hoy."
        example="¿Qué me conviene hacer hoy con lo que trae mi día?"
      />

    </>
  );
}

export default function DiaPage() {
  return (
    <Page>
      <Suspense>
        <Dia />
      </Suspense>
    </Page>
  );
}
