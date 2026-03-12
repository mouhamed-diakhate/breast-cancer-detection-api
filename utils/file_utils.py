import os
from werkzeug.utils import secure_filename
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Vérifie si l'extension du fichier est autorisée
    
    Args:
        filename: Nom du fichier
        allowed_extensions: Ensemble des extensions autorisées
        
    Returns:
        True si l'extension est autorisée, False sinon
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder: Path) -> str:
    """
    Sauvegarde un fichier uploadé de manière sécurisée
    
    Args:
        file: Fichier Flask
        upload_folder: Dossier de destination
        
    Returns:
        Chemin complet du fichier sauvegardé
    """
    filename = secure_filename(file.filename)
    
    # Créer un nom de fichier unique si nécessaire
    filepath = upload_folder / filename
    counter = 1
    name, ext = os.path.splitext(filename)
    
    while filepath.exists():
        filename = f"{name}_{counter}{ext}"
        filepath = upload_folder / filename
        counter += 1
    
    file.save(str(filepath))
    logger.info(f"Fichier sauvegardé: {filepath}")
    
    return str(filepath)


def cleanup_old_files(folder: Path, max_age_hours: int = 24):
    """
    Nettoie les fichiers anciens d'un dossier
    
    Args:
        folder: Dossier à nettoyer
        max_age_hours: Age maximum des fichiers en heures
    """
    import time
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in folder.glob('*'):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    logger.info(f"Fichier supprimé: {file_path}")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {file_path}: {str(e)}")
