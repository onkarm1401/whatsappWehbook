import openai
import time
import json
from datetime import datetime, timezone, timedelta
from global_vars import *
from google.cloud import secretmanager

def get_openai_key():
    # Initialize Secret Manager Client
    client = secretmanager.SecretManagerServiceClient()

    # Project ID (replace with your actual GCP Project ID)
    project_id = "chatbot-2300b"

    # Secret name based on user_id
    secret_name = "openai_key"

    # Secret path (format: projects/PROJECT_ID/secrets/SECRET_NAME/versions/latest)
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    # Access the secret
    response = client.access_secret_version(name=secret_path)

    # Decode and return the actual key
    return response.payload.data.decode("UTF-8")

def add_message_to_thread(thread_id, user_message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

def run_thread(thread_id, assistant_id):
    run_response = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run_response.id

def wait_for_run_completion(thread_id, run_id):
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run_status.status in ["completed", "failed", "cancelled"]:
            return run_status
        time.sleep(2)

def get_messages_from_thread(thread_id):
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    return messages.data

def get_last_assistant_message(messages):
    for message in reversed(messages):
        if message.role == "assistant":
            return message.content[0].text.value if message.content else ""
    return ""

def chatbot_process(user_message,ASSISTANT_ID,thread_id):
    openai.api_key = get_openai_key()
    logger.info(f" open ai key : {get_ai_key()}")

    # Step 1: Add user message to predefined thread
    add_message_to_thread(thread_id, user_message)

    # Step 2: Start assistant run
    run_id = run_thread(thread_id, ASSISTANT_ID)

    # Step 3: Wait for assistant to complete processing
    run_status = wait_for_run_completion(thread_id, run_id)

    if run_status.status != "completed":
        return "Error: Assistant run failed."

    # Step 4: Retrieve messages and get last assistant response
    messages = get_messages_from_thread(thread_id)
    return get_last_assistant_message(messages)

