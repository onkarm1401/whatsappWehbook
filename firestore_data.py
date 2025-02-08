# firebase_data.py

import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize Firebase (only once)
try:
    cred = credentials.Certificate("serviceAccountKey.json")  # Update with your correct path
    firebase_admin.initialize_app(cred)
    db = firestore.client()  # Initialize Firestore client
except Exception as e:
    logger.error(f"Error initializing Firebase: {e}")

def get_filtered_firestore_data(message, owner_phone_number):
    """Fetch documents from Firestore based on filters."""
    try:
        # Reference to the collection
        whatsapp_flow_chart_ref = db.collection("whatsapp-flow-chart")

        # Apply filters to the collection query
        query = whatsapp_flow_chart_ref.where("message", "==", message).where("id", "==", owner_phone_number)

        # Get documents matching the filters
        results = query.stream()

        # Collect results
        documents = [doc.to_dict() for doc in results]

        if documents:
            logger.info(f"Fetched documents: {documents}")
            return documents
        else:
            logger.warning("No documents found matching the filters.")
            return None
    except Exception as e:
        logger.error(f"Error fetching data from Firestore: {e}")
        return None
