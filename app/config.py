# config.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY not found in .env file!")

genai.configure(api_key=GEMINI_API_KEY)

# Choose your Gemini model
DEFAULT_MODEL = "gemini-2.0-flash" 
model = genai.GenerativeModel(DEFAULT_MODEL)

# Optional generation settings
DEFAULT_TEMPERATURE = 0.7
MAX_TOKENS = 1024
