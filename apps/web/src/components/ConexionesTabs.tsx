"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { segmentClass, SEGMENTS } from "@/components/ui";

// Mis conexiones (spec U1, nombres de German): Descubrir y los chats en una sola
// pestaña, con el gancho como título y dos solapas.
const TABS = [
  { href: "/discover", label: "Descubrir" },
  { href: "/conexiones", label: "Mis chats" },
];

export default function ConexionesTabs() {
  const pathname = usePathname();
  return (
    <header className="space-y-3">
      <h1 className="text-2xl font-semibold">¿Con quién fluye?</h1>
      <nav className={`${SEGMENTS} grid-cols-2`}>
        {TABS.map((t) => (
          <Link
            key={t.href}
            href={t.href}
            aria-current={pathname === t.href ? "page" : undefined}
            className={segmentClass(pathname === t.href)}
          >
            {t.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
