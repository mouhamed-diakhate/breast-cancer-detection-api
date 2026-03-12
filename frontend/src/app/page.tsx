/**
 * page.tsx (Home) — Tableau de bord affichant l'état de l'API et les infos modèle.
 * Requêtes : GET /health  &  GET /model/info
 */

"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  Cpu,
  Database,
  Layers,
  RefreshCw,
  Server,
  Zap,
} from "lucide-react";

import { getHealth, getModelInfo, HealthResponse, ModelInfoResponse } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/ui/Skeleton";
import { StatRow } from "@/components/ui/StatRow";
import { Button } from "@/components/ui/Button";

// Formate un grand nombre avec séparateur
function formatNumber(n: number) {
  return n.toLocaleString("fr-FR");
}

export default function HomePage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [model, setModel] = useState<ModelInfoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, m] = await Promise.all([getHealth(), getModelInfo()]);
      setHealth(h);
      setModel(m);
      setLastUpdate(new Date());
    } catch {
      setError("Impossible de joindre le backend. Vérifiez que le serveur tourne sur http://localhost:5000.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  return (
    <div 
      className="bg-cover bg-center bg-fixed"
      style={{ backgroundImage: "url('/1.jpg')" }}
    >
      <div 
        className="min-h-screen flex items-center backdrop-blur-x justify-center px-4 py-12"
        style={{
          background: "linear-gradient(to bottom right, rgba(var(--color-rgb-bg-light), 0.8), rgba(var(--color-rgb-primary), 0.05))",
        }}
      >
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div 
            className="absolute top-20 right-10 w-72 h-72 rounded-full blur-3xl animate-float" 
            style={{
              background: "rgba(var(--color-rgb-tertiary), 0.1)",
            }}
          />
          <div 
            className="absolute bottom-20 left-10 w-96 h-96 rounded-full blur-3xl animate-float" 
            style={{ 
              animationDelay: '1s',
              background: "rgba(var(--color-rgb-primary), 0.1)",
            }} 
          />
        </div>
        <div
          style={{
          maxWidth: 1200,
          margin: "0 auto",
          padding: "3rem 1.5rem 4rem",
          width: "100%",
          position: "relative",
          zIndex: 10,
        }}
        >
      {/* En-tête */}
      <div
        className="animate-fade-up"
        style={{ marginBottom: "2.5rem" }}
      >
        <p
          style={{
            fontSize: "0.8125rem",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--color-muted)",
            marginBottom: "0.5rem",
            fontWeight: 500,
          }}
        >
          Tableau de bord
        </p>
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <h1
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "clamp(1.75rem, 4vw, 2.5rem)",
              fontWeight: 700,
              lineHeight: 1.15,
              letterSpacing: "-0.02em",
            }}
          >
            État du système
          </h1>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            {lastUpdate && (
              <span style={{ fontSize: "0.75rem", color: "var(--color-muted)" }}>
                Mis à jour à {lastUpdate.toLocaleTimeString("fr-FR")}
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchAll}
              loading={loading}
              icon={<RefreshCw size={14} />}
            >
              Actualiser
            </Button>
          </div>
        </div>
      </div>

      {/* Bannière d'erreur */}
      {error && (
        <div
          className="animate-fade-up"
          style={{
            marginBottom: "1.5rem",
            padding: "1rem 1.25rem",
            borderRadius: 12,
            background: "rgba(192,57,43,0.06)",
            border: "1px solid rgba(192,57,43,0.2)",
            color: "var(--color-danger)",
            fontSize: "0.875rem",
            display: "flex",
            alignItems: "center",
            gap: "0.625rem",
          }}
        >
          <Activity size={16} />
          {error}
        </div>
      )}

      {/* Grille principale */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "1.5rem",
          alignItems: "start",
        }}
      >
        {/* ---- Carte Santé API ---- */}
        <Card animate="animate-fade-up delay-100">
          <CardHeader>
            <span
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: "rgba(10,10,10)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Activity size={18} color="var(--color-secondary)" />
            </span>
            <div style={{ flex: 1 }}>
              <p
                style={{
                  fontSize: "0.8125rem",
                  color: "var(--color-muted)",
                  marginBottom: 2,
                }}
              >
                GET /health
              </p>
              <h2
                style={{
                  fontSize: "1rem",
                  fontWeight: 600,
                  fontFamily: "var(--font-display)",
                }}
              >
                Santé de l&rsquo;API
              </h2>
            </div>
            {health && (
              <StatusBadge status={health.status} />
            )}
          </CardHeader>
          <CardBody>
            {loading && !health ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem" }}>
                <Skeleton height={18} />
                <Skeleton height={18} width="70%" />
                <Skeleton height={18} width="85%" />
              </div>
            ) : health ? (
              <div>
                <StatRow
                  label="Statut"
                  value={<StatusBadge status={health.status} label={health.status} />}
                />
                <StatRow
                  label="Modèle chargé"
                  value={
                    <StatusBadge
                      status={health.model_loaded ? "loaded" : "error"}
                      label={health.model_loaded ? "Oui" : "Non"}
                    />
                  }
                />
                <StatRow label="Version" value={health.version} mono />
              </div>
            ) : (
              <p style={{ color: "var(--color-muted)", fontSize: "0.875rem" }}>
                Données indisponibles
              </p>
            )}
          </CardBody>
        </Card>

        {/* ---- Carte Infos modèle ---- */}
        <Card animate="animate-fade-up delay-200" style={{ gridRow: "span 2" }}>
          <CardHeader>
            <span
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: "rgba(10,10,10)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Cpu size={18} color="var(--color-secondary)" />
            </span>
            <div style={{ flex: 1 }}>
              <p
                style={{
                  fontSize: "0.8125rem",
                  color: "var(--color-muted)",
                  marginBottom: 2,
                }}
              >
                GET /model/info
              </p>
              <h2
                style={{
                  fontSize: "1rem",
                  fontWeight: 600,
                  fontFamily: "var(--font-display)",
                }}
              >
                Informations du modèle
              </h2>
            </div>
            {model && <StatusBadge status={model.status} label={model.status} />}
          </CardHeader>
          <CardBody>
            {loading && !model ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.875rem" }}>
                {[...Array(7)].map((_, i) => (
                  <Skeleton key={i} height={18} width={`${65 + (i % 3) * 10}%`} />
                ))}
              </div>
            ) : model ? (
              <div>
                <StatRow label="Architecture" value={model.architecture} mono />
                <StatRow label="Dispositif" value={
                  <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <Zap size={12} color="var(--color-secondary)" />
                    {model.device.toUpperCase()}
                  </span>
                } />
                <StatRow label="Forme d'entrée" value={model.input_shape} mono />
                <StatRow label="Forme de sortie" value={model.output_shape} mono />
                <StatRow label="Paramètres totaux" value={formatNumber(model.total_params)} mono />
                <StatRow label="Paramètres entraînables" value={formatNumber(model.trainable_params)} mono />

                {/* Classes */}
                <div style={{ marginTop: "1.25rem" }}>
                  <p
                    style={{
                      fontSize: "0.75rem",
                      textTransform: "uppercase",
                      letterSpacing: "0.08em",
                      color: "var(--color-muted)",
                      fontWeight: 500,
                      marginBottom: "0.75rem",
                    }}
                  >
                    Classes de prédiction
                  </p>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                    {model.classes.map((cls, i) => (
                      <span
                        key={cls}
                        style={{
                          padding: "0.375rem 0.875rem",
                          borderRadius: 999,
                          fontSize: "0.8125rem",
                          fontWeight: 500,
                          background: i === 0
                            ? "rgba(45,138,78,0.08)"
                            : "rgba(192,57,43,0.08)",
                          color: i === 0 ? "var(--color-success)" : "var(--color-danger)",
                          border: `1px solid ${i === 0 ? "rgba(45,138,78,0.2)" : "rgba(192,57,43,0.2)"}`,
                        }}
                      >
                        {cls}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p style={{ color: "var(--color-muted)", fontSize: "0.875rem" }}>
                Données indisponibles
              </p>
            )}
          </CardBody>
        </Card>

        {/* ---- Carte Accès rapide ---- */}
        <Card animate="animate-fade-up delay-300" glass>
          <CardBody>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                marginBottom: "1rem",
              }}
            >
              <span
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  background: "var(--color-primary)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <Layers size={18} color="var(--color-secondary)" />
              </span>
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--color-muted)" }}>
                  Démarrer
                </p>
                <h3
                  style={{
                    fontSize: "1rem",
                    fontWeight: 600,
                    fontFamily: "var(--font-display)",
                  }}
                >
                  Analyser une image
                </h3>
              </div>
            </div>
            <p
              style={{
                fontSize: "0.875rem",
                color: "var(--color-muted)",
                lineHeight: 1.6,
                marginBottom: "1.25rem",
              }}
            >
              Uploadez une image médicale et obtenez une prédiction instantanée avec
              la visualisation Grad-CAM.
            </p>
            <Button
              variant="primary"
              size="md"
              onClick={() => { window.location.href = "/analyze"; }}
              icon={<Server size={15} />}
              style={{ width: "100%" }}
            >
              Lancer une analyse
            </Button>
          </CardBody>
        </Card>

        {/* ---- Carte infos backend ---- */}
        <Card animate="animate-fade-up delay-400">
          <CardBody>
            <p
              style={{
                fontSize: "0.75rem",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "var(--color-muted)",
                fontWeight: 500,
                marginBottom: "0.75rem",
              }}
            >
              Connexion backend
            </p>
            <code
              style={{
                display: "block",
                padding: "0.75rem 1rem",
                borderRadius: 10,
                background: "var(--color-primary)",
                color: "var(--color-secondary)",
                fontFamily: "var(--font-mono)",
                fontSize: "0.8125rem",
                wordBreak: "break-all",
              }}
            >
              http://localhost:5000/api/
            </code>
          </CardBody>
        </Card>
      </div>
        </div>
      </div>
    </div>
  );
}
