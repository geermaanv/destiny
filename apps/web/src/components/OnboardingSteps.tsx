import Link from "next/link";

// Indicador de pasos del registro (mejora #1 de la revisión): cuánto falta y
// cómo volver al paso anterior sin perder lo cargado.
const STEPS = ["Datos natales", "Perfil", "Avisos", "Verificación"];

export function onboardingHref(path: string, profileId: string | null, ref: string | null): string {
  const params = new URLSearchParams();
  if (profileId) params.set("profileId", profileId);
  if (ref) params.set("ref", ref);
  const query = params.toString();
  return query ? `${path}?${query}` : path;
}

export default function OnboardingSteps({ step, backHref }: { step: number; backHref?: string }) {
  return (
    <div className="w-full max-w-sm space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-400">
        {backHref ? (
          <Link href={backHref} className="text-slate-300 hover:text-white">
            ‹ Volver
          </Link>
        ) : (
          <span />
        )}
        <span>
          Paso {step} de {STEPS.length} · {STEPS[step - 1]}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-1.5" aria-hidden>
        {STEPS.map((label, i) => (
          <span key={label} className={`h-1 rounded-full ${i < step ? "bg-gold-400" : "bg-slate-800"}`} />
        ))}
      </div>
    </div>
  );
}
