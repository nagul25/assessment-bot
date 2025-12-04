import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    load_dotenv()

    # Azure Blob Storage Configuration
    BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING", None)
    BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", None)
    BLOB_ACCOUNT_NAME = os.getenv("BLOB_ACCOUNT_NAME", None)
    BLOB_ACCOUNT_KEY = os.getenv("BLOB_ACCOUNT_KEY", None)
    SAS_URL = os.getenv("SAS_URL", None)
    SAS_TOKEN = os.getenv("SAS_TOKEN", None)
    
    # Azure AI Foundry Configuration (for GPT-5 / Assistants API)
    AZURE_AI_FOUNDRY_ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT", None)
    AZURE_AI_FOUNDRY_KEY = os.getenv("AZURE_AI_FOUNDRY_KEY", None)
    AZURE_AI_FOUNDRY_DEPLOYMENT = os.getenv("AZURE_AI_FOUNDRY_DEPLOYMENT", "gpt-5")
    AZURE_AI_FOUNDRY_API_VERSION = os.getenv("AZURE_AI_FOUNDRY_API_VERSION", "2024-05-01-preview")
    
    # Azure Assistant Configuration
    AZURE_ASSISTANT_ID = os.getenv("AZURE_ASSISTANT_ID", None)
    
    # Standard Files Configuration
    STANDARD_FILES_JSON = os.path.join(basedir, "standard_files.json")