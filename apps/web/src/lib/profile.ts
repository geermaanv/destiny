// Etiquetas del perfil liviano (spec A4). Los valores coinciden con la API.
import type { AvatarKey, EnergyPeriod, Interest } from "@/lib/api";

export const ENERGY_PERIODS: { value: EnergyPeriod; label: string; icon: string }[] = [
  { value: "madrugada", label: "Madrugada", icon: "🌌" },
  { value: "manana", label: "Mañana", icon: "🌅" },
  { value: "tarde", label: "Tarde", icon: "☀️" },
  { value: "noche", label: "Noche", icon: "🌙" },
];

export const INTERESTS: { value: Interest; label: string }[] = [
  { value: "musica", label: "Música" },
  { value: "deporte", label: "Deporte" },
  { value: "arte", label: "Arte" },
  { value: "tecnologia", label: "Tecnología" },
  { value: "viajes", label: "Viajes" },
  { value: "espiritualidad", label: "Espiritualidad" },
  { value: "lectura", label: "Lectura" },
  { value: "cine", label: "Cine" },
  { value: "naturaleza", label: "Naturaleza" },
  { value: "cocina", label: "Cocina" },
  { value: "emprendimientos", label: "Emprendimientos" },
  { value: "juegos", label: "Juegos" },
];
export const MAX_INTERESTS = 5;

export const AVATARS: { value: AvatarKey; emoji: string }[] = [
  { value: "signo", emoji: "" }, // se reemplaza por el glifo del signo
  { value: "luna", emoji: "🌙" },
  { value: "sol", emoji: "☀️" },
  { value: "estrella", emoji: "⭐" },
  { value: "planeta", emoji: "🪐" },
  { value: "fuego", emoji: "🔥" },
  { value: "ola", emoji: "🌊" },
  { value: "hoja", emoji: "🌿" },
  { value: "mariposa", emoji: "🦋" },
  { value: "rayo", emoji: "⚡" },
];

const SIGN_GLYPHS: Record<string, string> = {
  Aries: "♈", Tauro: "♉", Géminis: "♊", Gemini: "♊", Cáncer: "♋", Leo: "♌", Virgo: "♍",
  Libra: "♎", Escorpio: "♏", Sagitario: "♐", Capricornio: "♑", Acuario: "♒", Piscis: "♓",
};

export function avatarEmoji(avatar: AvatarKey | null, sunSign: string | null): string {
  if (avatar && avatar !== "signo") return AVATARS.find((a) => a.value === avatar)?.emoji ?? "✦";
  return (sunSign && SIGN_GLYPHS[sunSign]) || "✦";
}

export const energyLabel = (value: EnergyPeriod | null) => ENERGY_PERIODS.find((e) => e.value === value);
export const interestLabel = (value: Interest) => INTERESTS.find((i) => i.value === value)?.label ?? value;
