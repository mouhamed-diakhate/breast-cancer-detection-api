/**
 * Navbar.tsx — Barre de navigation principale.
 * Design translucide avec effet glass, logo et liens de navigation.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, ScanSearch } from "lucide-react";

const NAV_LINKS = [
  { href: "/", label: "Tableau de bord", icon: Activity },
  { href: "/analyze", label: "Analyse", icon: ScanSearch },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 100,
        borderBottom: "1px solid rgba(232,226,213,0.8)",
      }}
      className="glass"
    >
      <div
        style={{
          maxWidth: 1200,
          margin: "0 auto",
          padding: "0 1.5rem",
          height: 64,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "2rem",
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.625rem",
            textDecoration: "none",
            flexShrink: 0,
          }}
        >
          <span
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: "var(--color-primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8 1L15 4.5V11.5L8 15L1 11.5V4.5L8 1Z"
                stroke="#f5c518"
                strokeWidth="1.5"
                strokeLinejoin="round"
              />
              <circle cx="8" cy="8" r="2.5" fill="#f5c518" />
            </svg>
          </span>
          <span
            style={{
              fontFamily: "var(--font-display)",
              fontWeight: 700,
              fontSize: "1.125rem",
              color: "var(--color-primary)",
              letterSpacing: "-0.01em",
            }}
          >
            BREAST CANCER DETECTION
          </span>
        </Link>

        {/* Navigation */}
        <nav
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.25rem",
          }}
        >
          {NAV_LINKS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  padding: "0.5rem 0.875rem",
                  borderRadius: "var(--radius-button)",
                  textDecoration: "none",
                  fontSize: "0.875rem",
                  fontWeight: active ? 600 : 400,
                  color: active ? "var(--color-primary)" : "var(--color-muted)",
                  background: active
                    ? "rgba(245,197,24,0.12)"
                    : "transparent",
                  border: active
                    ? "1px solid rgba(245,197,24,0.3)"
                    : "1px solid transparent",
                  transition: "all 0.2s ease",
                }}
              >
                <Icon size={15} />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
