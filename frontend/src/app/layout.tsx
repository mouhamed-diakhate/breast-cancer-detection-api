/**
 * layout.tsx — Layout racine de l'application MedVision.
 * Charge les polices Google, définit les métadonnées et la navigation principale.
 */

import type { Metadata } from "next";
import "../styles/globals.css";
import { Navbar } from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "BREAST CANCER DETECTION — Analyse d'images médicales",
  description:
    "Plateforme d'analyse d'images médicales par intelligence artificielle, basée sur ResNet18.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body
        style={{
          fontFamily: "var(--font-body)",
          backgroundColor: "var(--color-surface)",
          color: "var(--color-primary)",
          minHeight: "100vh",
        }}
      >
        {/* Fond décoratif global */}
        <div
          aria-hidden
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 0,
            pointerEvents: "none",
            background:
              "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(245,197,24,0.08) 0%, transparent 70%)",
          }}
        />

        <Navbar />

        <main style={{ position: "relative", zIndex: 1 }}>{children}</main>

        {/* Footer minimaliste */}
        {/* <footer
          style={{
            position: "relative",
            zIndex: 1,
            borderTop: "1px solid var(--color-border)",
            padding: "2rem 1.5rem",
            textAlign: "center",
            color: "var(--color-muted)",
            fontSize: "0.8125rem",
            fontFamily: "var(--font-body)",
          }}
        >
          MedVision &mdash; Analyse d&rsquo;images médicales par IA &mdash; ResNet18
        </footer> */}
      </body>
    </html>
  );
}
