// "/api" en vez de una URL absoluta: Next.js la proxea server-side a
// API_INTERNAL_URL (ver next.config.ts). Así el browser solo necesita
// llegar al origen de Next — un solo túnel alcanza para hostear
// (ver docs/decisions/0007-hosting-local-tunel.md). NEXT_PUBLIC_API_URL
// sigue existiendo como escape hatch si alguna vez se separan los hosts.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";

export type BirthPlace = {
  query: string;
  lat?: number;
  lon?: number;
  timezone?: string;
};

export type Place = {
  label: string;
  lat: number;
  lon: number;
  timezone: string;
};

export async function searchPlaces(query: string): Promise<Place[]> {
  const res = await fetch(`${API_URL}/geocoding/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("No se pudo buscar el lugar");
  return res.json();
}

export type BirthDataPayload = {
  birth_date: string;
  birth_time?: string;
  birth_place: BirthPlace;
};

export type NotificationRhythm = "ritmo_diario" | "pulso_cosmos";

export type Profile = {
  id: string;
  birth_date: string | null;
  birth_time: string | null;
  birth_time_estimated: boolean;
  birth_place_query: string | null;
  birth_place_lat: number | null;
  birth_place_lon: number | null;
  birth_place_timezone: string | null;
  notification_rhythm: NotificationRhythm | null;
};

async function postJson<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`Request failed: ${path}`);
  return res.json();
}

export function createProfile(): Promise<Profile> {
  return postJson<Profile>("/profiles");
}

export function setBirthData(profileId: string, payload: BirthDataPayload): Promise<Profile> {
  return postJson<Profile>(`/profiles/${profileId}/birth-data`, payload);
}

export function setNotificationPreference(profileId: string, rhythm: NotificationRhythm): Promise<Profile> {
  return postJson<Profile>(`/profiles/${profileId}/notification-preference`, { rhythm });
}

export type VerificationStatus = "pendiente" | "en_revision" | "verificado" | "rechazado" | "duplicado_detectado";

export type VerificationResult = {
  verification_id: string | null;
  status: VerificationStatus;
  method?: "whatsapp" | "kyc_video" | null;
};

export type WhatsappCode = {
  code: string;
  wa_link: string;
  expires_at: string;
  mock: boolean;
};

export type Mood = "energico" | "tranquilo" | "reflexivo" | "ansioso" | "inspirado";

export async function getTodayAstroWeather(): Promise<{ astro_weather: string; date: string }> {
  const res = await fetch(`${API_URL}/home/today`);
  if (!res.ok) throw new Error("No se pudo obtener el clima astrológico");
  return res.json();
}

export async function getFrequencyCount(profileId?: string): Promise<{ count: number }> {
  const query = profileId ? `?profile_id=${profileId}` : "";
  const res = await fetch(`${API_URL}/home/frequency-count${query}`);
  if (!res.ok) throw new Error("No se pudo obtener el contador de frecuencia");
  return res.json();
}

export function submitMoodCheckin(profileId: string, mood: Mood): Promise<void> {
  return postJson("/mood-checkins", { profile_id: profileId, mood });
}

export type DiscoverCandidate = {
  profile_id: string;
  compatibility_pct: number;
  preview: string;
};

export async function getDiscoverCandidates(viewerId: string): Promise<DiscoverCandidate[]> {
  const res = await fetch(`${API_URL}/discover?viewer_id=${viewerId}`);
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}

export async function getExplanation(viewerId: string, candidateId: string): Promise<{ text: string }> {
  const res = await fetch(`${API_URL}/discover/${candidateId}/explanation?viewer_id=${viewerId}`);
  if (!res.ok) throw new Error("No se pudo cargar la explicación");
  return res.json();
}

export type CalendarDay = { date: string; has_key_transit: boolean };
export type CalendarAnnotation = { text: string; created_at: string };
export type CalendarDayDetail = { transits: { aspect: string }[]; annotations: CalendarAnnotation[] };

export async function getMonth(profileId: string, year: number, month: number): Promise<CalendarDay[]> {
  const res = await fetch(`${API_URL}/calendar/${year}/${month}?profile_id=${profileId}`);
  if (!res.ok) throw new Error("No se pudo cargar el calendario");
  return res.json();
}

export async function getDay(profileId: string, day: string): Promise<CalendarDayDetail> {
  const res = await fetch(`${API_URL}/calendar/day/${day}?profile_id=${profileId}`);
  if (!res.ok) throw new Error("No se pudo cargar el día");
  return res.json();
}

export function addAnnotation(profileId: string, day: string, text: string): Promise<CalendarAnnotation> {
  return postJson(`/calendar/day/${day}/annotations`, { profile_id: profileId, text });
}

export type ChatMessage = { sender: string; text: string; created_at: string };

export function createMatch(profileAId: string, profileBId: string): Promise<{ id: string; icebreaker: string }> {
  return postJson("/matches", { profile_a_id: profileAId, profile_b_id: profileBId });
}

export async function getMessages(matchId: string): Promise<ChatMessage[]> {
  const res = await fetch(`${API_URL}/chats/${matchId}/messages`);
  if (!res.ok) throw new Error("No se pudieron cargar los mensajes");
  return res.json();
}

export function sendMessage(matchId: string, profileId: string, text: string): Promise<ChatMessage> {
  return postJson(`/chats/${matchId}/messages`, { profile_id: profileId, text });
}

export const SUN_SIGNS = [
  "Aries", "Tauro", "Gemini", "Cáncer", "Leo", "Virgo",
  "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
] as const;

export type Invitation = {
  ref_id: string;
  whatsapp_url: string;
  partial_report: { teaser: string; locked_fields: string[] };
};

export function createInvitation(inviterId: string, friendName: string, friendSunSign: string): Promise<Invitation> {
  return postJson("/invitations", { inviter_id: inviterId, friend_name: friendName, friend_sun_sign: friendSunSign });
}

export async function getInvitation(refId: string): Promise<{ ref_id: string; friend_name: string; teaser: string }> {
  const res = await fetch(`${API_URL}/invitations/${refId}`);
  if (!res.ok) throw new Error("No se pudo cargar la invitación");
  return res.json();
}

export async function revealInvitation(
  refId: string,
  inviteeId: string
): Promise<{ aspect: string; percentage: number; text: string }> {
  const res = await fetch(`${API_URL}/invitations/${refId}/reveal?invitee_id=${inviteeId}`);
  if (!res.ok) throw new Error("No se pudo revelar la compatibilidad");
  return res.json();
}

export async function startVerification(profileId: string, media: File): Promise<VerificationResult> {
  const formData = new FormData();
  formData.append("media", media);
  const res = await fetch(`${API_URL}/profiles/${profileId}/verification`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("No se pudo iniciar la verificación");
  return res.json();
}

// Verificación v1 por WhatsApp (spec A3, ADR 0008).
export function startWhatsappVerification(profileId: string): Promise<WhatsappCode> {
  return postJson(`/profiles/${profileId}/verification/whatsapp`);
}

export async function getVerification(profileId: string): Promise<VerificationResult> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/verification`);
  if (!res.ok) throw new Error("No se pudo consultar la verificación");
  return res.json();
}

// Tras duplicado_detectado: descarta el perfil nuevo y devuelve el que ya tiene ese número.
export function continueWithExistingProfile(profileId: string): Promise<{ profile_id: string }> {
  return postJson(`/profiles/${profileId}/verification/continue-existing`);
}

// Solo modo mock (sin credenciales de WhatsApp): simula el mensaje que Meta
// mandaría al webhook cuando el usuario envía el código.
export function simulateWhatsappMessage(fromPhone: string, text: string): Promise<void> {
  return postJson("/webhooks/whatsapp", {
    object: "whatsapp_business_account",
    entry: [{ changes: [{ value: { messages: [{ from: fromPhone, type: "text", text: { body: text } }] } }] }],
  });
}
