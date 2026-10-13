"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// Barra de navegación inferior de la app (después del onboarding). El perfil
// sale de la sesión (spec A5), así que los links no llevan profileId.
// Spec U1-A: Hoy · Mi carta · Descubrir · Conexiones · Perfil. `also` = rutas que
// cuentan como esa pestaña (el calendario es parte de Hoy, el chat de Conexiones).
const ITEMS = [
  { href: "/home", label: "Hoy", icon: "☾", also: ["/calendario"] },
  { href: "/carta", label: "Mi carta", icon: "☉", also: [] },
  { href: "/discover", label: "Descubrir", icon: "✦", also: [] },
  { href: "/conexiones", label: "Conexiones", icon: "✉", also: ["/chat"] },
  { href: "/perfil", label: "Perfil", icon: "◉", also: ["/perfil/", "/invitar"] },
];

export default function AppNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 border-t border-slate-800 bg-slate-950/95 backdrop-blur">
      <ul className="mx-auto flex max-w-sm justify-around px-2 pb-[env(safe-area-inset-bottom)]">
        {ITEMS.map((item) => {
          const active = pathname === item.href || item.also.some((p) => pathname.startsWith(p));
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`flex flex-col items-center gap-0.5 px-2 py-2 text-xs ${
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

