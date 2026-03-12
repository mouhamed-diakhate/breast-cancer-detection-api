# API de Détection du Cancer du Sein

Backend Flask pour le système de détection du cancer du sein par deep learning avec explicabilité (Grad-CAM).

## 🚀 Fonctionnalités

- ✅ Upload d'images mammographiques
- ✅ Prédiction automatique (Bénin/Malin)
- ✅ Visualisation Grad-CAM pour l'explicabilité
- ✅ API REST complète
- ✅ Support CORS pour frontend React
- ✅ Gestion sécurisée des fichiers
- ✅ Logging complet

## 📋 Prérequis

- Python 3.8+
- pip
- (Optionnel) GPU pour accélération TensorFlow

## 🛠️ Installation

### 1. Cloner le projet

```bash
cd flaskProject8
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### 3. Activer l'environnement virtuel

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configuration

Créer un fichier `.env` à partir de `.env.example`:

```bash
copy .env.example .env
```

Modifier les variables selon vos besoins.

## 📁 Structure du Projet

```
flaskProject8/
├── app.py                      # Point d'entrée de l'application
├── config.py                   # Configuration de l'application
├── requirements.txt            # Dépendances Python
├── .env.example               # Template de variables d'environnement
├── .gitignore                 # Fichiers à ignorer par Git
│
├── routes/                    # Routes de l'API
│   ├── __init__.py
│   └── api.py                 # Endpoints REST
│
├── utils/                     # Utilitaires
│   ├── __init__.py
│   ├── image_preprocessing.py # Prétraitement d'images
│   ├── model_loader.py        # Chargement du modèle
│   ├── gradcam.py            # Implémentation Grad-CAM
│   └── file_utils.py         # Gestion des fichiers
│
├── models/                    # Modèles entraînés (à créer)
│   └── breast_cancer_model.h5
│
├── uploads/                   # Fichiers uploadés (créé automatiquement)
├── logs/                      # Logs de l'application (créé automatiquement)
│
├── static/                    # Fichiers statiques
└── templates/                 # Templates HTML (si nécessaire)
```

## 🚀 Démarrage

### Mode Développement

```bash
python app.py
```

L'API sera accessible sur `http://localhost:5000`

### Mode Production

```bash
# Utiliser un serveur WSGI comme Gunicorn
pip install gunicorn

# Linux/Mac
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Windows (utiliser waitress)
pip install waitress
waitress-serve --port=5000 app:app
```

## 📡 Endpoints de l'API

### 1. Health Check

**GET** `/api/health`

Vérifie l'état de l'API et du modèle.

**Réponse:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### 2. Informations du Modèle

**GET** `/api/model/info`

Retourne les informations sur le modèle chargé.

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

### 3. Upload d'Image

**POST** `/api/upload`

Upload une image mammographique.

**Paramètres:**

- `file`: Fichier image (multipart/form-data)

**Réponse:**

```json
{
  "message": "Fichier uploadé avec succès",
  "filename": "mammogram.png",
  "filepath": "c:\\uploads\\mammogram.png"
}
```

### 4. Prédiction

**POST** `/api/predict`

Effectue une prédiction sur une image.

**Paramètres:**

- `file`: Fichier image (multipart/form-data)
  OU
- `filepath`: Chemin vers un fichier déjà uploadé (JSON)

**Réponse:**

```json
{
  "predicted_class": "Benign",
  "confidence": 0.87,
  "probabilities": {
    "Benign": 0.87,
    "Malignant": 0.13
  }
}
```

### 5. Grad-CAM

**POST** `/api/gradcam`

Génère une visualisation Grad-CAM.

**Paramètres:**

- `file`: Fichier image (multipart/form-data)
  OU
- `filepath`: Chemin vers un fichier déjà uploadé (JSON)

**Réponse:**

```json
{
  "prediction": {
    "predicted_class": "Benign",
    "confidence": 0.87,
    "probabilities": {
      "Benign": 0.87,
      "Malignant": 0.13
    }
  },
  "gradcam_image": "data:image/png;base64,iVBORw0KG..."
}
```

### 6. Analyse Complète

**POST** `/api/analyze`

Effectue une analyse complète (prédiction + Grad-CAM).

**Paramètres:**

- `file`: Fichier image (multipart/form-data)

**Réponse:**

```json
{
  "prediction": {
    "predicted_class": "Benign",
    "confidence": 0.87,
    "probabilities": {
      "Benign": 0.87,
      "Malignant": 0.13
    }
  },
  "gradcam_image": "data:image/png;base64,iVBORw0KG...",
  "original_filename": "mammogram.png"
}
```

## 🧪 Tests avec cURL

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Upload d'image

```bash
curl -X POST -F "file=@path/to/image.png" http://localhost:5000/api/upload
```

### Prédiction

```bash
curl -X POST -F "file=@path/to/image.png" http://localhost:5000/api/predict
```

### Analyse complète

```bash
curl -X POST -F "file=@path/to/image.png" http://localhost:5000/api/analyze
```

## 🧪 Tests avec Python

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Upload et analyse
with open('mammogram.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/analyze', files=files)
    result = response.json()
    print(result['prediction'])
```

## 🔧 Configuration

### Variables d'environnement (.env)

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MODEL_PATH=models/breast_cancer_model.h5
```

### Configuration CORS

Par défaut, l'API accepte les requêtes depuis:

- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

Modifier dans `config.py`:

```python
CORS_ORIGINS = ['http://localhost:3000', 'http://your-frontend-url']
```

## 📦 Intégration du Modèle

### 1. Placer votre modèle entraîné

Copier votre modèle `.h5` dans le dossier `models/`:

```
models/
└── breast_cancer_model.h5
```

### 2. Modèle de démonstration

Si aucun modèle n'est trouvé, l'application crée automatiquement un modèle de démonstration basé sur ResNet50 pour les tests.

## 🔍 Logging

Les logs sont enregistrés dans:

- Console (stdout)
- Fichier `logs/app.log`

Niveaux de log:

- **INFO**: Opérations normales
- **WARNING**: Avertissements
- **ERROR**: Erreurs

## 🛡️ Sécurité

- ✅ Validation des extensions de fichiers
- ✅ Noms de fichiers sécurisés (secure_filename)
- ✅ Limite de taille de fichier (16MB)
- ✅ CORS configuré
- ⚠️ **À faire en production:**
  - Changer SECRET_KEY
  - Utiliser HTTPS
  - Ajouter authentification
  - Rate limiting

## 🐛 Dépannage

### Erreur: Modèle non trouvé

**Solution:** Placer un modèle `.h5` dans `models/` ou laisser l'application créer un modèle de démonstration.

### Erreur: TensorFlow GPU

**Solution:** Installer la version CPU de TensorFlow:

```bash
pip install tensorflow-cpu==2.15.0
```

### Erreur: CORS

**Solution:** Vérifier que l'origine du frontend est dans `CORS_ORIGINS` dans `config.py`.

## 📚 Technologies Utilisées

- **Flask 3.0**: Framework web
- **TensorFlow 2.15**: Deep learning
- **OpenCV**: Traitement d'images
- **Pillow**: Manipulation d'images
- **Flask-CORS**: Support CORS
- **NumPy**: Calculs numériques

## 🚀 Prochaines Étapes

1. ✅ Backend Flask (Terminé)
2. 🔄 Frontend React (Phase 7)
3. 🔄 Tests unitaires
4. 🔄 Déploiement

## 📝 Notes

- Le modèle de démonstration utilise ResNet50 pré-entraîné
- Pour la production, remplacer par votre modèle entraîné sur CBIS-DDSM/INbreast
- Les images sont automatiquement prétraitées (resize, normalisation, enhancement)
- Grad-CAM utilise la dernière couche convolutionnelle par défaut

## 👨‍💻 Développement

### Ajouter un nouvel endpoint

1. Ouvrir `routes/api.py`
2. Ajouter une nouvelle fonction avec le décorateur `@api_bp.route()`
3. L'endpoint sera automatiquement disponible sous `/api/votre-route`

### Modifier le prétraitement

Éditer `utils/image_preprocessing.py` pour ajuster:

- Taille des images
- Normalisation
- Débruitage
- Enhancement de contraste

## 📄 Licence

Ce projet est développé dans un cadre académique pour la détection du cancer du sein.

## 🤝 Contribution

Pour contribuer:

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Créer une Pull Request

---

**Développé avec ❤️ pour la détection précoce du cancer du sein**
