# 🚀 Guide de Démarrage Rapide

## Installation et Lancement en 3 Étapes

### Étape 1: Installer les dépendances

```bash
cd c:\Users\hp\PycharmProjects\flaskProject8
pip install -r requirements.txt
```

**Note:** L'installation peut prendre 5-10 minutes (TensorFlow est volumineux).

### Étape 2: Lancer le serveur

```bash
python app.py
```

Vous devriez voir:

```
* Running on http://0.0.0.0:5000
* Application démarrée
```

### Étape 3: Tester l'API

Ouvrir un nouveau terminal et exécuter:

```bash
python test_api.py
```

Ou tester avec une image:

```bash
python test_api.py chemin/vers/image.png
```

## 🧪 Test Rapide avec cURL

```bash
# Test de santé
curl http://localhost:5000/api/health

# Devrait retourner:
# {"status":"healthy","model_loaded":true,"version":"1.0.0"}
```

## 📝 Votre Modèle

Pour utiliser votre propre modèle entraîné:

1. Copier votre fichier `.h5` dans le dossier `models/`
2. Le renommer en `breast_cancer_model.h5`
3. Redémarrer le serveur

**Sans modèle:** L'application crée automatiquement un modèle de démonstration (ResNet50).

## 🎨 Intégration Frontend React

Exemple de code React pour appeler l'API:

```javascript
const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:5000/api/analyze', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  
  // result.prediction.predicted_class -> "Benign" ou "Malignant"
  // result.prediction.confidence -> 0.0 à 1.0
  // result.gradcam_image -> Image base64 à afficher
};
```

## 📚 Documentation Complète

- **[README.md](README.md)** - Guide complet
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentation API détaillée

## ❓ Problèmes Courants

### Erreur: Module not found

**Solution:** Installer les dépendances:

```bash
pip install -r requirements.txt
```

### Erreur: Port déjà utilisé

**Solution:** Changer le port dans `app.py`:

```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### TensorFlow trop lent

**Solution:** Installer la version CPU:

```bash
pip install tensorflow-cpu==2.15.0
```

## 🎯 Prochaine Étape

**Phase 7: Développement Frontend React**

Créer l'interface utilisateur pour:

- Upload d'images
- Affichage des prédictions
- Visualisation Grad-CAM

---

**Besoin d'aide ?** Consulter la documentation complète dans README.md
