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

# Dictionnaire des modèles chargés: { model_id: ModelLoader }
model_loaders = {}
preprocessor = None
gradcams = {}


def init_model(app):
    """Initialise tous les modèles au démarrage de l'application"""
    global model_loaders, preprocessor, gradcams

    try:
        preprocessor = ImagePreprocessor(app.config['IMG_SIZE'])
        available = app.config.get('AVAILABLE_MODELS', {})

        for model_id, info in available.items():
            path = app.config[info['path_key']]
            model_type = info.get('type', 'pth')
            architecture = info.get('architecture', 'Unknown')
            try:
                loader = ModelLoader(path, model_type=model_type, architecture=architecture)
                model_loaders[model_id] = loader
                gradcams[model_id] = GradCAM(loader.model)
                logger.info(f"Modèle '{model_id}' ({architecture}) initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle '{model_id}': {str(e)}")

        if not model_loaders:
            # Fallback: charger le modèle par défaut
            loader = ModelLoader(app.config['MODEL_PATH'])
            model_loaders['resnet18'] = loader
            gradcams['resnet18'] = GradCAM(loader.model)
            logger.info("Chargement du modèle par défaut (fallback)")

    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des modèles: {str(e)}")


def _get_loader(model_id: str = None):
    """Retourne le ModelLoader pour l'id donné, ou le premier disponible."""
    if model_id and model_id in model_loaders:
        return model_loaders[model_id]
    # Fallback to first available
    if model_loaders:
        return next(iter(model_loaders.values()))
    return None


def _get_gradcam(model_id: str = None):
    """Retourne le GradCAM pour l'id donné, ou le premier disponible."""
    if model_id and model_id in gradcams:
        return gradcams[model_id]
    if gradcams:
        return next(iter(gradcams.values()))
    return None


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de l'état de l'API"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': len(model_loaders) > 0,
        'version': '1.0.0'
    }), 200


@api_bp.route('/models', methods=['GET'])
def list_models():
    """Retourne la liste des modèles disponibles"""
    available = current_app.config.get('AVAILABLE_MODELS', {})
    result = []
    for model_id, info in available.items():
        result.append({
            'id': model_id,
            'name': info.get('name', model_id),
            'architecture': info.get('architecture', 'Unknown'),
            'loaded': model_id in model_loaders,
        })
    return jsonify(result), 200


@api_bp.route('/model/info', methods=['GET'])
def model_info():
    """Retourne les informations sur le modèle par défaut"""
    loader = _get_loader()
    if loader is None:
        return jsonify({'error': 'Modèle non initialisé'}), 500

    info = loader.get_model_info()
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

        # Vérification mammographie
        if preprocessor is not None and not preprocessor.is_mammography(filepath):
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({
                'error': 'L\'image téléchargée ne semble pas être une mammographie. Veuillez uploader une image mammographique.'
            }), 400

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
        - model: ID du modèle à utiliser (optionnel)
        OU
        - filepath: Chemin vers un fichier déjà uploadé (JSON)
        - model: ID du modèle à utiliser (optionnel)
    """
    try:
        # Récupérer le modèle demandé
        model_id = request.form.get('model') or (request.json.get('model') if request.is_json else None)
        loader = _get_loader(model_id)

        if loader is None or loader.model is None:
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

        # Vérification mammographie
        if not preprocessor.is_mammography(filepath):
            if temp_file:
                try:
                    os.remove(filepath)
                except:
                    pass
            return jsonify({
                'error': 'L\'image téléchargée ne semble pas être une mammographie. Veuillez uploader une image mammographique.'
            }), 400

        # Prétraiter l'image
        preprocessed_image = preprocessor.preprocess(filepath)

        # Effectuer la prédiction
        prediction_result = loader.predict(preprocessed_image)

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
        - model: ID du modèle à utiliser (optionnel)
        OU
        - filepath: Chemin vers un fichier déjà uploadé (JSON)
    """
    try:
        model_id = request.form.get('model') or (request.json.get('model') if request.is_json else None)
        loader = _get_loader(model_id)
        gradcam = _get_gradcam(model_id)

        if loader is None or gradcam is None:
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

        # Vérification mammographie
        if not preprocessor.is_mammography(filepath):
            if temp_file:
                try:
                    os.remove(filepath)
                except:
                    pass
            return jsonify({
                'error': 'L\'image téléchargée ne semble pas être une mammographie. Veuillez uploader une image mammographique.'
            }), 400

        # Charger l'image originale
        original_image = preprocessor.load_image(filepath)

        # Prétraiter l'image pour le modèle
        preprocessed_image = preprocessor.preprocess(filepath)

        # Effectuer la prédiction
        prediction_result = loader.predict(preprocessed_image)

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
        - model: ID du modèle à utiliser (optionnel, défaut: premier modèle disponible)

    Retourne:
        - prediction: Résultat de la prédiction
        - gradcam_image: Image avec carte de chaleur (base64)
        - original_filename: Nom du fichier original
        - model_used: ID du modèle utilisé
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

        # Récupérer l'id du modèle demandé
        model_id = request.form.get('model')
        loader = _get_loader(model_id)
        gradcam = _get_gradcam(model_id)
        used_model_id = model_id if (model_id and model_id in model_loaders) else (next(iter(model_loaders)) if model_loaders else None)

        if loader is None or gradcam is None:
            return jsonify({'error': 'Modèle non disponible'}), 500

        # Sauvegarder temporairement
        filepath = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])

        # Vérification mammographie
        if not preprocessor.is_mammography(filepath):
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({
                'error': 'L\'image téléchargée ne semble pas être une mammographie. Veuillez uploader une image mammographique.'
            }), 400

        # Charger l'image originale
        original_image = preprocessor.load_image(filepath)

        # Prétraiter l'image
        preprocessed_image = preprocessor.preprocess(filepath)

        # Prédiction
        prediction_result = loader.predict(preprocessed_image)

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
            'original_filename': file.filename,
            'model_used': used_model_id,
        }), 200

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        return jsonify({'error': f'Erreur lors de l\'analyse: {str(e)}'}), 500
