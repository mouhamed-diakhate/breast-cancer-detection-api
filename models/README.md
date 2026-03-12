# Modèles de Deep Learning

Ce dossier contient les modèles entraînés pour la détection du cancer du sein.

## Structure

- `breast_cancer_model.h5` : Modèle principal entraîné
- `model_weights.h5` : Poids du modèle (optionnel)

## Instructions

1. Placer votre modèle entraîné (format .h5) dans ce dossier
2. Nommer le fichier `breast_cancer_model.h5`
3. Si aucun modèle n'est présent, l'application créera un modèle de démonstration basé sur ResNet50

## Format attendu

- **Input shape**: (224, 224, 3) - Images RGB 224x224
- **Output shape**: (1,) - Classification binaire (sigmoid)
- **Classes**:
  - 0 = Benign (Bénin)
  - 1 = Malignant (Malin)

## Entraînement

Pour entraîner votre modèle:

1. Utiliser Google Colab (Phase 3 du projet)
2. Entraîner sur CBIS-DDSM ou INbreast
3. Sauvegarder le modèle au format .h5
4. Copier le fichier dans ce dossier
