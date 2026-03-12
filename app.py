from flask import Flask
from flask_cors import CORS
import logging
from pathlib import Path

from config import config
from routes.api import api_bp, init_model


def create_app(config_name='development'):
    """
    Factory function pour créer l'application Flask
    
    Args:
        config_name: Nom de la configuration à utiliser
        
    Returns:
        Application Flask configurée
    """
    # Créer l'application
    app = Flask(__name__)
    
    # Charger la configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configurer le logging
    setup_logging(app)
    
    # Configurer CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Enregistrer les blueprints
    app.register_blueprint(api_bp)
    
    # Initialiser le modèle
    with app.app_context():
        init_model(app)
    
    # Route de base
    @app.route('/')
    def index():
        return {
            'message': 'API de détection du cancer du sein',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'model_info': '/api/model/info',
                'upload': '/api/upload',
                'predict': '/api/predict',
                'gradcam': '/api/gradcam',
                'analyze': '/api/analyze'
            }
        }
    
    # Gestionnaire d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint non trouvé'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Erreur serveur: {error}')
        return {'error': 'Erreur interne du serveur'}, 500
    
    return app


def setup_logging(app):
    """Configure le système de logging"""
    
    # Créer le dossier de logs
    log_dir = Path(app.config['BASE_DIR']) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configuration du logging
    log_file = log_dir / 'app.log'
    
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    app.logger.info('Application démarrée')


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)
