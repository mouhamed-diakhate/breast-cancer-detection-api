import numpy as np
from PIL import Image
import cv2
import torch
from torchvision import transforms
from typing import Tuple, Optional


# Normalisation ImageNet identique au notebook Colab
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


class ImagePreprocessor:
    """Prétraitement des images médicales pour ResNet18 (PyTorch)"""

    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        """
        Args:
            target_size: (hauteur, largeur) de l'image cible.
        """
        self.target_size = target_size  # (H, W)

        # Pipeline identique au pipeline TEST du notebook Colab
        self.transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=3),  # mammographies → 3 canaux
            transforms.Resize(target_size),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ])

    # ------------------------------------------------------------------
    # Méthodes publiques
    # ------------------------------------------------------------------

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Charge une image en tableau NumPy RGB uint8 (H, W, 3).
        Utile pour la superposition Grad-CAM.
        """
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return np.array(img)
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement de l'image: {str(e)}")

    def preprocess(self, image_path: str) -> np.ndarray:
        """
        Pipeline complet : charge → Grayscale→RGB → resize → tenseur normalisé.

        Returns:
            Tenseur NumPy de forme (1, 3, 224, 224) prêt pour le modèle.
        """
        try:
            img = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement de l'image: {str(e)}")

        tensor = self.transform(img)          # (3, 224, 224)
        batch  = tensor.unsqueeze(0)          # (1, 3, 224, 224)
        return batch.numpy()                  # NumPy pour compatibilité avec model_loader

    def preprocess_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """
        Prétraite une image depuis des bytes.

        Returns:
            Tenseur NumPy (1, 3, 224, 224).
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        bgr   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb   = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        img   = Image.fromarray(rgb)

        tensor = self.transform(img)
        batch  = tensor.unsqueeze(0)
        return batch.numpy()
