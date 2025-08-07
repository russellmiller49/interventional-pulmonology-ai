import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Data Paths
INPUT_ARTICLES_PATH = Path('./data/input_articles')
NEW_DOCS_PATH = Path(os.getenv('NEW_DOCS_PATH', './data/new_docs'))

# Create directories if they don't exist
INPUT_ARTICLES_PATH.mkdir(parents=True, exist_ok=True)
NEW_DOCS_PATH.mkdir(parents=True, exist_ok=True)

# Model Settings
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
LLM_MODEL = 'gpt-4-turbo-preview'
EXTRACTION_MODEL = 'gemini-2.5-pro'

# Application Settings
MAX_SEARCH_RESULTS = 5
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CONFIDENCE_THRESHOLD = 0.5

# ChromaDB Settings
CHROMA_PERSIST_DIR = './data/chroma_db'

# Temp directory for uploads
TEMP_DIR = Path('./temp')
TEMP_DIR.mkdir(exist_ok=True)