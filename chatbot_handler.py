import time
import logging
from google.cloud import secretmanager
from openai import OpenAI  # ✅ Correct import for v2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_openai_key():
    client = secretmanager.SecretManagerServiceClient()
    project_id = "chatbot-2300b"
    secret_path = f"projects/{project_id}/secrets/openai_key/versions/latest"
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")

def add_message_to_thread(client, thread_id, user_message):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

def run_thread(client, thread_id, assistant_id):
    run_response = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run_response.id

def wait_for_run_completion(client, thread_id, run_id):
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run_status.status in ["completed", "failed", "cancelled"]:
            return run_status
        time.sleep(2)

def get_messages_from_thread(client, thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data

def get_last_assistant_message(messages):
    for message in reversed(messages):
        if message.role == "assistant":
            return message.content[0].text.value if message.content else ""
    return ""

def chatbot_process(user_message, ASSISTANT_ID, thread_id):
    from openai import OpenAI
    client = OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"})
    logger.info("Inside chatbot process method")
    logger.info(f"user message : {user_message}")
    logger.info(f"ASSISTANT_ID : {ASSISTANT_ID}")
    logger.info(f"thread_id : {thread_id}")

    client = OpenAI(api_key=get_openai_key())  # ✅ Correct client creation for v2

    add_message_to_thread(client, thread_id, user_message)
    run_id = run_thread(client, thread_id, ASSISTANT_ID)
    run_status = wait_for_run_completion(client, thread_id, run_id)

    if run_status.status != "completed":
        return "Error: Assistant run failed."

    messages = get_messages_from_thread(client, thread_id)
    return get_last_assistant_message(messages)
