import os
import json
from google.cloud import secretmanager
import firebase_admin
from firebase_admin import credentials, firestore

def get_firebase_credentials():
    """Fetch Firebase credentials from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()

    # Construct the secret name using the project ID
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")  # Automatically set in Cloud Run
    secret_name = f"projects/{project_id}/secrets/FIREBASE_CREDENTIALS/versions/latest"

    # Access the secret value
    response = client.access_secret_version(name=secret_name)
    return json.loads(response.payload.data.decode("utf-8"))

# Get Firebase credentials from Secret Manager
firebase_creds = get_firebase_credentials()

# Initialize Firebase with the fetched credentials
cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

print("Firebase Initialized Successfully from Secret Manager!")