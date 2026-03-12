"""
Grad-CAM pour PyTorch via la bibliothèque pytorch-grad-cam.

Cette implémentation utilise GradCAM de la lib `pytorch_grad_cam` qui est
une réimplémentation standard et bien maintenue.
"""

import cv2
import numpy as np
import torch
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class GradCAM:
    """
    Grad-CAM PyTorch utilisant pytorch-grad-cam.

    Attributs:
        model     – le modèle PyTorch (ResNet18)
        device    – 'cuda' ou 'cpu'
    """

    def __init__(self, model, layer_name: str = None):
        self.model = model
        self.device = next(model.parameters()).device

        # Pour ResNet18, la dernière couche convolutionnelle est layer4[-1]
        # pytorch-grad-cam accepte directement la liste des couches cibles
        self.target_layers = [model.layer4[-1]]

    def generate_heatmap(self, image: np.ndarray, pred_index: int = None) -> np.ndarray:
        """
        Génère une heatmap Grad-CAM normalisée [0,1] de forme (H, W).

        Args:
            image      : tenseur NumPy (1, 3, H, W) normalisé ImageNet
            pred_index : index de la classe à visualiser (None = classe prédite)
        """
        try:
            from pytorch_grad_cam import GradCAM as PGC
            from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

            tensor = torch.from_numpy(image).float().to(self.device)

            # Déterminer la classe cible
            if pred_index is None:
                with torch.no_grad():
                    logits = self.model(tensor)
                pred_index = int(logits.argmax(dim=1).item())

            targets = [ClassifierOutputTarget(pred_index)]

            with PGC(model=self.model, target_layers=self.target_layers) as cam:
                grayscale_cam = cam(input_tensor=tensor, targets=targets)
                # grayscale_cam a la forme (1, H, W) avec valeurs dans [0, 1]
                return grayscale_cam[0]   # (H, W)

        except ImportError:
            logger.warning(
                "pytorch-grad-cam non disponible. Retour d'une heatmap vide. "
                "Installez-le : pip install pytorch-grad-cam"
            )
            return np.zeros((7, 7))
        except Exception as e:
            logger.error(f"Erreur Grad-CAM: {str(e)}")
            return np.zeros((7, 7))

    def overlay_heatmap(
        self,
        heatmap: np.ndarray,
        original_image: np.ndarray,
        alpha: float = 0.4,
        colormap: int = cv2.COLORMAP_JET,
    ) -> np.ndarray:
        """
        Superpose la heatmap sur l'image originale.

        Args:
            heatmap        : tableau 2-D float [0,1]
            original_image : tableau NumPy RGB uint8 (H, W, 3)
            alpha          : transparence de la superposition
            colormap       : colormap OpenCV
        Returns:
            image superposée RGB uint8 (H, W, 3)
        """
        # Redimensionner la heatmap à la taille de l'image originale
        heatmap_resized = cv2.resize(
            heatmap, (original_image.shape[1], original_image.shape[0])
        )

        # Convertir en uint8 et appliquer la colormap
        heatmap_uint8   = np.uint8(255 * heatmap_resized)
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        # Normaliser l'image originale si nécessaire
        orig = original_image
        if orig.max() <= 1.0:
            orig = np.uint8(255 * orig)

        return cv2.addWeighted(orig, 1 - alpha, heatmap_colored, alpha, 0)

    def generate_gradcam_visualization(
        self, image: np.ndarray, original_image: np.ndarray
    ) -> np.ndarray:
        """
        Pipeline complet : heatmap → superposition.

        Args:
            image          : tenseur (1, 3, H, W) normalisé
            original_image : RGB uint8 (H, W, 3)
        Returns:
            RGB uint8 (H, W, 3)
        """
        heatmap = self.generate_heatmap(image)
        return self.overlay_heatmap(heatmap, original_image)
