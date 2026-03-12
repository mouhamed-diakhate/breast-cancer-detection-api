/**
 * ProbabilityBar.tsx — Barre de probabilité animée pour les classes de prédiction.
 */

"use client";

import { useEffect, useState } from "react";

interface ProbabilityBarProps {
  label: string;
  value: number; // 0-1
  isPrimary?: boolean;
}

export function ProbabilityBar({ label, value, isPrimary = false }: ProbabilityBarProps) {
  const [width, setWidth] = useState(0);
  const pct = Math.round(value * 100);

  // Animation d'entrée
  useEffect(() => {
    const t = setTimeout(() => setWidth(pct), 80);
    return () => clearTimeout(t);
  }, [pct]);

  const isMalignant = label.toLowerCase() === "malignant";
  const barColor = isMalignant
    ? "var(--color-danger)"
    : "var(--color-success)";

  return (
    <div style={{ marginBottom: "0.875rem" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "0.375rem",
        }}
      >
        <span
          style={{
            fontSize: "0.875rem",
            fontWeight: isPrimary ? 600 : 400,
            color: isPrimary ? "var(--color-primary)" : "var(--color-muted)",
          }}
        >
          {label}
        </span>
        <span
          style={{
            fontSize: "0.875rem",
            fontWeight: 600,
            fontFamily: "var(--font-mono)",
            color: isPrimary ? barColor : "var(--color-muted)",
          }}
        >
          {pct}%
        </span>
      </div>
      {/* Track */}
      <div
        style={{
          height: 8,
          borderRadius: 999,
          background: "var(--color-border)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            borderRadius: 999,
            width: `${width}%`,
            background: barColor,
            transition: "width 0.7s cubic-bezier(0.16,1,0.3,1)",
            boxShadow: isPrimary ? `0 0 12px ${barColor}60` : "none",
          }}
        />
      </div>
    </div>
  );
}
