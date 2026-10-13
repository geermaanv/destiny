import type { Metadata, Viewport } from "next";
import { Cormorant_Garamond, Josefin_Sans, Lora, Sora } from "next/font/google";
import "./globals.css";
import ThemeApplier from "@/components/ThemeApplier";

// Tipografías de títulos por tema (spec X2 v3); se elige con la variable --font-display.
const sora = Sora({ subsets: ["latin"], weight: ["600"], variable: "--font-sora", display: "swap" });
const lora = Lora({ subsets: ["latin"], weight: ["600"], variable: "--font-lora", display: "swap" });
const josefin = Josefin_Sans({ subsets: ["latin"], weight: ["600"], variable: "--font-josefin", display: "swap" });
const cormorant = Cormorant_Garamond({ subsets: ["latin"], weight: ["600"], variable: "--font-cormorant", display: "swap" });

export const metadata: Metadata = {
  title: "Destiny",
  description: "¿Por qué con algunas personas fluye y con otras no? Destiny lee tu carta natal para entenderte a vos y a tus vínculos.",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#25225b",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={`${sora.variable} ${lora.variable} ${josefin.variable} ${cormorant.variable}`}>
      <body>
        <ThemeApplier />
        {children}
      </body>
    </html>
  );
}
