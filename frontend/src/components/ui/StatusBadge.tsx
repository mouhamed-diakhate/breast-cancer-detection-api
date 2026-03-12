/**
 * StatusBadge.tsx — Badge d'état coloré (healthy/unhealthy/loaded/etc.)
 */

type Status = "healthy" | "unhealthy" | "loaded" | "error" | "warning";

interface StatusBadgeProps {
  status: Status | string;
  label?: string;
}

const STATUS_CONFIG: Record<string, { bg: string; color: string; dot: string }> =
  {
    healthy: {
      bg: "rgba(45,138,78,0.1)",
      color: "var(--color-success)",
      dot: "var(--color-success)",
    },
    loaded: {
      bg: "rgba(45,138,78,0.1)",
      color: "var(--color-success)",
      dot: "var(--color-success)",
    },
    unhealthy: {
      bg: "rgba(192,57,43,0.1)",
      color: "var(--color-danger)",
      dot: "var(--color-danger)",
    },
    error: {
      bg: "rgba(192,57,43,0.1)",
      color: "var(--color-danger)",
      dot: "var(--color-danger)",
    },
    warning: {
      bg: "rgba(245,197,24,0.15)",
      color: "#b8900a",
      dot: "var(--color-secondary)",
    },
  };

const DEFAULT_CONFIG = {
  bg: "rgba(107,101,96,0.1)",
  color: "var(--color-muted)",
  dot: "var(--color-muted)",
};

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? DEFAULT_CONFIG;
  const text = label ?? status;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.375rem",
        padding: "0.25rem 0.75rem",
        borderRadius: 999,
        background: config.bg,
        color: config.color,
        fontSize: "0.75rem",
        fontWeight: 600,
        letterSpacing: "0.04em",
        textTransform: "uppercase",
      }}
    >
      {/* Dot animé pour "healthy" */}
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: config.dot,
          display: "inline-block",
          animation:
            status === "healthy" || status === "loaded"
              ? "pulse-slow 2s ease-in-out infinite"
              : "none",
        }}
      />
      {text}
    </span>
  );
}
