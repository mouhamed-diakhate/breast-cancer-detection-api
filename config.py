import os
from pathlib import Path

class Config:
    """Configuration de base pour l'application Flask"""
    
    # Chemins de base
    BASE_DIR = Path(__file__).parent
    
    # Configuration Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuration des uploads
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm'}
    
    # Configuration du modèle
    MODEL_PATH = BASE_DIR / 'models' / 'breast_cancer_model.pth'
    MODEL_DENSENET_PATH = BASE_DIR / 'models' / 'mammography_model_v3_densenet'
    
    AVAILABLE_MODELS = {
        'resnet18': {
            'name': 'ResNet18 (v1)',
            'architecture': 'ResNet18',
            'path_key': 'MODEL_PATH',
            'type': 'pth',
        },
        'densenet': {
            'name': 'DenseNet (v3)',
            'architecture': 'DenseNet',
            'path_key': 'MODEL_DENSENET_PATH',
            'type': 'torchscript',
        },
    }
    
    # Configuration des images
    IMG_SIZE = (224, 224)  # Taille standard pour les modèles pré-entraînés
    
    # Configuration CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']
    
    # Seuils de classification
    CLASSIFICATION_THRESHOLD = 0.5
    
    # Classes
    CLASS_NAMES = ['Benign', 'Malignant']
    
    @staticmethod
    def init_app(app):
        """Initialise les dossiers nécessaires"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.BASE_DIR / 'models', exist_ok=True)
        os.makedirs(Config.BASE_DIR / 'logs', exist_ok=True)


class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuration pour les tests"""
    DEBUG = True
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
