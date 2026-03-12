# Documentation API - Système de Détection du Cancer du Sein

## Vue d'ensemble

Cette API REST permet d'analyser des images mammographiques pour détecter des anomalies potentielles (bénignes ou malignes) en utilisant un modèle de deep learning avec explicabilité via Grad-CAM.

## Base URL

```
http://localhost:5000
```

## Authentification

Actuellement, l'API ne nécessite pas d'authentification (à ajouter en production).

---

## Endpoints

### 1. Health Check

Vérifie l'état de santé de l'API et du modèle.

**Endpoint:** `GET /api/health`

**Réponse:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

**Codes de statut:**

- `200 OK`: API fonctionnelle

---

### 2. Informations du Modèle

Retourne les détails techniques du modèle chargé.

**Endpoint:** `GET /api/model/info`

**Réponse:**

```json
{
  "status": "loaded",
  "input_shape": [null, 224, 224, 3],
  "output_shape": [null, 1],
  "total_params": 23587713,
  "layers": 177
}
```

**Codes de statut:**

- `200 OK`: Informations retournées
- `500 Internal Server Error`: Modèle non initialisé

---

### 3. Upload d'Image

Upload une image mammographique sur le serveur.

**Endpoint:** `POST /api/upload`

**Content-Type:** `multipart/form-data`

**Paramètres:**

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| file | File | Oui | Image mammographique (PNG, JPG, JPEG, DCM) |

**Exemple de requête (cURL):**

```bash
curl -X POST \
  -F "file=@mammogram.png" \
  http://localhost:5000/api/upload
```

**Exemple de requête (Python):**

```python
import requests

with open('mammogram.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/upload', files=files)
    print(response.json())
```

**Exemple de requête (JavaScript):**

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/api/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Réponse:**

```json
{
  "message": "Fichier uploadé avec succès",
  "filename": "mammogram.png",
  "filepath": "c:\\uploads\\mammogram.png"
}
```

**Codes de statut:**

- `200 OK`: Fichier uploadé avec succès
- `400 Bad Request`: Fichier manquant ou extension non autorisée
- `500 Internal Server Error`: Erreur serveur

---

### 4. Prédiction

Effectue une prédiction sur une image mammographique.

**Endpoint:** `POST /api/predict`

**Option 1: Upload direct**

**Content-Type:** `multipart/form-data`

**Paramètres:**

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| file | File | Oui | Image mammographique |

**Option 2: Fichier existant**

**Content-Type:** `application/json`

**Paramètres:**

```json
{
  "filepath": "c:\\uploads\\mammogram.png"
}
```

**Exemple de requête (cURL):**

```bash
curl -X POST \
  -F "file=@mammogram.png" \
  http://localhost:5000/api/predict
```

**Exemple de requête (Python):**

```python
import requests

# Option 1: Upload direct
with open('mammogram.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/predict', files=files)

# Option 2: Fichier existant
data = {'filepath': 'c:\\uploads\\mammogram.png'}
response = requests.post('http://localhost:5000/api/predict', json=data)

print(response.json())
```

**Réponse:**

```json
{
  "predicted_class": "Benign",
  "confidence": 0.8734,
  "probabilities": {
    "Benign": 0.8734,
    "Malignant": 0.1266
  }
}
```

**Description des champs:**

- `predicted_class`: Classe prédite ("Benign" ou "Malignant")
- `confidence`: Niveau de confiance de la prédiction (0-1)
- `probabilities`: Probabilités pour chaque classe

**Codes de statut:**

- `200 OK`: Prédiction effectuée
- `400 Bad Request`: Paramètres invalides
- `404 Not Found`: Fichier non trouvé
- `500 Internal Server Error`: Erreur lors de la prédiction

---

### 5. Grad-CAM

Génère une visualisation Grad-CAM pour expliquer la prédiction.

**Endpoint:** `POST /api/gradcam`

**Content-Type:** `multipart/form-data` ou `application/json`

**Paramètres:** (identiques à `/api/predict`)

**Exemple de requête (Python):**

```python
import requests
import base64
from PIL import Image
import io

with open('mammogram.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/gradcam', files=files)
    result = response.json()

# Décoder l'image Grad-CAM
img_data = result['gradcam_image'].split(',')[1]
img_bytes = base64.b64decode(img_data)
img = Image.open(io.BytesIO(img_bytes))
img.save('gradcam_result.png')

print(result['prediction'])
```

**Réponse:**

```json
{
  "prediction": {
    "predicted_class": "Benign",
    "confidence": 0.8734,
    "probabilities": {
      "Benign": 0.8734,
      "Malignant": 0.1266
    }
  },
  "gradcam_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**Description des champs:**

- `prediction`: Résultat de la prédiction (même format que `/api/predict`)
- `gradcam_image`: Image avec carte de chaleur en base64 (format data URL)

**Codes de statut:**

- `200 OK`: Visualisation générée
- `400 Bad Request`: Paramètres invalides
- `404 Not Found`: Fichier non trouvé
- `500 Internal Server Error`: Erreur lors de la génération

---

### 6. Analyse Complète

Effectue une analyse complète (prédiction + Grad-CAM) en une seule requête.

**Endpoint:** `POST /api/analyze`

**Content-Type:** `multipart/form-data`

**Paramètres:**

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| file | File | Oui | Image mammographique |

**Exemple de requête (JavaScript/React):**

```javascript
const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:5000/api/analyze', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    // Afficher la prédiction
    console.log('Classe:', result.prediction.predicted_class);
    console.log('Confiance:', result.prediction.confidence);
    
    // Afficher l'image Grad-CAM
    const imgElement = document.getElementById('gradcam');
    imgElement.src = result.gradcam_image;
    
  } catch (error) {
    console.error('Erreur:', error);
  }
};
```

**Réponse:**

```json
{
  "prediction": {
    "predicted_class": "Benign",
    "confidence": 0.8734,
    "probabilities": {
      "Benign": 0.8734,
      "Malignant": 0.1266
    }
  },
  "gradcam_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "original_filename": "mammogram.png"
}
```

**Codes de statut:**

- `200 OK`: Analyse complète effectuée
- `400 Bad Request`: Fichier manquant ou invalide
- `500 Internal Server Error`: Erreur lors de l'analyse

---

## Gestion des Erreurs

Toutes les erreurs retournent un JSON avec un champ `error`:

```json
{
  "error": "Description de l'erreur"
}
```

### Codes d'erreur courants

| Code | Signification | Cause possible |
|------|---------------|----------------|
| 400 | Bad Request | Paramètres manquants ou invalides |
| 404 | Not Found | Fichier non trouvé |
| 500 | Internal Server Error | Erreur du serveur ou du modèle |

---

## Formats de Fichiers Supportés

- **PNG** (.png)
- **JPEG** (.jpg, .jpeg)
- **DICOM** (.dcm)

**Taille maximale:** 16 MB

---

## Prétraitement Automatique

Toutes les images sont automatiquement prétraitées:

1. **Conversion en RGB** (si nécessaire)
2. **Redimensionnement** à 224x224 pixels
3. **Enhancement de contraste** (CLAHE)
4. **Normalisation** des pixels (0-1)

---

## Exemple d'Intégration Complète (React)

```javascript
import React, { useState } from 'react';

function BreastCancerDetection() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileUpload} accept="image/*" />
      
      {loading && <p>Analyse en cours...</p>}
      
      {result && (
        <div>
          <h3>Résultat: {result.prediction.predicted_class}</h3>
          <p>Confiance: {(result.prediction.confidence * 100).toFixed(2)}%</p>
          <img src={result.gradcam_image} alt="Grad-CAM" />
        </div>
      )}
    </div>
  );
}

export default BreastCancerDetection;
```

---

## Performance

- **Temps de réponse moyen:** 1-3 secondes (dépend du GPU)
- **Throughput:** ~10-20 requêtes/seconde
- **Optimisations:**
  - Modèle chargé en mémoire au démarrage
  - Cache des images prétraitées (à implémenter)
  - Batch processing (à implémenter)

---

## Sécurité

### Recommandations pour la production

1. **HTTPS obligatoire**
2. **Authentification JWT**
3. **Rate limiting** (ex: 100 requêtes/heure)
4. **Validation stricte des fichiers**
5. **Sanitization des noms de fichiers**
6. **Logs d'audit**
7. **Chiffrement des données sensibles**

---

## Support

Pour toute question ou problème:

- Consulter le README.md
- Vérifier les logs dans `logs/app.log`
- Tester avec `test_api.py`

---

**Version:** 1.0.0  
**Dernière mise à jour:** 2026-02-16
