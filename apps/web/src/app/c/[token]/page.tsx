import type { Metadata } from "next";
import { notFound } from "next/navigation";
import PublicCartaView from "@/components/PublicCartaView";
import type { PublicCarta } from "@/lib/api";

// Página pública de una carta compartida (spec A9). Se arma en el servidor para que
// WhatsApp muestre la vista previa (título y descripción con los signos y el gancho).
const API = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
const HOOK = "¿Por qué con algunas personas fluye y con otras no?";

async function load(token: string): Promise<PublicCarta | null> {
  const res = await fetch(`${API}/public/carta/${encodeURIComponent(token)}`, { cache: "no-store" });
  return res.ok ? res.json() : null;
}

function signLine(c: PublicCarta): string {
  return [`Sol en ${c.signos.sol}`, `Luna en ${c.signos.luna}`, c.signos.asc && `Ascendente en ${c.signos.asc}`]
    .filter(Boolean)
    .join(" · ");
}

export async function generateMetadata({ params }: { params: Promise<{ token: string }> }): Promise<Metadata> {
  const carta = await load((await params).token);
  if (!carta) return { title: "Destiny" };
  const title = `La carta de ${carta.nombre} en Destiny`;
  const description = `${signLine(carta)}. ${HOOK} Descubrí la tuya.`;
  return { title, description, openGraph: { title, description, siteName: "Destiny", images: ["/logo.png"] } };
}

export default async function PublicCartaPage({ params }: { params: Promise<{ token: string }> }) {
  const carta = await load((await params).token);
  if (!carta) notFound();
  return <PublicCartaView carta={carta} signLine={signLine(carta)} hook={HOOK} />;
}
