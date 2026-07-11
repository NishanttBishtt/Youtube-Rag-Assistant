from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

LLM_MODEL = os.getenv("LLM_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 60))
TOP_K = int(os.getenv("TOP_K", 4))