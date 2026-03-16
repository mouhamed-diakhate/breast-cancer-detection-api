/**
 * page.tsx (Analyze) — Page d'analyse d'image médicale.
 * Upload → POST /analyze → affichage prédiction + Grad-CAM.
 */

"use client";

import { useState, useEffect } from "react";
import { ScanSearch, FileImage, AlertCircle, CheckCircle2, XCircle, Cpu } from "lucide-react";

import { analyzeImage, getModels, AnalyzeResponse, ModelEntry } from "@/lib/api";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ImageDropzone } from "@/components/ui/ImageDropzone";
import { ProbabilityBar } from "@/components/ui/ProbabilityBar";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Skeleton } from "@/components/ui/Skeleton";

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Model selection
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [modelsLoading, setModelsLoading] = useState(true);

  useEffect(() => {
    getModels()
      .then((list) => {
        setModels(list);
        const first = list.find((m) => m.loaded) ?? list[0];
        if (first) setSelectedModel(first.id);
      })
      .catch(() => setModels([]))
      .finally(() => setModelsLoading(false));
  }, []);

  const handleFileChange = (f: File | null) => {
    setFile(f);
    setResult(null);
    setError(null);
    if (f) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target?.result as string);
      reader.readAsDataURL(f);
    } else {
      setPreview(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeImage(file, selectedModel || undefined);
      setResult(data);
    } catch (err: any) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError("Erreur lors de l'analyse. Vérifiez que le backend est disponible.");
      }
    } finally {
      setLoading(false);
    }
  };

  const isMalignant =
    result?.prediction.predicted_class.toLowerCase() === "malignant";
  const confidence = result
    ? Math.round(result.prediction.confidence * 100)
    : null;

  return (
    <div 
      className="bg-cover bg-center bg-fixed"
      style={{ backgroundImage: "url('/1.jpg')" }}
    >
      <div 
        className="min-h-screen flex items-center backdrop-blur-xl justify-center px-4 py-12"
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
      <div className="animate-fade-up" style={{ marginBottom: "2.5rem" }}>
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
          POST /analyze
        </p>
        <h1
          style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(1.75rem, 4vw, 2.5rem)",
            fontWeight: 700,
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
          }}
        >
          Analyse d&rsquo;image médicale
        </h1>
        <p
          style={{
            marginTop: "0.625rem",
            color: "var(--color-muted)",
            fontSize: "0.9375rem",
            maxWidth: 540,
          }}
        >
          Uploadez une image et obtenez une classification instantanée ainsi
          que la carte Grad-CAM de visualisation.
        </p>
      </div>

      {/* Grille principale */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
          gap: "1.5rem",
          alignItems: "start",
        }}
      >
        {/* ---- Colonne gauche : Upload ---- */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Dropzone */}
          <Card className="animate-fade-up delay-100">
            <CardHeader>
              <span
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  background: "rgba(245,197,24,0.12)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <FileImage size={18} color="var(--color-secondary)" />
              </span>
              <div>
                <h2
                  style={{
                    fontSize: "1rem",
                    fontWeight: 600,
                    fontFamily: "var(--font-display)",
                  }}
                >
                  Sélection de l&rsquo;image
                </h2>
                {file && (
                  <p
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--color-muted)",
                      marginTop: 2,
                    }}
                  >
                    {file.name}
                  </p>
                )}
              </div>
            </CardHeader>
            <CardBody>
              <ImageDropzone onFileChange={handleFileChange} preview={preview} />
            </CardBody>
          </Card>

          {/* Sélecteur de modèle */}
          <Card className="animate-fade-up delay-150">
            <CardHeader>
              <span
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  background: "rgba(245,197,24,0.12)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <Cpu size={18} color="var(--color-secondary)" />
              </span>
              <div>
                <h2
                  style={{
                    fontSize: "1rem",
                    fontWeight: 600,
                    fontFamily: "var(--font-display)",
                  }}
                >
                  Choisir le modèle
                </h2>
                {selectedModel && (
                  <p style={{ fontSize: "0.75rem", color: "var(--color-muted)", marginTop: 2 }}>
                    Sélectionné : <strong>{models.find((m) => m.id === selectedModel)?.name ?? selectedModel}</strong>
                  </p>
                )}
              </div>
            </CardHeader>
            <CardBody>
              {modelsLoading ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  <Skeleton height={56} borderRadius={12} />
                  <Skeleton height={56} borderRadius={12} />
                </div>
              ) : models.length === 0 ? (
                <p style={{ color: "var(--color-muted)", fontSize: "0.875rem" }}>
                  Impossible de charger les modèles. Vérifiez que le backend est disponible.
                </p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.625rem" }}>
                  {models.map((m) => {
                    const isSelected = selectedModel === m.id;
                    return (
                      <button
                        key={m.id}
                        onClick={() => setSelectedModel(m.id)}
                        disabled={!m.loaded}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.875rem",
                          padding: "0.875rem 1rem",
                          borderRadius: 12,
                          border: isSelected
                            ? "1.5px solid var(--color-secondary)"
                            : "1.5px solid var(--color-border)",
                          background: isSelected
                            ? "rgba(245,197,24,0.06)"
                            : "var(--color-tertiary)",
                          cursor: m.loaded ? "pointer" : "not-allowed",
                          opacity: m.loaded ? 1 : 0.5,
                          textAlign: "left",
                          transition: "all 0.18s ease",
                          width: "100%",
                        }}
                      >
                        {/* Radio circle */}
                        <span
                          style={{
                            width: 18,
                            height: 18,
                            borderRadius: "50%",
                            border: isSelected
                              ? "5px solid var(--color-secondary)"
                              : "2px solid var(--color-border)",
                            flexShrink: 0,
                            transition: "all 0.18s ease",
                          }}
                        />
                        <div>
                          <p
                            style={{
                              fontWeight: 600,
                              fontSize: "0.875rem",
                              color: isSelected ? "var(--color-secondary)" : "var(--color-primary)",
                              fontFamily: "var(--font-display)",
                            }}
                          >
                            {m.name}
                          </p>
                          <p
                            style={{
                              fontSize: "0.75rem",
                              color: "var(--color-muted)",
                              marginTop: 2,
                              fontFamily: "var(--font-mono)",
                            }}
                          >
                            {m.architecture} {!m.loaded && "· indisponible"}
                          </p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </CardBody>
          </Card>

          {/* Bouton analyser */}
          <Button
            variant="secondary"
            size="lg"
            onClick={handleAnalyze}
            disabled={!file || !selectedModel}
            loading={loading}
            icon={<ScanSearch size={18} />}
            style={{ width: "100%" }}
            className="animate-fade-up delay-200"
          >
            {loading ? "Analyse en cours..." : "Lancer l'analyse"}
          </Button>


          {/* Erreur */}
          {error && (
            <div
              className="animate-fade-up"
              style={{
                padding: "0.875rem 1rem",
                borderRadius: 12,
                background: "rgba(192,57,43,0.06)",
                border: "1px solid rgba(192,57,43,0.2)",
                color: "var(--color-danger)",
                fontSize: "0.875rem",
                display: "flex",
                alignItems: "flex-start",
                gap: "0.625rem",
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
              {error}
            </div>
          )}
        </div>

        {/* ---- Colonne droite : Résultats ---- */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>

          {/* Squelette pendant le chargement */}
          {loading && (
            <Card className="animate-fade-up">
              <CardBody>
                <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                  <Skeleton height={28} width="55%" />
                  <Skeleton height={16} />
                  <Skeleton height={16} width="80%" />
                  <Skeleton height={16} />
                  <div style={{ marginTop: "0.5rem" }}>
                    <Skeleton height={200} borderRadius={12} />
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Résultats réels */}
          {result && !loading && (
            <>
              {/* Carte prédiction principale */}
              <Card className="animate-fade-up">
                <CardHeader>
                  <span
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 10,
                      background: isMalignant
                        ? "rgba(192,57,43,0.08)"
                        : "rgba(45,138,78,0.08)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}
                  >
                    {isMalignant ? (
                      <XCircle size={18} color="var(--color-danger)" />
                    ) : (
                      <CheckCircle2 size={18} color="var(--color-success)" />
                    )}
                  </span>
                  <div style={{ flex: 1 }}>
                    <p
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--color-muted)",
                        marginBottom: 2,
                      }}
                    >
                      Prédiction
                    </p>
                    <h2
                      style={{
                        fontSize: "1rem",
                        fontWeight: 600,
                        fontFamily: "var(--font-display)",
                      }}
                    >
                      Résultat de l&rsquo;analyse
                    </h2>
                  </div>
                  <StatusBadge
                    status={isMalignant ? "error" : "healthy"}
                    label={result.prediction.predicted_class}
                  />
                </CardHeader>
                <CardBody>
                  {/* Fichier original */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      padding: "0.625rem 0.875rem",
                      borderRadius: 10,
                      background: "var(--color-tertiary)",
                      marginBottom: "1.25rem",
                    }}
                  >
                    <FileImage size={14} color="var(--color-muted)" />
                    <span
                      style={{
                        fontSize: "0.8125rem",
                        fontFamily: "var(--font-mono)",
                        color: "var(--color-primary)",
                        wordBreak: "break-all",
                      }}
                    >
                      {result.original_filename}
                    </span>
                  </div>

                  {/* Classe prédite + confiance */}
                  <div
                    style={{
                      textAlign: "center",
                      padding: "1.5rem 1rem",
                      borderRadius: 12,
                      background: isMalignant
                        ? "rgba(192,57,43,0.04)"
                        : "rgba(45,138,78,0.04)",
                      border: `1px solid ${isMalignant ? "rgba(192,57,43,0.15)" : "rgba(45,138,78,0.15)"}`,
                      marginBottom: "1.5rem",
                    }}
                  >
                    <p
                      style={{
                        fontFamily: "var(--font-display)",
                        fontSize: "2rem",
                        fontWeight: 700,
                        color: isMalignant
                          ? "var(--color-danger)"
                          : "var(--color-success)",
                        lineHeight: 1,
                        marginBottom: "0.375rem",
                      }}
                    >
                      {result.prediction.predicted_class}
                    </p>
                    <p
                      style={{
                        fontSize: "0.875rem",
                        color: "var(--color-muted)",
                      }}
                    >
                      Confiance&nbsp;
                      <strong
                        style={{
                          fontFamily: "var(--font-mono)",
                          color: "var(--color-primary)",
                        }}
                      >
                        {confidence}%
                      </strong>
                    </p>
                  </div>

                  {/* Probabilités par classe */}
                  <div>
                    <p
                      style={{
                        fontSize: "0.75rem",
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                        color: "var(--color-muted)",
                        fontWeight: 500,
                        marginBottom: "0.875rem",
                      }}
                    >
                      Probabilités
                    </p>
                    {Object.entries(result.prediction.probabilities).map(
                      ([cls, val]) => (
                        <ProbabilityBar
                          key={cls}
                          label={cls}
                          value={val}
                          isPrimary={
                            cls === result.prediction.predicted_class
                          }
                        />
                      )
                    )}
                  </div>
                </CardBody>
              </Card>

              {/* Carte Grad-CAM */}
              <Card className="animate-fade-up delay-200">
                <CardHeader>
                  <span
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 10,
                      background: "rgba(10,10,10,0.06)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}
                  >
                    <ScanSearch size={18} color="var(--color-primary)" />
                  </span>
                  <div>
                    <p
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--color-muted)",
                        marginBottom: 2,
                      }}
                    >
                      Explainabilité
                    </p>
                    <h2
                      style={{
                        fontSize: "1rem",
                        fontWeight: 600,
                        fontFamily: "var(--font-display)",
                      }}
                    >
                      Carte Grad-CAM
                    </h2>
                  </div>
                </CardHeader>
                <CardBody style={{ padding: "1rem" }}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={result.gradcam_image}
                    alt="Visualisation Grad-CAM"
                    style={{
                      width: "100%",
                      borderRadius: 10,
                      objectFit: "contain",
                      display: "block",
                      border: "1px solid var(--color-border)",
                    }}
                  />
                  <p
                    style={{
                      marginTop: "0.75rem",
                      fontSize: "0.75rem",
                      color: "var(--color-muted)",
                      textAlign: "center",
                      lineHeight: 1.6,
                    }}
                  >
                    Les zones en rouge indiquent les régions ayant le plus influencé la décision du modèle.
                  </p>
                </CardBody>
              </Card>
            </>
          )}

          {/* Placeholder vide */}
          {!result && !loading && !error && (
            <Card className="animate-fade-up delay-200" glass>
              <CardBody
                style={{
                  minHeight: 220,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  textAlign: "center",
                  gap: "0.75rem",
                }}
              >
                <div
                  style={{
                    width: 56,
                    height: 56,
                    borderRadius: 16,
                    background: "var(--color-tertiary)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <ScanSearch size={24} color="var(--color-muted)" />
                </div>
                <p
                  style={{ fontWeight: 500, color: "var(--color-primary)" }}
                >
                  Aucun résultat
                </p>
                <p
                  style={{
                    fontSize: "0.875rem",
                    color: "var(--color-muted)",
                    maxWidth: 260,
                  }}
                >
                  Sélectionnez une image et lancez l&rsquo;analyse pour voir les résultats ici.
                </p>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
        </div>
      </div>
    </div>
  );
}
