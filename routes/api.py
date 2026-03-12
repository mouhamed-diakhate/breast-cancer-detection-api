from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import logging
import base64
import io
from PIL import Image
import numpy as np

from utils.file_utils import allowed_file, save_uploaded_file
from utils.image_preprocessing import ImagePreprocessor
from utils.model_loader import ModelLoader
from utils.gradcam import GradCAM

logger = logging.getLogger(__name__)

# Créer le Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Variables globales pour le modèle (chargées au démarrage)
model_loader = None
preprocessor = None
gradcam = None


def init_model(app):
    """Initialise le modèle au démarrage de l'application"""
    global model_loader, preprocessor, gradcam
    
    try:
        model_loader = ModelLoader(app.config['MODEL_PATH'])
        preprocessor = ImagePreprocessor(app.config['IMG_SIZE'])
        gradcam = GradCAM(model_loader.model)
        logger.info("Modèle initialisé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du modèle: {str(e)}")


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de l'état de l'API"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loader is not None and model_loader.model is not None,
        'version': '1.0.0'
    }), 200


@api_bp.route('/model/info', methods=['GET'])
def model_info():
    """Retourne les informations sur le modèle"""
    if model_loader is None:
        return jsonify({'error': 'Modèle non initialisé'}), 500
    
    info = model_loader.get_model_info()
    return jsonify(info), 200


@api_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    Endpoint pour uploader une image
    
    Accepte:
        - file: Fichier image (multipart/form-data)
    
    Retourne:
        - filename: Nom du fichier sauvegardé
        - filepath: Chemin du fichier
        - message: Message de confirmation
    """
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        
        # Vérifier que le fichier a un nom
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        # Vérifier l'extension
        if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify({
                'error': 'Extension de fichier non autorisée',
                'allowed_extensions': list(current_app.config['ALLOWED_EXTENSIONS'])
            }), 400
        
        # Sauvegarder le fichier
        filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        
        return jsonify({
            'message': 'Fichier uploadé avec succès',
            'filename': os.path.basename(filepath),
            'filepath': filepath
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload: {str(e)}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500


@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint pour effectuer une prédiction
    
    Accepte:
        - file: Fichier image (multipart/form-data)
        OU
        - filepath: Chemin vers un fichier déjà uploadé (JSON)
    
    Retourne:
        - prediction: Classe prédite (Benign/Malignant)
        - confidence: Niveau de confiance
        - probabilities: Probabilités pour chaque classe
    """
    try:
        # Vérifier que le modèle est chargé
        if model_loader is None or model_loader.model is None:
            return jsonify({'error': 'Modèle non disponible'}), 500
        
        filepath = None
        temp_file = False
        
        # Cas 1: Fichier uploadé directement
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'Nom de fichier vide'}), 400
            
            if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                return jsonify({'error': 'Extension de fichier non autorisée'}), 400
            
            filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
            temp_file = True
            
        # Cas 2: Chemin de fichier fourni
        elif request.is_json and 'filepath' in request.json:
            filepath = request.json['filepath']
            
            if not os.path.exists(filepath):
                return jsonify({'error': 'Fichier non trouvé'}), 404
        
        else:
            return jsonify({'error': 'Aucun fichier ou chemin fourni'}), 400
        
        # Prétraiter l'image
        preprocessed_image = preprocessor.preprocess(filepath)
        
        # Effectuer la prédiction
        prediction_result = model_loader.predict(preprocessed_image)
        
        # Nettoyer le fichier temporaire si nécessaire
        if temp_file:
            try:
                os.remove(filepath)
            except:
                pass
        
        return jsonify(prediction_result), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {str(e)}")
        return jsonify({'error': f'Erreur lors de la prédiction: {str(e)}'}), 500


@api_bp.route('/gradcam', methods=['POST'])
def generate_gradcam():
    """
    Endpoint pour générer une visualisation Grad-CAM
    
    Accepte:
        - file: Fichier image (multipart/form-data)
        OU
        - filepath: Chemin vers un fichier déjà uploadé (JSON)
    
    Retourne:
        - prediction: Résultat de la prédiction
        - gradcam_image: Image avec carte de chaleur (base64)
    """
    try:
        # Vérifier que le modèle est chargé
        if model_loader is None or gradcam is None:
            return jsonify({'error': 'Modèle non disponible'}), 500
        
        filepath = None
        temp_file = False
        
        # Cas 1: Fichier uploadé directement
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'Nom de fichier vide'}), 400
            
            if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                return jsonify({'error': 'Extension de fichier non autorisée'}), 400
            
            filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
            temp_file = True
            
        # Cas 2: Chemin de fichier fourni
        elif request.is_json and 'filepath' in request.json:
            filepath = request.json['filepath']
            
            if not os.path.exists(filepath):
                return jsonify({'error': 'Fichier non trouvé'}), 404
        
        else:
            return jsonify({'error': 'Aucun fichier ou chemin fourni'}), 400
        
        # Charger l'image originale
        original_image = preprocessor.load_image(filepath)
        
        # Prétraiter l'image pour le modèle
        preprocessed_image = preprocessor.preprocess(filepath)
        
        # Effectuer la prédiction
        prediction_result = model_loader.predict(preprocessed_image)
        
        # Générer la visualisation Grad-CAM
        gradcam_visualization = gradcam.generate_gradcam_visualization(
            preprocessed_image,
            original_image
        )
        
        # Convertir l'image en base64
        pil_image = Image.fromarray(gradcam_visualization.astype('uint8'))
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Nettoyer le fichier temporaire si nécessaire
        if temp_file:
            try:
                os.remove(filepath)
            except:
                pass
        
        return jsonify({
            'prediction': prediction_result,
            'gradcam_image': f'data:image/png;base64,{img_str}'
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération Grad-CAM: {str(e)}")
        return jsonify({'error': f'Erreur lors de la génération: {str(e)}'}), 500


@api_bp.route('/analyze', methods=['POST'])
def analyze_complete():
    """
    Endpoint complet d'analyse (prédiction + Grad-CAM)
    
    Accepte:
        - file: Fichier image (multipart/form-data)
    
    Retourne:
        - prediction: Résultat de la prédiction
        - gradcam_image: Image avec carte de chaleur (base64)
        - original_filename: Nom du fichier original
    """
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify({'error': 'Extension de fichier non autorisée'}), 400
        
        # Sauvegarder temporairement
        filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        
        # Charger l'image originale
        original_image = preprocessor.load_image(filepath)
        
        # Prétraiter l'image
        preprocessed_image = preprocessor.preprocess(filepath)
        
        # Prédiction
        prediction_result = model_loader.predict(preprocessed_image)
        
        # Grad-CAM
        gradcam_visualization = gradcam.generate_gradcam_visualization(
            preprocessed_image,
            original_image
        )
        
        # Convertir en base64
        pil_image = Image.fromarray(gradcam_visualization.astype('uint8'))
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Nettoyer
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'prediction': prediction_result,
            'gradcam_image': f'data:image/png;base64,{img_str}',
            'original_filename': file.filename
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        return jsonify({'error': f'Erreur lors de l\'analyse: {str(e)}'}), 500
