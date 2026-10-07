"use client";

import { Suspense } from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";

// Barra de navegación inferior de la app (después del onboarding). El perfil
// viaja en ?profileId= (todavía no hay sesión, ver BACKLOG), así que cada link lo conserva.
const ITEMS = [
  { href: "/home", label: "Inicio", icon: "☾" },
  { href: "/discover", label: "Descubrir", icon: "✦" },
  { href: "/calendario", label: "Calendario", icon: "▦" },
  { href: "/invitar", label: "Invitar", icon: "＋" },
  { href: "/perfil", label: "Perfil", icon: "◉" },
];

function NavLinks() {
  const pathname = usePathname();
  const profileId = useSearchParams().get("profileId");
  if (!profileId) return null;

  return (
    <nav className="fixed inset-x-0 bottom-0 border-t border-slate-800 bg-slate-950/95 backdrop-blur">
      <ul className="mx-auto flex max-w-sm justify-around px-2 pb-[env(safe-area-inset-bottom)]">
        {ITEMS.map((item) => {
          const active = pathname === item.href || (item.href === "/discover" && pathname.startsWith("/chat"));
          return (
            <li key={item.href}>
              <Link
                href={`${item.href}?profileId=${profileId}`}
                aria-current={active ? "page" : undefined}
                className={`flex flex-col items-center gap-0.5 px-2 py-2 text-xs ${
                  active ? "text-violet-300" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                <span aria-hidden className="text-lg leading-none">
                  {item.icon}
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

export default function AppNav() {
  return (
    <Suspense>
      <NavLinks />
    </Suspense>
  );
}
