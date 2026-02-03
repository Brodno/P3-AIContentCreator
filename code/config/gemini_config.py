"""
Gemini API Configuration using google-genai SDK
Supports Gemini 3 Flash Preview with Robust Retry Logic
"""
import os
import time
import random
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

# Załaduj .env
load_dotenv()

# Konfiguracja
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY nie znaleziony!")

def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)

def generate_content_with_retry(prompt, config=None, max_retries=10):
    """
    Wrapper na generate_content z agresywnym retry logic.
    """
    client = get_client()
    delay = 2  # Start delay: 2 seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            return client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config
            )
        except errors.ServerError as e:
            if attempt == max_retries:
                raise e
            print(f"⚠️ API Error 503/500 (Attempt {attempt}/{max_retries}). Retrying in {delay}s...")
            time.sleep(delay + random.uniform(0, 1)) # Jitter
            delay *= 1.5 # Exponential backoff
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"⚠️ API Quota Limit (Attempt {attempt}/{max_retries}). Retrying in {delay}s...")
                time.sleep(delay + random.uniform(0, 1))
                delay *= 2
            else:
                raise e

    raise Exception("Max retries exceeded")

def test_connection():
    try:
        response = generate_content_with_retry(
            prompt="Test: odpowiedz tylko 'OK'",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low")
            )
        )
        print(f"✅ Gemini API: Połączenie OK (Model: {GEMINI_MODEL})")
        return True
    except Exception as e:
        print(f"❌ Gemini API: Błąd połączenia - {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
