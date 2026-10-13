import { redirect } from "next/navigation";

// Mi carta pasó a ser una pestaña propia (spec U1-A).
export default function PerfilCartaRedirect() {
  redirect("/carta");
}
