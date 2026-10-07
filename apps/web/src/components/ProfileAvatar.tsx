import { apiUrl, AvatarKey } from "@/lib/api";
import { avatarEmoji } from "@/lib/profile";

// Foto si hay; si no, el avatar elegido (spec A4). Por defecto, el glifo del signo.
export default function ProfileAvatar({
  photoUrl,
  avatar,
  sunSign,
  size = 48,
}: {
  photoUrl: string | null;
  avatar: AvatarKey | null;
  sunSign: string | null;
  size?: number;
}) {
  const style = { width: size, height: size };
  if (photoUrl) {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={apiUrl(photoUrl)} alt="" style={style} className="shrink-0 rounded-full object-cover" />;
  }
  return (
    <span
      aria-hidden
      style={{ ...style, fontSize: size * 0.5 }}
      className="flex shrink-0 items-center justify-center rounded-full bg-violet-950 text-violet-200 ring-1 ring-violet-800"
    >
      {avatarEmoji(avatar, sunSign)}
    </span>
  );
}
