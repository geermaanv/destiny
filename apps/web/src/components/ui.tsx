import Link from "next/link";
import { ReactNode } from "react";
import AppNav from "@/components/AppNav";

// Sistema visual común (spec U1-E): mismas tarjetas, títulos, filas y espaciados
// en todas las pantallas. El borde dorado (`highlight`) es solo para lo destacado.

export function Page({ children, nav = true }: { children: ReactNode; nav?: boolean }) {
  return (
    <main className="flex min-h-screen flex-col items-center bg-slate-950 px-5 pb-28 pt-8 text-slate-100">
      <div className="w-full max-w-md space-y-6">{children}</div>
      {nav && <AppNav />}
    </main>
  );
}

// Solapas (Carta, Círculo): la seleccionada en un tono neutro, para no confundirse
// con los links de acción (pedido de German).
export function segmentClass(active: boolean): string {
  return `rounded-lg px-1 py-1.5 text-center text-xs ${active ? "bg-slate-700 text-white" : "text-slate-400 hover:bg-slate-800"}`;
}
export const SEGMENTS = "grid gap-1 rounded-xl bg-slate-900 p-1 ring-1 ring-slate-700";

export function PageTitle({
  title,
  subtitle,
  back,
  action,
}: {
  title: string;
  subtitle?: ReactNode;
  back?: { href: string; label: string };
  action?: ReactNode;
}) {
  return (
    <header className="space-y-1">
      {back && (
        <Link href={back.href} className="text-sm text-slate-400 hover:text-slate-200">
          ← {back.label}
        </Link>
      )}
      <div className="flex items-baseline justify-between gap-3">
        <h1 className="text-2xl font-semibold">{title}</h1>
        {action && <div className="shrink-0 text-sm">{action}</div>}
      </div>
      {subtitle && <div className="text-sm text-slate-400">{subtitle}</div>}
    </header>
  );
}

export function SectionTitle({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between">
      <h3 className="text-xs font-medium uppercase tracking-wide text-slate-400">{children}</h3>
      {action && <div className="text-sm">{action}</div>}
    </div>
  );
}

const CARD = "block rounded-xl bg-slate-900 p-4 ring-1";

export function Card({
  children,
  href,
  highlight = false,
  className = "",
}: {
  children: ReactNode;
  href?: string;
  highlight?: boolean;
  className?: string;
}) {
  const ring = highlight ? "ring-gold-400/50" : "ring-slate-700";
  const classes = `${CARD} ${ring} ${href ? "hover:ring-violet-400" : ""} ${className}`;
  return href ? (
    <Link href={href} className={classes}>
      {children}
    </Link>
  ) : (
    <div className={classes}>{children}</div>
  );
}

// Lista de filas dentro de una tarjeta (Perfil, accesos).
export function ListCard({ children }: { children: ReactNode }) {
  return <div className="divide-y divide-slate-800 overflow-hidden rounded-xl bg-slate-900 ring-1 ring-slate-700">{children}</div>;
}

export function ListRow({
  href,
  onClick,
  icon,
  title,
  detail,
}: {
  href?: string;
  onClick?: () => void;
  icon?: ReactNode;
  title: ReactNode;
  detail?: ReactNode;
}) {
  const body = (
    <>
      {icon && <span className="w-6 text-center text-lg text-gold-300">{typeof icon === "string" ? icon + "\uFE0E" : icon}</span>}
      <span className="flex-1">
        <span className="block text-sm text-slate-100">{title}</span>
        {detail && <span className="block text-xs text-slate-400">{detail}</span>}
      </span>
      <span className="text-slate-500">›</span>
    </>
  );
  const classes = "flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-slate-800/60";
  if (href)
    return (
      <Link href={href} className={classes}>
        {body}
      </Link>
    );
  return (
    <button type="button" onClick={onClick} className={classes}>
      {body}
    </button>
  );
}
