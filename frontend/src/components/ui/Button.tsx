/**
 * Button.tsx — Bouton réutilisable avec variantes et états de chargement.
 */

"use client";

import { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: ReactNode;
}

const VARIANTS = {
  primary: {
    background: "var(--color-primary)",
    color: "#ffffff",
    border: "1.5px solid var(--color-primary)",
  },
  secondary: {
    background: "var(--color-secondary)",
    color: "var(--color-primary)",
    border: "1.5px solid var(--color-secondary)",
  },
  ghost: {
    background: "transparent",
    color: "var(--color-primary)",
    border: "1.5px solid var(--color-border)",
  },
};

const SIZES = {
  sm: { padding: "0.5rem 0.875rem", fontSize: "0.8125rem", height: 36 },
  md: { padding: "0.625rem 1.25rem", fontSize: "0.875rem", height: 42 },
  lg: { padding: "0.75rem 1.75rem", fontSize: "0.9375rem", height: 50 },
};

export function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  disabled,
  style,
  className,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      disabled={isDisabled}
      className={clsx("group", className)}
      style={{
        ...VARIANTS[variant],
        ...SIZES[size],
        borderRadius: "var(--radius-button)",
        fontFamily: "var(--font-body)",
        fontWeight: 500,
        cursor: isDisabled ? "not-allowed" : "pointer",
        opacity: isDisabled ? 0.55 : 1,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "0.5rem",
        transition: "all 0.2s ease",
        outline: "none",
        letterSpacing: "0.01em",
        whiteSpace: "nowrap",
        ...style,
      }}
      onMouseEnter={(e) => {
        if (isDisabled) return;
        const el = e.currentTarget;
        if (variant === "primary") {
          el.style.background = "#1a1a1a";
          el.style.boxShadow = "0 4px 16px rgba(0,0,0,0.2)";
          el.style.transform = "translateY(-1px)";
        } else if (variant === "secondary") {
          el.style.boxShadow = "var(--shadow-glow)";
          el.style.transform = "translateY(-1px)";
        } else {
          el.style.background = "var(--color-tertiary)";
          el.style.transform = "translateY(-1px)";
        }
      }}
      onMouseLeave={(e) => {
        const el = e.currentTarget;
        if (variant === "primary") {
          el.style.background = "var(--color-primary)";
          el.style.boxShadow = "none";
        } else if (variant === "secondary") {
          el.style.boxShadow = "none";
        } else {
          el.style.background = "transparent";
        }
        el.style.transform = "translateY(0)";
      }}
      {...rest}
    >
      {loading ? (
        <Loader2
          size={size === "sm" ? 14 : size === "lg" ? 18 : 16}
          style={{ animation: "spin 1s linear infinite" }}
        />
      ) : (
        icon
      )}
      {children}
    </button>
  );
}
