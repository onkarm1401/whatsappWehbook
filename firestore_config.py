from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials, firestore
import json

def get_firebase_credentials():
    """Fetch Firebase credentials from Google Secret Manager"""
    project_id = "chatbot-2300b"
    secret_name = f"projects/{project_id}/secrets/FIREBASE_CREDENTIALS/versions/latest"

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(name=secret_name)
    secret_data = response.payload.data.decode("UTF-8")
    
    return json.loads(secret_data)

def initialize_firebase():
    """Initialize Firebase with retrieved credentials"""
    creds_dict = get_firebase_credentials()
    cred = credentials.Certificate(creds_dict)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

db = initialize_firebase()
