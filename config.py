import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'insaafai-dev-secret-key-2026')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'insaafai.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit per request
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}

    # LLM Provider Configuration (GroqCloud GPT-OSS)
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'groq')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'openai/gpt-oss-120b')
    
    # Fallback/Generic LLM keys
    LLM_API_KEY = os.environ.get('GROQ_API_KEY') or os.environ.get('LLM_API_KEY') or os.environ.get('GEMINI_API_KEY', '')
    LLM_MODEL = os.environ.get('GROQ_MODEL') or os.environ.get('LLM_MODEL', 'openai/gpt-oss-120b')

    # Embedding Provider Configuration
    EMBEDDING_PROVIDER = os.environ.get('EMBEDDING_PROVIDER', 'sentence-transformers')

    # RAG Hyperparameters
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '500'))
    CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '50'))
    TOP_K = int(os.environ.get('TOP_K_RETRIEVAL', '4'))
    RRF_K = int(os.environ.get('RRF_K', '60'))
