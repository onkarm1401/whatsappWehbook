import openai
import time
import json
import logging
from datetime import datetime, timezone, timedelta
from google.cloud import secretmanager

# ✅ Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_openai_key():
    logger.info("Inside openai key")
    client = secretmanager.SecretManagerServiceClient()

    project_id = "chatbot-2300b"
    logger.info("inside openai function")

    secret_name = "openai_key"
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")

def add_message_to_thread(thread_id, user_message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message,
        headers={"OpenAI-Beta": "assistants=v2"}
    )

def run_thread(thread_id, assistant_id):
    run_response = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        headers={"OpenAI-Beta": "assistants=v2"}
    )
    return run_response.id

def wait_for_run_completion(thread_id, run_id):
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
            headers={"OpenAI-Beta": "assistants=v2"}  # ✅ Missing header added here
        )
        if run_status.status in ["completed", "failed", "cancelled"]:
            return run_status
        time.sleep(2)

def get_messages_from_thread(thread_id):
    messages = openai.beta.threads.messages.list(
        thread_id=thread_id,
        headers={"OpenAI-Beta": "assistants=v2"}  # ✅ Missing header added here
    )
    return messages.data

def get_last_assistant_message(messages):
    for message in reversed(messages):
        if message.role == "assistant":
            return message.content[0].text.value if message.content else ""
    return ""

def chatbot_process(user_message, ASSISTANT_ID, thread_id):
    logger.info("Inside chatbot process method")

    openai.api_key = get_openai_key()
    logger.info(f"openai key : {get_openai_key()}")
    logger.info(f"assistant id : {ASSISTANT_ID}")
    logger.info(f"thread id : {thread_id}")

    openai.default_http_client = None  # Clear stale state

    add_message_to_thread(thread_id, user_message)
    run_id = run_thread(thread_id, ASSISTANT_ID)
    run_status = wait_for_run_completion(thread_id, run_id)

    if run_status.status != "completed":
        return "Error: Assistant run failed."

    messages = get_messages_from_thread(thread_id)
    return get_last_assistant_message(messages)
