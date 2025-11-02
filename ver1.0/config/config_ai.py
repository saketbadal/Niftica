# config/config_ai.py
import os
from dotenv import load_dotenv

load_dotenv()

# Vertex AI Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "asia-south1")
VERTEX_MODEL = os.getenv("VERTEX_MODEL", "gemini-1.5-pro")

# AI Parameters
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.3"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))

# OI Analysis Parameters
OI_CHANGE_THRESHOLD = int(os.getenv("OI_CHANGE_THRESHOLD", "1000"))
PCR_BULLISH_THRESHOLD = float(os.getenv("PCR_BULLISH_THRESHOLD", "0.7"))
PCR_BEARISH_THRESHOLD = float(os.getenv("PCR_BEARISH_THRESHOLD", "1.3"))

# Market Analysis
VIX_HIGH_THRESHOLD = float(os.getenv("VIX_HIGH_THRESHOLD", "25"))
ADX_TREND_THRESHOLD = float(os.getenv("ADX_TREND_THRESHOLD", "20"))