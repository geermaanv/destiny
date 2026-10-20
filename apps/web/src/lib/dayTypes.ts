// Spec B11: tipo de día según el aspecto de la Luna con tu Sol. Colores fijos (no cambian con
// el tema) para que cada tipo se reconozca siempre igual. Tranquilo es la mayoría de los días:
// apenas un tinte, para que resalten los demás.
export type DayType = "fluye" | "desafia" | "intenso" | "tranquilo";

export const DAY_TYPES: Record<DayType, { label: string; cell: string; dot: string }> = {
  fluye: { label: "Fluye", cell: "bg-sky-500/30", dot: "bg-sky-400" },
  desafia: { label: "Desafía", cell: "bg-orange-500/30", dot: "bg-orange-400" },
  intenso: { label: "Intenso", cell: "bg-purple-500/35", dot: "bg-purple-400" },
  tranquilo: { label: "Tranquilo", cell: "bg-emerald-500/10", dot: "bg-emerald-400/60" },
};

export const DAY_TYPE_ORDER: DayType[] = ["fluye", "desafia", "intenso", "tranquilo"];
