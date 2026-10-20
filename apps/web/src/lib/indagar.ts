// Spec U2: link a Indagar con una pregunta sobre un día, que se manda sola y lleva los
// datos de ese día (desde el calendario y desde Próximos días de Hoy).
export function indagarDayHref(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const day = new Date(y, m - 1, d)
    .toLocaleDateString("es-AR", { weekday: "long", day: "numeric", month: "long" })
    .replace(",", "");
  return `/astrochat?q=${encodeURIComponent(`¿Qué significa para mí el ${day}?`)}&dia=${iso}&enviar=1`;
}
