import { Fondo, resetLook } from "@/lib/theme";
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

export type BirthTimePeriod = "madrugada" | "manana" | "mediodia" | "tarde" | "noche";

export type BirthDataPayload = {
  birth_date: string;
  birth_time?: string;
  birth_time_period?: BirthTimePeriod;
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
  // Perfil liviano (spec A4)
  display_name: string | null;
  bio: string | null;
  neighborhood: string | null;
  energy_period: EnergyPeriod | null;
  interests: Interest[];
  avatar: AvatarKey | null;
  has_photo: boolean;
  sun_sign: string | null;
  verification_status: string;
  // Spec B8: género y a quién ver en Descubrir ("pareja").
  gender: Gender | null;
  gender_detail: string | null;
  show_me: Gender[];
  appear_in: ("mujer" | "hombre")[];
  show_gender: boolean;
  // Spec B9: dónde vive (solo lo ve su dueño).
  residence_label: string | null;
  residence_lat: number | null;
  residence_lon: number | null;
  // Spec A12
  privacy_version: string | null;
  test_privacy_version: string | null;
  looking_for: RelationshipContext | null;
};

export function acceptPrivacy(profileId: string, contexto: "registro" | "test", version: string): Promise<Profile> {
  return postJson(`/profiles/${profileId}/privacy`, { version, contexto });
}

export function setLookingFor(profileId: string, lookingFor: RelationshipContext): Promise<Profile> {
  return postJson(`/profiles/${profileId}/looking-for`, { looking_for: lookingFor });
}

export function setResidence(profileId: string, place: Place): Promise<Profile> {
  return postJson(`/profiles/${profileId}/residence`, { query: place.label, lat: place.lat, lon: place.lon });
}

export type Gender = "mujer" | "hombre" | "no_binario";

export type PreferencesPayload = {
  gender: Gender | null;
  gender_detail: string | null;
  show_me: Gender[];
  appear_in: ("mujer" | "hombre")[];
  show_gender: boolean;
};

export function setPreferences(profileId: string, payload: PreferencesPayload): Promise<Profile> {
  return postJson(`/profiles/${profileId}/preferences`, payload);
}

export type EnergyPeriod = "madrugada" | "manana" | "tarde" | "noche";
export type Interest =
  | "musica" | "deporte" | "arte" | "tecnologia" | "viajes" | "espiritualidad"
  | "lectura" | "cine" | "naturaleza" | "cocina" | "emprendimientos" | "juegos";
export type AvatarKey =
  | "signo" | "luna" | "sol" | "estrella" | "planeta" | "fuego" | "ola" | "hoja" | "mariposa" | "rayo";

export type BasicInfoPayload = {
  display_name: string;
  energy_period: EnergyPeriod | null;
  interests: Interest[];
  bio: string | null;
  neighborhood: string | null;
  avatar: AvatarKey | null;
};

export async function getProfile(profileId: string): Promise<Profile> {
  const res = await fetch(`${API_URL}/profiles/${profileId}`);
  if (!res.ok) throw new Error("No se pudo cargar el perfil");
  return res.json();
}

export function setBasicInfo(profileId: string, payload: BasicInfoPayload): Promise<Profile> {
  return postJson(`/profiles/${profileId}/basic-info`, payload);
}

// Fotos del perfil (spec A11): hasta 4, la primera es la principal.
export type Photo = { id: string; url: string; principal: boolean };
export type Photos = { photos: Photo[]; max: number };

async function photosResponse(res: Response): Promise<Photos> {
  if (!res.ok) {
    // 422 trae el motivo del chequeo automático ("Esta foto no se puede usar: …").
    const detail = await res.json().then((b) => (typeof b.detail === "string" ? b.detail : null)).catch(() => null);
    throw new Error(detail ?? (res.status === 413 ? "La foto no puede pesar más de 5 MB" : "No se pudo subir la foto"));
  }
  return res.json();
}

export async function getPhotos(profileId: string): Promise<Photos> {
  return photosResponse(await fetch(`${API_URL}/profiles/${profileId}/photos`));
}

export async function uploadPhoto(profileId: string, photo: Blob): Promise<Photos> {
  const formData = new FormData();
  formData.append("photo", photo, "foto.jpg");
  return photosResponse(await fetch(`${API_URL}/profiles/${profileId}/photos`, { method: "POST", body: formData }));
}

export async function deletePhoto(profileId: string, photoId: string): Promise<Photos> {
  return photosResponse(await fetch(`${API_URL}/profiles/${profileId}/photos/${photoId}`, { method: "DELETE" }));
}

export async function setPrincipalPhoto(profileId: string, photoId: string): Promise<Photos> {
  return photosResponse(await fetch(`${API_URL}/profiles/${profileId}/photos/${photoId}/principal`, { method: "POST" }));
}

// photo_url viene relativo a la API (ej. "/profiles/{id}/photo").
export function apiUrl(path: string): string {
  return `${API_URL}${path}`;
}

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
  claim_token: string;
};

export type Mood = "energico" | "tranquilo" | "reflexivo" | "ansioso" | "inspirado";

// Con la fecha local, así coincide con "Tu día" (de noche, en UTC ya es mañana).
export async function getTodayAstroWeather(localDate?: string): Promise<{ astro_weather: string; date: string }> {
  const res = await fetch(`${API_URL}/home/today${localDate ? `?date=${localDate}` : ""}`);
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
  compatibility_pct: number; // = global_pct
  // Spec B9: número global (promedio de los sistemas incluidos), sus ejes y cada sistema.
  global_pct: number;
  axes_global: Partial<Record<AxisKey, number | null>>;
  systems: { astrologia: SystemScore | null; personalidad: SystemScore | null };
  distance_km: number | null;
  common_interests: Interest[]; // spec B10
  astrology_pct: number;
  preview: string;
  axes: Partial<Record<"atraccion" | "afecto" | "comunicacion" | "compromiso", number>>;
  relationship: RelationshipContext | null;
  approximate: boolean;
  verificado?: boolean;
  personality: PersonalityCompat | null;
  display_name: string | null;
  age: number | null;
  sun_sign: string | null;
  photo_url: string | null;
  photos: string[];
  gender_label: string | null;
  avatar: AvatarKey | null;
  energy_period: EnergyPeriod | null;
  interests: Interest[];
  bio: string | null;
  neighborhood: string | null;
};

export type AxisKey = "atraccion" | "afecto" | "comunicacion" | "compromiso";
export type SystemScore = { total: number; axes: Partial<Record<AxisKey, number | null>> };
export type Sistema = "astrologia" | "personalidad";

// Filtros de Descubrir (specs B8 y B9).
export type DiscoverFilters = {
  context: RelationshipContext;
  sistemas: Sistema[];
  min_pct: number;
  edad_min: number;
  edad_max: number;
  max_km: number | null;
  intereses: Interest[]; // spec B10: tiene que tener todos
};

// Contexto de relación en Descubrir (spec B5): cambia los pesos de cada eje.
export type RelationshipContext = "pareja" | "amistad" | "laboral" | "ocasional";

export async function getDiscoverCandidates(
  viewerId: string,
  filters: DiscoverFilters,
  q?: string
): Promise<DiscoverCandidate[]> {
  const params = new URLSearchParams({
    viewer_id: viewerId,
    context: filters.context,
    sistemas: filters.sistemas.join(","),
    min_pct: String(filters.min_pct),
    edad_min: String(filters.edad_min),
    edad_max: String(filters.edad_max),
  });
  if (filters.max_km !== null) params.set("max_km", String(filters.max_km));
  if (filters.intereses.length > 0) params.set("intereses", filters.intereses.join(","));
  if (q?.trim()) params.set("q", q.trim());
  const res = await fetch(`${API_URL}/discover?${params.toString()}`);
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
}

export async function getExplanation(
  viewerId: string,
  candidateId: string,
  context: RelationshipContext = "pareja"
): Promise<{ text: string }> {
  const res = await fetch(`${API_URL}/discover/${candidateId}/explanation?viewer_id=${viewerId}&context=${context}`);
  if (!res.ok) throw new Error("No se pudo cargar la explicación");
  return res.json();
}

export type CalendarDay = { date: string; has_key_transit: boolean };
// Las notas del día se sacaron (spec U2).
export type CalendarDayDetail = {
  transits: { aspect: string; title: string | null; text: string | null }[];
};

export type UpcomingEvent = {
  start: string;
  end: string;
  aspect: string;
  title: string;
  text: string;
};

export async function getUpcoming(profileId: string, fromDate: string, limit = 10): Promise<UpcomingEvent[]> {
  const res = await fetch(`${API_URL}/calendar/upcoming?profile_id=${profileId}&from=${fromDate}&limit=${limit}`);
  if (!res.ok) throw new Error("No se pudieron cargar los próximos eventos");
  return res.json();
}

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

export type ChatMessage = { sender: string; text: string; created_at: string };

// Conexión mutua + chat híbrido (spec B7 v2).
export type ConnectionStatus = "pendiente" | "aceptada" | "rechazada" | "bloqueada";

export function createMatch(
  profileAId: string,
  profileBId: string
): Promise<{ id: string; icebreaker: string; status: ConnectionStatus }> {
  return postJson("/matches", { profile_a_id: profileAId, profile_b_id: profileBId });
}

export type Connection = {
  match_id: string;
  status: ConnectionStatus;
  direction: "enviada" | "recibida";
  other: {
    profile_id: string;
    display_name: string | null;
    age: number | null;
    sun_sign: string | null;
    photo_url: string | null;
    avatar: AvatarKey | null;
  };
  last_message: string | null;
  last_message_at: string | null;
  whatsapp: { me_ok: boolean; other_ok: boolean; link: string | null };
};

export async function getConnections(profileId: string): Promise<Connection[]> {
  const res = await fetch(`${API_URL}/connections?profile_id=${profileId}`);
  if (!res.ok) throw new Error("No se pudieron cargar las conexiones");
  return res.json();
}

export async function getConnection(matchId: string): Promise<Connection> {
  const res = await fetch(`${API_URL}/matches/${matchId}`);
  if (!res.ok) throw new Error("No se pudo cargar la conexión");
  return res.json();
}

export function respondConnection(
  matchId: string,
  profileId: string,
  action: "accept" | "reject" | "block" | "whatsapp"
): Promise<Connection> {
  return postJson(`/matches/${matchId}/${action}`, { profile_id: profileId });
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
  "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
  "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
] as const;

export type InvitationKind = "astro" | "test";

export type Invitation = {
  ref_id: string;
  kind: InvitationKind;
  whatsapp_url: string;
  message: string;
  partial_report: { teaser: string; locked_fields: string[] } | null;
};

export function createInvitation(
  inviterId: string,
  friendName: string,
  options: { kind: InvitationKind; friendSunSign?: string; relationship?: RelationshipContext }
): Promise<Invitation> {
  return postJson("/invitations", {
    inviter_id: inviterId,
    friend_name: friendName,
    kind: options.kind,
    friend_sun_sign: options.friendSunSign,
    relationship: options.relationship,
  });
}

export type InvitationPreload = {
  ref_id: string;
  friend_name: string;
  teaser: string;
  kind: InvitationKind;
  inviter_name: string | null;
  relationship: RelationshipContext | null;
};

// C8 v2: el invitado (ya con sesión) queda conectado con quien lo invitó.
export function acceptInvitation(refId: string): Promise<{ match_id: string }> {
  return postJson(`/invitations/${refId}/accept`);
}

export type MyInvitation = {
  ref_id: string;
  friend_name: string;
  kind: InvitationKind;
  relationship: RelationshipContext | null;
  status: "enviada" | "registrado" | "test_completo";
  match_id: string | null;
  created_at: string;
};

export async function getMyInvitations(profileId: string): Promise<MyInvitation[]> {
  const res = await fetch(`${API_URL}/invitations/mine?profile_id=${profileId}`);
  if (!res.ok) throw new Error("No se pudieron cargar tus invitaciones");
  return res.json();
}

// Panel "Compatibilidad" del chat (B7): astrología y personalidad por separado.
export type Compatibility = {
  relationship: RelationshipContext;
  astrology: { total: number; axes: Record<"atraccion" | "afecto" | "comunicacion" | "compromiso", number>; approximate: boolean };
  personality: PersonalityCompat | null;
};

export async function getCompatibility(matchId: string, context?: RelationshipContext): Promise<Compatibility> {
  const res = await fetch(`${API_URL}/matches/${matchId}/compatibility${context ? `?context=${context}` : ""}`);
  if (!res.ok) throw new Error("No se pudo cargar la compatibilidad");
  return res.json();
}

export async function getInvitation(refId: string): Promise<InvitationPreload> {
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
export function continueWithExistingProfile(profileId: string, claimToken: string): Promise<{ profile_id: string }> {
  return postJson(`/profiles/${profileId}/verification/continue-existing`, { claim_token: claimToken });
}

// Solo modo mock (sin credenciales de WhatsApp): simula el mensaje que Meta
// mandaría al webhook cuando el usuario envía el código.
export function simulateWhatsappMessage(fromPhone: string, text: string): Promise<void> {
  return postJson("/webhooks/whatsapp", {
    object: "whatsapp_business_account",
    entry: [{ changes: [{ value: { messages: [{ from: fromPhone, type: "text", text: { body: text } }] } }] }],
  });
}

// Sesión con WhatsApp (spec A5). La cookie la maneja el navegador (HttpOnly).
export async function getMe(): Promise<Profile | null> {
  const res = await fetch(`${API_URL}/me`);
  if (res.status === 401) return null;
  if (!res.ok) throw new Error("No se pudo consultar la sesión");
  return res.json();
}

export async function claimSession(claimToken: string): Promise<void> {
  const res = await fetch(`${API_URL}/sessions/claim`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ claim_token: claimToken }),
  });
  if (!res.ok) throw new Error("No se pudo iniciar la sesión");
}

export type LoginStart = {
  login_id: string;
  code: string;
  wa_link: string;
  expires_at: string;
  claim_token: string;
  mock: boolean;
};

export function startLogin(): Promise<LoginStart> {
  return postJson("/sessions/login");
}

export async function getLoginStatus(loginId: string): Promise<"pendiente" | "listo" | "sin_cuenta" | "vencido"> {
  const res = await fetch(`${API_URL}/sessions/login/${loginId}`);
  if (!res.ok) throw new Error("No se pudo consultar el login");
  return (await res.json()).status;
}

export async function logout(): Promise<void> {
  await fetch(`${API_URL}/sessions/logout`, { method: "POST" });
  resetLook(); // el estilo es de la persona: al salir vuelve el clásico (spec X2 v2)
}

// Test de personalidad de Pablo (spec A6).
export type PersonalityQuestion = { id: string; axis: "E1" | "E2" | "E3" | "E4"; kind: string; question: string; options: string[] };
export type PersonalityTest = {
  version: string;
  max_choices: number;
  axes: Record<string, { title: string; short: string; caption: string }>;
  questions: PersonalityQuestion[];
};
export type MyPersonality = {
  answers: Record<string, number[]>;
  completed: number;
  total_questions: number;
  axis_order: ("E1" | "E2" | "E3" | "E4")[]; // spec A12: según lo que busca
  privacy_accepted: boolean;
};
export type PersonalityCompat = {
  axes: Record<"E1" | "E2" | "E3" | "E4", number | null>;
  coverage: Record<string, number>;
  flags: string[];
  total: number | null;
  complete: boolean;
};

export async function getPersonalityTest(): Promise<PersonalityTest> {
  const res = await fetch(`${API_URL}/personality/test`);
  if (!res.ok) throw new Error("No se pudo cargar el test");
  return res.json();
}

export async function getMyPersonality(profileId: string): Promise<MyPersonality> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/personality`);
  if (!res.ok) throw new Error("No se pudieron cargar tus respuestas");
  return res.json();
}

export async function savePersonality(profileId: string, answers: Record<string, number[]>): Promise<MyPersonality> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/personality`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
  if (!res.ok) throw new Error("No se pudo guardar la respuesta");
  return res.json();
}

// "Tu día" (spec B4 v2): tránsito personal de hoy, texto de la biblioteca fija.
export type MyDay = { date: string; aspect: string; is_major: boolean; moon_sign: string; title: string; text: string; reviewed: boolean };

export async function getMyDay(profileId: string, date: string): Promise<MyDay> {
  const res = await fetch(`${API_URL}/home/my-day?profile_id=${profileId}&date=${date}`);
  if (!res.ok) throw new Error("No se pudo cargar tu día");
  return res.json();
}

// Hiperpersonalización (spec X2): cómo le habla Destiny a cada persona, según su carta.
export type Registro = "directo" | "practico" | "analitico" | "intuitivo";

export type Style = {
  registro: Registro;
  tono: "contenedor" | "liviano";
  formato: "acciones" | "profundidad" | "opciones";
  source: "carta" | "elegido";
  por_que: string;
  registro_carta: Registro;
  tema: Tema;
  tema_carta: Tema;
  tema_source: "carta" | "elegido";
  tema_por_que: string;
  elementos: Record<string, number>;
  paleta: Record<string, Record<string, string>>;
  modo: "oscuro" | "claro";
  acento: string;
  tipografia: string;
  fondo: Fondo;
  cielo: { punto: string; lon: number }[];
  cielo_leyenda: string;
};

export type Tema = "fuego" | "tierra" | "aire" | "agua" | "clasico";

export async function getStyle(profileId: string): Promise<Style> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/style`);
  if (!res.ok) throw new Error("No se pudo cargar tu estilo");
  return res.json();
}

// Solo cambia lo que se manda; null en registro o tema = que decida la carta.
export type StyleChange = {
  registro?: Registro | null;
  tema?: Tema | null;
  modo?: "oscuro" | "claro";
  fondo?: Fondo;
};

export async function setStyle(profileId: string, change: StyleChange): Promise<Style> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/style`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(change),
  });
  if (!res.ok) throw new Error("No se pudo guardar tu estilo");
  return res.json();
}

// Mi carta por dimensiones (spec A8).
export type NatalFoundation = {
  tipo: "signo" | "casa" | "aspecto";
  punto: string;
  signo?: string | null;
  casa?: number | null;
  otro?: string | null;
  aspecto?: string | null;
  texto: string;
};

export type NatalDimension = {
  clave: string;
  nombre: string;
  pregunta: string;
  fundamentos: NatalFoundation[];
  preguntas: string[];
  faltan_por_hora: string[];
};

export type NatalDimensions = { aproximado: boolean; falta?: "hora" | "lugar" | null; cielo: { punto: string; lon: number }[]; dimensiones: NatalDimension[] };

export async function getNatalDimensions(profileId: string): Promise<NatalDimensions> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/natal/dimensions`);
  if (!res.ok) throw new Error("No se pudo cargar tu carta");
  return res.json();
}

export async function getNatalSynthesis(profileId: string, clave: string): Promise<{ texto: string; ia: boolean }> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/natal/dimensions/${clave}/synthesis`);
  if (!res.ok) throw new Error("No se pudo cargar la síntesis");
  return res.json();
}

// Compartir mi carta con un link (spec A9).
export type ShareStatus = { activo: boolean; token?: string | null; vistas: number };

export type PublicCarta = {
  nombre: string;
  signos: { sol: string; luna: string; asc?: string };
  cielo: { punto: string; lon: number }[];
  dimensiones: { clave: string; nombre: string; pregunta: string; sintesis: string }[];
  paleta: Record<string, Record<string, string>>;
  tipografia: string;
  fondo: Fondo;
  elementos: Record<string, number>;
};

export async function createShare(profileId: string): Promise<ShareStatus> {
  return postJson(`/profiles/${profileId}/share`);
}

export async function getShare(profileId: string): Promise<ShareStatus> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/share`);
  if (!res.ok) throw new Error("No se pudo cargar el estado de compartir");
  return res.json();
}

export async function deleteShare(profileId: string): Promise<void> {
  await fetch(`${API_URL}/profiles/${profileId}/share`, { method: "DELETE" });
}

// Tu día completo (spec B4 v3).
export type DayDetail = {
  date: string;
  luna: { signo: string; fase: string; casa?: number | null; tema_casa?: string | null };
  transitos: { planeta: string; punto: string; aspecto: string; orbe: number; fuerza: number; exacto?: string | null; texto: string }[];
  areas: { clave: string; nombre: string; estado: "fluye" | "cuidado" | "tranquilo"; motivo?: string | null }[];
  lectura: { texto: string; ia: boolean };
  pregunta: string;
  aproximado: boolean;
  falta?: "hora" | "lugar" | null;
};

export async function getMyDayDetail(profileId: string, date: string): Promise<DayDetail> {
  const res = await fetch(`${API_URL}/home/my-day/detail?profile_id=${profileId}&date=${date}`);
  if (!res.ok) throw new Error("No se pudo cargar tu día");
  return res.json();
}

// Astrochat (spec X3).
export type AstroMessage = { rol: "persona" | "destiny"; texto: string; modo: string; creado: string };
export type Astrochat = {
  modo: string;
  modos: { clave: string; nombre: string; descripcion: string }[];
  mensajes: AstroMessage[];
  restantes_hoy: number;
  limite: number;
  ejemplos: string[];
};

export async function getAstrochat(profileId: string): Promise<Astrochat> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/astrochat`);
  if (!res.ok) throw new Error("No se pudo cargar el Astrochat");
  return res.json();
}

export async function askAstrochat(
  profileId: string,
  texto: string,
  modo?: string,
  dia?: string, // spec U2: pregunta sobre un día del calendario (YYYY-MM-DD)
): Promise<{ respuesta: AstroMessage; ia: boolean; restantes_hoy: number }> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/astrochat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto, modo, dia }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(typeof body?.detail === "string" ? body.detail : "No pudimos enviar tu pregunta");
  }
  return res.json();
}

export async function clearAstrochat(profileId: string): Promise<void> {
  await fetch(`${API_URL}/profiles/${profileId}/astrochat`, { method: "DELETE" });
}

// Verificación opcional (spec A10): al terminar el registro se inicia la sesión en el
// dispositivo, sin WhatsApp. Devuelve "verificacion" si la verificación es obligatoria.
export async function startSession(profileId: string): Promise<"ok" | "verificacion"> {
  const res = await fetch(`${API_URL}/sessions/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_id: profileId }),
  });
  if (res.ok) return "ok";
  const body = await res.json().catch(() => null);
  if (body?.detail === "verificacion_obligatoria") return "verificacion";
  throw new Error(typeof body?.detail === "string" ? body.detail : "No pudimos terminar tu registro");
}

