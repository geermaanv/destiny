"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

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
      <nav className="grid grid-cols-2 gap-1 rounded-xl bg-slate-900 p-1 ring-1 ring-slate-700">
        {TABS.map((t) => (
          <Link
            key={t.href}
            href={t.href}
            aria-current={pathname === t.href ? "page" : undefined}
            className={`rounded-lg py-1.5 text-center text-sm ${
              pathname === t.href ? "bg-violet-600 text-white" : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            {t.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
