import os
import json
import base64
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from .env
load_dotenv()

# Read the Base64-encoded Firebase credentials
firebase_creds_base64 = os.getenv("FIREBASE_CREDENTIALS")

if firebase_creds_base64:
    # Decode Base64 to JSON
    firebase_creds_json = json.loads(base64.b64decode(firebase_creds_base64).decode("utf-8"))
    cred = credentials.Certificate(firebase_creds_json)
    firebase_admin.initialize_app(cred)
else:
    raise Exception("Firebase credentials not found. Set FIREBASE_CREDENTIALS environment variable.")

# Initialize Firestore
db = firestore.client()
