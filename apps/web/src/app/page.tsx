import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 text-slate-100">
      <h1 className="text-3xl font-semibold">Destiny</h1>
      <p className="mt-2 text-slate-400">Scaffold inicial — en construcción.</p>
      <Link href="/onboarding/datos-natales" className="mt-6 text-violet-400 underline">
        Onboarding: datos natales
      </Link>
    </main>
  );
}
