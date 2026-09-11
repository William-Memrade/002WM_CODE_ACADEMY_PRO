import type { Metadata } from "next";
import "./globals.css";
import { PlatformTitle } from "@/components/PlatformTitle";

export const metadata: Metadata = {
  title: "CodeAcademy Pro — Academia Virtual de Programación",
  description:
    "Aprende programación con clases en vivo y pregrabadas. Cursos de Backend, Frontend, DevOps y más.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <PlatformTitle />
        {children}
      </body>
    </html>
  );
}
