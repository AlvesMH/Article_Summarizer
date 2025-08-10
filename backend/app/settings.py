from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    SEA_LION_API_KEY: str = os.getenv("SEA_LION_API_KEY", "")
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    SEA_LION_BASE_URL: str = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1/chat/completions")
    DEFAULT_SEALION_MODEL: str = os.getenv("DEFAULT_SEALION_MODEL", "aisingapore/Gemma-SEA-LION-v3-9B-IT")
    HF_EMBED_MODEL: str = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    HF_EMBED_API: str = os.getenv("HF_EMBED_API", f"https://router.huggingface.co/hf-inference/models/{HF_EMBED_MODEL}/pipeline/feature-extraction")
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "/data/chroma_lessons")

settings = Settings()
