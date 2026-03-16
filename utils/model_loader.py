import torch
import torch.nn as nn
from torchvision import models
import numpy as np
from pathlib import Path
import logging
import zipfile
import tempfile
import os

logger = logging.getLogger(__name__)


def build_resnet18_model():
    """
    Reconstruit l'architecture ResNet18 exactement comme dans le notebook Colab.
    - Base: ResNet18, toutes les couches gelées sauf layer3, layer4, fc
    - fc: nn.Sequential(nn.Dropout(0.3), nn.Linear(512, 2))
    - 2 classes: 0=BENIGN, 1=MALIGNANT
    """
    model = models.resnet18(weights=None)

    for param in model.parameters():
        param.requires_grad = False

    for name, param in model.named_parameters():
        if any(x in name for x in ["layer3", "layer4", "fc"]):
            param.requires_grad = True

    num_features = model.fc.in_features  # 512
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_features, 2)
    )
    return model


def build_densenet_model():
    """
    Reconstruit l'architecture DenseNet121 pour la classification mammographique.
    - Base: DenseNet121
    - Dernière couche remplacée: nn.Linear(1024, 2)
    - 2 classes: 0=BENIGN, 1=MALIGNANT
    """
    model = models.densenet121(weights=None)
    num_features = model.classifier.in_features  # 1024
    model.classifier = nn.Linear(num_features, 2)
    return model


# Alias for backwards compatibility
build_model = build_resnet18_model


def _try_load_checkpoint(path: Path, device: torch.device):
    """
    Tente de charger un checkpoint depuis un fichier ou dossier PyTorch.
    Gère les cas : fichier .pth, dossier zip extrait, TorchScript.

    Returns: (model_or_checkpoint, is_torchscript: bool)
    """
    path = Path(path)

    # Cas 1 : fichier régulier (ou fichier zip .pth/.pt)
    if path.is_file():
        # Essayer TorchScript en premier
        try:
            m = torch.jit.load(str(path), map_location=device)
            m.eval()
            logger.info("Chargé en tant que TorchScript (fichier)")
            return m, True
        except Exception:
            pass
        # Sinon, torch.load classique
        checkpoint = torch.load(str(path), map_location=device)
        return checkpoint, False

    # Cas 2 : dossier — essayer TorchScript directement sur le dossier
    if path.is_dir():
        try:
            m = torch.jit.load(str(path), map_location=device)
            m.eval()
            logger.info("Chargé en tant que TorchScript (dossier)")
            return m, True
        except Exception:
            pass

        # Cas 2b : le dossier contient les fichiers internes d'un zip PyTorch extrait.
        # On recrée un zip temporaire et on utilise torch.load.
        data_pkl = path / "data.pkl"
        if data_pkl.exists():
            logger.info("Structure zip PyTorch détectée dans le dossier — reconstruction en zip temporaire")
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_STORED) as zf:
                    prefix = f"{path.name}/"
                    for root, dirs, files_list in os.walk(path):
                        # Exclure les dossiers cachés sauf .data
                        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.data']
                        for fname in files_list:
                            full_path = os.path.join(root, fname)
                            rel = os.path.relpath(full_path, path)
                            arcname = prefix + rel.replace("\\", "/")
                            zf.write(full_path, arcname)

                checkpoint = torch.load(tmp_path, map_location=device)
                return checkpoint, False
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    raise RuntimeError(f"Impossible de charger le modèle depuis {path}")


class ModelLoader:
    """Classe pour charger et gérer un modèle PyTorch"""

    MODEL_BUILDERS = {
        'ResNet18': build_resnet18_model,
        'DenseNet': build_densenet_model,
    }

    def __init__(self, model_path: Path, model_type: str = 'pth', architecture: str = 'ResNet18'):
        """
        Args:
            model_path: chemin vers le fichier .pth ou le dossier modèle
            model_type: 'pth' pour state dict, 'torchscript' pour TorchScript
            architecture: 'ResNet18' ou 'DenseNet' (utilisé pour reconstruire l'architecture)
        """
        self.model_path = Path(model_path)
        self.model_type = model_type
        self.architecture = architecture
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"[{architecture}] Utilisation du device: {self.device}")
        self._load_model()

    def _load_model(self):
        """Charge le modèle avec détection automatique du format"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Modèle non trouvé à {self.model_path}")

            logger.info(f"[{self.architecture}] Chargement depuis {self.model_path}")

            raw, is_torchscript = _try_load_checkpoint(self.model_path, self.device)

            if is_torchscript:
                # Modèle TorchScript complet — prêt à l'emploi
                self.model = raw
            else:
                # Construire l'architecture puis charger les poids
                builder = self.MODEL_BUILDERS.get(self.architecture)
                if builder is None:
                    raise ValueError(f"Architecture inconnue: {self.architecture}")

                self.model = builder()

                # Extraire le state dict si c'est un dict de checkpoint
                if isinstance(raw, dict):
                    state_dict = (
                        raw.get('model_state_dict')
                        or raw.get('state_dict')
                        or raw
                    )
                else:
                    # Cas : torch.save(model, path) — objet complet
                    if isinstance(raw, nn.Module):
                        self.model = raw
                        self.model.to(self.device)
                        self.model.eval()
                        logger.info(f"[{self.architecture}] Modèle complet chargé")
                        return
                    state_dict = raw

                self.model.load_state_dict(state_dict, strict=False)
                self.model.to(self.device)
                self.model.eval()

            logger.info(f"[{self.architecture}] Chargé avec succès")

        except Exception as e:
            logger.error(f"[{self.architecture}] Erreur de chargement: {str(e)}")
            raise

    def predict(self, preprocessed_image: np.ndarray) -> dict:
        """
        Effectue une prédiction sur une image prétraitée.
        Args:
            preprocessed_image: NumPy array (1, 3, 224, 224) normalisé ImageNet
        Returns:
            dict avec 'predicted_class', 'confidence', 'probabilities'
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")

        if isinstance(preprocessed_image, np.ndarray):
            tensor = torch.from_numpy(preprocessed_image).float().to(self.device)
        else:
            tensor = preprocessed_image.float().to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.softmax(outputs, dim=1)

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

        try:
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        except Exception:
            total_params = 0
            trainable_params = 0

        return {
            'status': 'loaded',
            'architecture': self.architecture,
            'device': str(self.device),
            'input_shape': '(N, 3, 224, 224)',
            'output_shape': '(N, 2)',
            'classes': ['Benign', 'Malignant'],
            'total_params': total_params,
            'trainable_params': trainable_params
        }
