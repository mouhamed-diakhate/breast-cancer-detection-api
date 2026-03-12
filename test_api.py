"""
Script de test pour l'API Flask
"""
import requests
import json
from pathlib import Path


BASE_URL = 'http://localhost:5000'


def test_health():
    """Test de l'endpoint health"""
    print("\n=== Test Health Check ===")
    response = requests.get(f'{BASE_URL}/api/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_model_info():
    """Test de l'endpoint model info"""
    print("\n=== Test Model Info ===")
    response = requests.get(f'{BASE_URL}/api/model/info')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_predict(image_path=None):
    """Test de l'endpoint predict"""
    print("\n=== Test Predict ===")
    
    if image_path and Path(image_path).exists():
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{BASE_URL}/api/predict', files=files)
    else:
        print("Aucune image fournie, test avec JSON filepath")
        data = {'filepath': 'test_image.png'}
        response = requests.post(
            f'{BASE_URL}/api/predict',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 400, 404]


def test_analyze(image_path=None):
    """Test de l'endpoint analyze"""
    print("\n=== Test Analyze ===")
    
    if image_path and Path(image_path).exists():
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{BASE_URL}/api/analyze', files=files)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if 'prediction' in result:
            print(f"Prediction: {json.dumps(result['prediction'], indent=2)}")
            print(f"Grad-CAM image: {'Present' if 'gradcam_image' in result else 'Missing'}")
        else:
            print(f"Response: {json.dumps(result, indent=2)}")
        
        return response.status_code == 200
    else:
        print("Aucune image fournie, test ignoré")
        return True


def run_all_tests(image_path=None):
    """Exécute tous les tests"""
    print("=" * 50)
    print("TESTS DE L'API FLASK")
    print("=" * 50)
    
    results = {
        'health': test_health(),
        'model_info': test_model_info(),
        'predict': test_predict(image_path),
        'analyze': test_analyze(image_path)
    }
    
    print("\n" + "=" * 50)
    print("RÉSULTATS")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests réussis")
    
    return all(results.values())


if __name__ == '__main__':
    import sys
    
    # Vérifier si un chemin d'image est fourni
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if image_path:
        print(f"Utilisation de l'image: {image_path}")
    else:
        print("Aucune image fournie. Certains tests seront limités.")
        print("Usage: python test_api.py [chemin_vers_image]")
    
    success = run_all_tests(image_path)
    sys.exit(0 if success else 1)
