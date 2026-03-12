import torch
import torch.nn as nn
from torchvision import models
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def build_model():
    """
    Reconstruit l'architecture ResNet18 exactement comme dans le notebook Colab.

    Architecture:
    - Base: ResNet18 (ImageNet weights)
    - Toutes les couches gelées sauf layer3, layer4 et fc
    - Dernière couche (fc): nn.Sequential(nn.Dropout(0.3), nn.Linear(512, 2))
    - 2 classes: 0=BENIGN, 1=MALIGNANT
    """
    model = models.resnet18(weights=None)

    # Geler toutes les couches (comme dans l'entraînement)
    for param in model.parameters():
        param.requires_grad = False

    # Dégeler layer3, layer4 et fc (comme dans l'entraînement)
    for name, param in model.named_parameters():
        if any(x in name for x in ["layer3", "layer4", "fc"]):
            param.requires_grad = True

    # Remplacer la dernière couche (identique au notebook)
    num_features = model.fc.in_features  # 512 pour ResNet18
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, 2)
    )

    return model


class ModelLoader:
    """Classe pour charger et gérer le modèle PyTorch ResNet18"""

    def __init__(self, model_path: Path):
        """
        Initialise le chargeur de modèle.

        Args:
            model_path: Chemin vers le fichier .pth (state_dict)
        """
        self.model_path = model_path
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Utilisation du device: {self.device}")
        self._load_model()

    def _load_model(self):
        """Charge le modèle PyTorch depuis le fichier state_dict"""
        try:
            if self.model_path.exists():
                logger.info(f"Chargement du modèle depuis {self.model_path}")
                self.model = build_model()
                checkpoint = torch.load(
                    self.model_path,
                    map_location=self.device
                )
                
                # Check if it's a full checkpoint dict or just the state dict
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    state_dict = checkpoint['model_state_dict']
                else:
                    state_dict = checkpoint
                    
                self.model.load_state_dict(state_dict)
                self.model.to(self.device)
                self.model.eval()
                logger.info("Modèle PyTorch chargé avec succès")
            else:
                logger.warning(f"Modèle non trouvé à {self.model_path}")
                logger.info("Création d'un modèle de démonstration ResNet18.")
                self.model = build_model()
                self.model.to(self.device)
                self.model.eval()
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
            raise

    def predict(self, preprocessed_image: np.ndarray) -> dict:
        """
        Effectue une prédiction sur une image prétraitée.

        Args:
            preprocessed_image: Tenseur NumPy de forme (1, 3, 224, 224)
                                 normalisé selon ImageNet.

        Returns:
            dict avec 'predicted_class', 'confidence', 'probabilities'
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")

        # Convertir en tenseur PyTorch et envoyer sur le bon device
        if isinstance(preprocessed_image, np.ndarray):
            tensor = torch.from_numpy(preprocessed_image).float().to(self.device)
        else:
            tensor = preprocessed_image.float().to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)           # (1, 2) logits
            probabilities = torch.softmax(outputs, dim=1)  # (1, 2)

        benign_prob = float(probabilities[0, 0].item())
        malignant_prob = float(probabilities[0, 1].item())

        predicted_class = "Malignant" if malignant_prob > 0.5 else "Benign"
        confidence = malignant_prob if malignant_prob > 0.5 else benign_prob

        return {
            'predicted_class': predicted_class,
            'confidence': float(confidence),
            'probabilities': {
                'Benign': float(benign_prob),
                'Malignant': float(malignant_prob)
            }
        }

    def get_model_info(self) -> dict:
        """Retourne les informations sur le modèle"""
        if self.model is None:
            return {'status': 'not_loaded'}

        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(
            p.numel() for p in self.model.parameters() if p.requires_grad
        )

        return {
            'status': 'loaded',
            'architecture': 'ResNet18',
            'device': str(self.device),
            'input_shape': '(N, 3, 224, 224)',
            'output_shape': '(N, 2)',
            'classes': ['Benign', 'Malignant'],
            'total_params': total_params,
            'trainable_params': trainable_params
        }
