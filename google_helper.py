"""
Helper per gestire Google Credentials da environment variable
per deploy su Render/Heroku senza file fisico
"""
import os
import json
import tempfile
from google.oauth2 import service_account

def get_vision_credentials():
    """
    Restituisce le credenziali Google Vision API.
    Priorità:
    1. File JSON se GOOGLE_APPLICATION_CREDENTIALS punta a file esistente
    2. Variabile ambiente GOOGLE_CREDENTIALS_JSON (per deploy cloud)
    """
    
    # Metodo 1: File JSON (sviluppo locale)
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if cred_path and os.path.exists(cred_path):
        return service_account.Credentials.from_service_account_file(cred_path)
    
    # Metodo 2: JSON da variabile ambiente (production)
    cred_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if cred_json:
        # Crea file temporaneo
        cred_dict = json.loads(cred_json)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(cred_dict, f)
            temp_path = f.name
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_path
        return service_account.Credentials.from_service_account_file(temp_path)
    
    raise ValueError("Google credentials non trovate. Imposta GOOGLE_APPLICATION_CREDENTIALS o GOOGLE_CREDENTIALS_JSON")

# Uso in app.py:
# from google_helper import get_vision_credentials
# vision_client = vision.ImageAnnotatorClient(credentials=get_vision_credentials())
