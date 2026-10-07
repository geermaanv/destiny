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

export type Profile = {
  id: string;
  birth_date: string | null;
  birth_time: string | null;
  birth_time_estimated: boolean;
  birth_place_query: string | null;
  birth_place_lat: number | null;
  birth_place_lon: number | null;
  birth_place_timezone: string | null;
};

export async function createProfile(): Promise<Profile> {
  const res = await fetch(`${API_URL}/profiles`, { method: "POST" });
  if (!res.ok) throw new Error("No se pudo crear el perfil");
  return res.json();
}

export async function setBirthData(profileId: string, payload: BirthDataPayload): Promise<Profile> {
  const res = await fetch(`${API_URL}/profiles/${profileId}/birth-data`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("No se pudieron guardar los datos natales");
  return res.json();
}
