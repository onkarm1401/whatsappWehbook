import firebase_admin
from firebase_admin import credentials, firestore

# Path to your Firebase service account key (Ensure the file exists)
cred = credentials.Certificate("serviceAccountKey.json")

# Initialize Firebase App (Prevent re-initialization if already initialized)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Initialize Firestore Client
db = firestore.client()
