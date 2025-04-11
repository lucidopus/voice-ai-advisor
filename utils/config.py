import os


# ======================= GENERAL =======================

ADVISOR_NAME = "Attila AI"
COURSES_DATA_PATH = os.getenv("COURSES_DATA_PATH")
HUMAN_ADVISOR_EMAIL = os.getenv("HUMAN_ADVISOR_EMAIL")

# =======================================================


# ======================== Azure ========================
# Azure OpenAI, embeddings, and email config

AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")
AZURE_API_BASE = os.getenv("AZURE_API_BASE")

AZURE_EMBEDDING_MODEL = os.getenv('AZURE_EMBEDDING_MODEL')
AZURE_EMBEDDING_VERSION = os.getenv('AZURE_EMBEDDING_VERSION')
AZURE_EMBEDDINGS_BASE = os.getenv("AZURE_EMBEDDINGS_BASE")

AZURE_EMAIL_URI = os.getenv("AZURE_EMAIL_URI")
AZURE_EMAIL = os.getenv("AZURE_EMAIL")

# =======================================================


# ====================== PINECONE =======================
# Vector database for semantic search

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION")
PINECONE_HOST = os.getenv("PINECONE_HOST")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# =======================================================


# ======================= TWILIO ========================
# Voice interaction setup

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# =======================================================


# ================= AUDIO STREAM CONFIG =================
# Streaming voice interaction parameters

VOICE = "shimmer"
WEBSOCKET_URI = os.getenv("WEBSOCKET_URI")
PORT = int(os.getenv("PORT", 5050))
LOG_EVENT_TYPES = [
    "error",
    "response.content.done",
    "rate_limits.updated",
    "response.done",
    "input_audio_buffer.committed",
    "input_audio_buffer.speech_stopped",
    "input_audio_buffer.speech_started",
    "session.created",
]
SHOW_TIMING_MATH = False

# =======================================================




# ====================== LANGSMITH ======================
# For prompts

LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
LANGSMITH_ACADEMIC_ADVISOR_PROMPT_IDENTIFIER = os.getenv('LANGSMITH_ACADEMIC_ADVISOR_PROMPT_IDENTIFIER')
LANGSMITH_AI_INITIATION_PROMPT_IDENTIFIER = os.getenv('LANGSMITH_AI_INITIATION_PROMPT_IDENTIFIER')

# =======================================================
