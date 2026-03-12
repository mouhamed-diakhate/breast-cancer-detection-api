/**
 * Skeleton.tsx — Placeholder animé pour le chargement des données.
 */

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
  style?: React.CSSProperties;
}

export function Skeleton({
  width = "100%",
  height = 20,
  borderRadius = 8,
  style,
}: SkeletonProps) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius,
        background:
          "linear-gradient(90deg, var(--color-tertiary) 25%, var(--color-border) 50%, var(--color-tertiary) 75%)",
        backgroundSize: "200% 100%",
        animation: "shimmer 1.6s linear infinite",
        ...style,
      }}
    />
  );
}
