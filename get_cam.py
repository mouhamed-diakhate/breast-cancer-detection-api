import requests
import base64
import sys

# L'API locale
url = "http://127.0.0.1:5000/api/gradcam"
image_path = "C:\\Users\\hp\\Pictures\\a.png"  # Chemin de votre image test

# Envoyer la requête
with open(image_path, "rb") as img_file:
    response = requests.post(url, files={"file": img_file})

# Vérifier si ça a marché
if response.status_code == 200:
    data = response.json()
    print("Prédiction :", data['prediction']['predicted_class'])

    # Récupérer le texte base64 (en enlevant 'data:image/png;base64,')
    base64_str = data['gradcam_image'].split(",")[1]

    # Sauvegarder en tant que vraie image
    with open("resultat_gradcam.png", "wb") as fh:
        fh.write(base64.b64decode(base64_str))

    print("✅ Image sauvegardée sous le nom : resultat_gradcam.png")
else:
    print("Erreur :", response.text)
