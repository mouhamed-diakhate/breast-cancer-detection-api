/**
 * Card.tsx — Composant carte réutilisable avec effet glass et animations.
 */

import { CSSProperties, ReactNode } from "react";
import clsx from "clsx";

interface CardProps {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  glass?: boolean;
  /** Classe d'animation + délai, ex: "animate-fade-up delay-200" */
  animate?: string;
}

export function Card({
  children,
  className,
  style,
  glass = false,
  animate,
}: CardProps) {
  return (
    <div
      className={clsx(animate, glass && "glass", className)}
      style={{
        borderRadius: "var(--radius-card)",
        border: glass
          ? undefined
          : "1px solid var(--color-border)",
        background: glass ? undefined : "var(--color-surface-elevated)",
        boxShadow: "var(--shadow-card)",
        overflow: "hidden",
        position: "relative",
        transition: "box-shadow 0.25s ease, transform 0.25s ease",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

/** Sous-composant CardHeader */
export function CardHeader({
  children,
  style,
}: {
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <div
      style={{
        padding: "1.25rem 1.5rem",
        borderBottom: "1px solid var(--color-border)",
        display: "flex",
        alignItems: "center",
        gap: "0.75rem",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

/** Sous-composant CardBody */
export function CardBody({
  children,
  style,
}: {
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <div style={{ padding: "1.5rem", ...style }}>{children}</div>
  );
}
