const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type BirthPlace = {
  query: string;
  lat?: number;
  lon?: number;
  timezone?: string;
};

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
};

export type Mood = "energico" | "tranquilo" | "reflexivo" | "ansioso" | "inspirado";

export async function getTodayAstroWeather(): Promise<{ astro_weather: string; date: string }> {
  const res = await fetch(`${API_URL}/home/today`);
  if (!res.ok) throw new Error("No se pudo obtener el clima astrológico");
  return res.json();
}

export async function getFrequencyCount(): Promise<{ count: number }> {
  const res = await fetch(`${API_URL}/home/frequency-count`);
  if (!res.ok) throw new Error("No se pudo obtener el contador de frecuencia");
  return res.json();
}

export function submitMoodCheckin(profileId: string, mood: Mood): Promise<void> {
  return postJson("/mood-checkins", { profile_id: profileId, mood });
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
