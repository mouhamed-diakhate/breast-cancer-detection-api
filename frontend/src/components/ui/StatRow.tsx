/**
 * StatRow.tsx — Ligne clé / valeur pour afficher des informations structurées.
 */

interface StatRowProps {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}

export function StatRow({ label, value, mono = false }: StatRowProps) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "0.625rem 0",
        borderBottom: "1px solid var(--color-border)",
        gap: "1rem",
      }}
    >
      <span
        style={{
          fontSize: "0.8125rem",
          color: "var(--color-muted)",
          fontWeight: 400,
          flexShrink: 0,
        }}
      >
        {label}
      </span>
      <span
        style={{
          fontSize: "0.875rem",
          fontWeight: 500,
          color: "var(--color-primary)",
          fontFamily: mono ? "var(--font-mono)" : "var(--font-body)",
          textAlign: "right",
          wordBreak: "break-all",
        }}
      >
        {value}
      </span>
    </div>
  );
}
