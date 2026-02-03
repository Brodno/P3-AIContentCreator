"""
Evaluator - ocenia post według scorecard + logic check
"""
import json
from config.gemini_config import generate_content_with_retry
from google.genai import types
from modules.prompt_loader import load_prompt, format_prompt

def evaluate_post(draft, platform="LinkedIn", context=None, fact_check_results=None):
    """
    Ocenia post przez Content Quality Scorecard + Logic Check

    Args:
        draft (str): Treść posta do oceny
        platform (str): Platforma
        context (dict): Kontekst (opcjonalny)
        fact_check_results (dict): Wyniki fact-checkingu (opcjonalne)

    Returns:
        dict: {
            'breakdown': {'hook': 26, 'eeat': 22, ...},
            'total_score': 88,
            'logic_check': {'passed': True, 'errors': []},
            'format_errors': [...],
            'repetition_check': {...},
            'feedback': "...",
            'strengths': "..."
        }
    """

    # ===================================
    # PRZYGOTUJ FACT-CHECK SECTION
    # ===================================
    fact_check_section = ""
    if fact_check_results and fact_check_results.get('suspicious_claims'):
        fact_check_section = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        fact_check_section += "⚠️ FACT-CHECK RESULTS (z wyszukiwania internetowego):\n\n"
        for claim in fact_check_results['suspicious_claims']:
            fact_check_section += f"❌ TWIERDZENIE: {claim['original_claim']['claim']}\n"
            fact_check_section += f"   VERDICT: {claim['verdict']}\n"
            fact_check_section += f"   REALNE DANE: {claim.get('real_range', 'N/A')}\n"
            fact_check_section += f"   WYJAŚNIENIE: {claim['explanation']}\n"
            if claim.get('correction_hint'):
                fact_check_section += f"   KOREKTA: {claim['correction_hint']}\n"
            fact_check_section += "\n"
        fact_check_section += "UWAGA: Te twierdzenia są NIEREALISTYCZNE według researchu internetowego!\n"
        fact_check_section += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    # ===================================
    # WCZYTAJ PROMPT Z PLIKU
    # ===================================
    prompt_template = load_prompt("evaluator.txt")

    # ===================================
    # FORMATUJ ZMIENNE
    # ===================================
    prompt = format_prompt(
        prompt_template,
        draft=draft,
        fact_check_section=fact_check_section
    )

    # ===================================
    # WYWOŁAJ API (zwróć JSON)
    # ===================================
    response = generate_content_with_retry(
        prompt=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_level="high")
        )
    )

    # ===================================
    # PARSE JSON
    # ===================================
    try:
        result = json.loads(response.text)

        # Policz total_score jeśli nie ma
        if 'total_score' not in result or result['total_score'] == 0:
            result['total_score'] = sum(result.get('breakdown', {}).values())

        return result
    except json.JSONDecodeError:
        return {
            "total_score": 0,
            "breakdown": {"hook": 0, "eeat": 0, "visual": 0, "pain": 0, "cta": 0},
            "logic_check": {"passed": False, "errors": ["Błąd parsowania JSON"]},
            "format_errors": [],
            "repetition_check": {},
            "feedback": "Błąd w ocenie - spróbuj ponownie",
            "strengths": ""
        }
