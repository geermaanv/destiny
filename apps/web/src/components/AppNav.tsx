"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// Barra de navegación inferior de la app (después del onboarding). El perfil
// sale de la sesión (spec A5), así que los links no llevan profileId.
// Hoy · Carta · Consulta · Red · Perfil (spec U1; palabras cortas elegidas por German;
// la calidez va en los títulos de cada pantalla). `also` = rutas que cuentan como esa pestaña.
const ITEMS = [
  { href: "/home", label: "Hoy", icon: "☾", also: ["/calendario", "/dia"] },
  { href: "/carta", label: "Carta", icon: "☉", also: [] },
  { href: "/astrochat", label: "Consulta", icon: "✧", also: [] },
  { href: "/discover", label: "Red", icon: "✦", also: ["/conexiones", "/chat"] },
  { href: "/perfil", label: "Perfil", icon: "◉", also: ["/perfil/", "/invitar"] },
];

export default function AppNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 border-t border-slate-800 bg-slate-950/95 backdrop-blur">
      <ul className="mx-auto flex max-w-md px-1 pb-[env(safe-area-inset-bottom)]">
        {ITEMS.map((item) => {
          const active = pathname === item.href || item.also.some((p) => pathname.startsWith(p));
          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`flex flex-col items-center gap-0.5 px-1 py-2 text-center text-[11px] leading-tight ${
                  active ? "text-gold-300" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                <span aria-hidden className="text-lg leading-none">
                  {item.icon + "\uFE0E"}
                </span>
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

