import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
    MCP_HOST = os.getenv("MCP_HOST", "localhost")
    MCP_PORT = int(os.getenv("MCP_PORT", 8001))
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

    MODEL_NAME = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
    TIMEOUT = 30

    DTI_THRESHOLD = 0.5
    CREDIT_SCORE_THRESHOLD = 650
    MIN_INCOME = 20000
    MAX_LOAN_AMOUNT = 500000
