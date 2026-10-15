// Spec A11: la foto se achica en el navegador antes de subirla (lado mayor 1600 px,
// JPEG), así las del celular no pasan el límite de 5 MB y suben rápido.
const MAX_SIDE = 1600;
const QUALITY = 0.85;

export async function shrinkPhoto(file: File): Promise<Blob> {
  try {
    const bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
    const scale = Math.min(1, MAX_SIDE / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bitmap.width * scale);
    canvas.height = Math.round(bitmap.height * scale);
    canvas.getContext("2d")!.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    bitmap.close();
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", QUALITY));
    return blob ?? file;
  } catch {
    // Si el navegador no puede leerla (formato raro), se manda tal cual y la API decide.
    return file;
  }
}
