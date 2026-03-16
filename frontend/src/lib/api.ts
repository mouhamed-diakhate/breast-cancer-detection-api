/**
 * api.ts — Axios client centralisé pour toutes les requêtes vers le backend.
 * Base URL : http://localhost:5000/api/
 */

import axios from "axios";

// Instance Axios configurée
export const api = axios.create({
  baseURL: "http://localhost:5000/api/",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// --- Types ---

export interface HealthResponse {
  status: "healthy" | "unhealthy";
  model_loaded: boolean;
  version: string;
}

export interface ModelInfoResponse {
  architecture: string;
  classes: string[];
  device: string;
  input_shape: string;
  output_shape: string;
  status: string;
  total_params: number;
  trainable_params: number;
}

export interface ModelEntry {
  id: string;
  name: string;
  architecture: string;
  loaded: boolean;
}

export interface AnalyzeResponse {
  gradcam_image: string;          // data:image/png;base64,...
  original_filename: string;
  model_used?: string;
  prediction: {
    confidence: number;
    predicted_class: string;
    probabilities: Record<string, number>;
  };
}

// --- Fonctions API ---

/** GET /health — Vérification de l'état du serveur */
export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>("health");
  return data;
}

/** GET /model/info — Informations sur le modèle chargé */
export async function getModelInfo(): Promise<ModelInfoResponse> {
  const { data } = await api.get<ModelInfoResponse>("model/info");
  return data;
}

/** GET /models — Liste des modèles disponibles */
export async function getModels(): Promise<ModelEntry[]> {
  const { data } = await api.get<ModelEntry[]>("models");
  return data;
}

/** POST /analyze — Analyse d'une image (multipart/form-data) */
export async function analyzeImage(file: File, modelId?: string): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("file", file);
  if (modelId) {
    form.append("model", modelId);
  }
  const { data } = await api.post<AnalyzeResponse>("analyze", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
