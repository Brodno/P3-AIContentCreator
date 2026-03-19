"""
Generator - generuje post LinkedIn używając promptu z pliku .txt
"""
from config.gemini_config import generate_content_with_retry
from google.genai import types
from modules.prompt_loader import load_prompt, format_prompt

def generate_post(topic, platform="LinkedIn", format_type="post", context=None, recent_topics=None):
    """
    Generuje post LinkedIn

    Args:
        topic (str): Temat posta
        platform (str): Platforma (LinkedIn)
        format_type (str): Format (post)
        context (dict): Kontekst z context_loader
        recent_topics (list): Ostatnie tematy (z INDEX_POSTOW.md)

    Returns:
        str: Wygenerowany post
    """
    if context is None:
        context = {}

    # ===================================
    # UNIKANIE POWTÓRZEŃ
    # ===================================
    avoid_instruction = ""
    if recent_topics and len(recent_topics) > 0:
        topics_str = ", ".join(recent_topics[:5])  # Max 5 ostatnich

        avoid_instruction = f"""
⛔ UNIKAJ POWTÓRZEŃ (ostatnie posty):
Tematy: {topics_str}

ZASADA:
- Nie używaj tych samych przykładów/historii
- Nie kopiuj tych samych liczb
- Używaj innych zwrotów niż ostatnio
"""

    # ===================================
    # WCZYTAJ PROMPT Z PLIKU
    # ===================================
    prompt_template = load_prompt("generator.txt")

    # ===================================
    # FORMATUJ ZMIENNE
    # ===================================
    prompt = format_prompt(
        prompt_template,
        topic=topic,
        avoid_instruction=avoid_instruction,
        story_brief="" # Fix: adding missing story_brief
    )

    # ===================================
    # WYWOŁAJ API
    # ===================================
    response = generate_content_with_retry(
        prompt=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="high"),
            temperature=1.0  # Wysoka = więcej różnorodności
        )
    )

    return response.text.strip()
