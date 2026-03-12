/**
 * ImageDropzone.tsx — Zone de dépôt / sélection d'image avec prévisualisation.
 */

"use client";

import { useCallback, useRef, useState } from "react";
import { ImagePlus, X } from "lucide-react";

interface ImageDropzoneProps {
  onFileChange: (file: File | null) => void;
  preview: string | null;
}

export function ImageDropzone({ onFileChange, preview }: ImageDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = useCallback(
    (file: File | null) => {
      if (!file) return;
      if (!file.type.startsWith("image/")) return;
      onFileChange(file);
    },
    [onFileChange]
  );

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0] ?? null;
    handleFile(file);
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFile(e.target.files?.[0] ?? null);
  };

  const clear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onFileChange(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Zone de dépôt d'image"
      onClick={() => !preview && inputRef.current?.click()}
      onKeyDown={(e) => e.key === "Enter" && !preview && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      style={{
        position: "relative",
        width: "100%",
        minHeight: 260,
        borderRadius: "var(--radius-card)",
        border: dragging
          ? "2px dashed var(--color-secondary)"
          : "2px dashed var(--color-border)",
        background: dragging
          ? "rgba(245,197,24,0.04)"
          : "var(--color-surface)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: preview ? "default" : "pointer",
        transition: "border-color 0.2s ease, background 0.2s ease",
        overflow: "hidden",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={onInputChange}
        style={{ display: "none" }}
        aria-hidden
      />

      {preview ? (
        <>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={preview}
            alt="Aperçu de l'image sélectionnée"
            style={{
              width: "100%",
              height: "100%",
              objectFit: "contain",
              maxHeight: 320,
              padding: "0.75rem",
            }}
          />
          {/* Bouton effacer */}
          <button
            onClick={clear}
            aria-label="Supprimer l'image"
            style={{
              position: "absolute",
              top: 10,
              right: 10,
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "var(--color-primary)",
              color: "#fff",
              border: "none",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "opacity 0.2s",
            }}
          >
            <X size={14} />
          </button>
        </>
      ) : (
        <div
          style={{
            textAlign: "center",
            padding: "2rem 1.5rem",
          }}
        >
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: "rgba(245,197,24,0.1)",
              border: "1.5px solid rgba(245,197,24,0.25)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 1rem",
              transition: "transform 0.2s",
            }}
          >
            <ImagePlus size={24} color="var(--color-secondary)" />
          </div>
          <p
            style={{
              fontWeight: 500,
              fontSize: "0.9375rem",
              marginBottom: "0.375rem",
              color: "var(--color-primary)",
            }}
          >
            Déposez ou cliquez pour sélectionner
          </p>
          <p
            style={{
              fontSize: "0.8125rem",
              color: "var(--color-muted)",
            }}
          >
            PNG, JPG, WEBP acceptés
          </p>
        </div>
      )}
    </div>
  );
}
